from email import policy
from email.parser import BytesParser, Parser
from email.utils import parseaddr
from email.header import decode_header
from email.headerregistry import Address
from email.errors import HeaderParseError
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import re
import unicodedata
from app.models import Evidence
from app.analyzers.text import analyze_text, communication_report
from app.analyzers.url import parse_address, analyze_url

MAX_EMAIL_BYTES = 250000
_BLOCK_TAGS = {'address', 'article', 'aside', 'blockquote', 'body', 'dd', 'div', 'dl', 'dt', 'fieldset',
               'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header',
               'hr', 'li', 'main', 'nav', 'ol', 'p', 'pre', 'section', 'table', 'td', 'th', 'tr', 'ul'}


def unsupported_href_characters(raw):
    return any(unicodedata.category(c) in ('Cc','Cf','Cs') or (c.isspace() and c!=' ') for c in raw)


def href_target(raw):
    """Classify a supplied target without resolving it or claiming transport."""
    if unsupported_href_characters(raw):
        return 'unsupported', None
    value=raw.strip(' ')
    if not value or value.startswith('#'):
        return 'none', None
    try:
        if value.startswith('//'):
            if not re.match(r'//[^/\\?#\s]',value): raise ValueError()
            # Parser adapter only: never emit this invented scheme or feed it
            # into body URL rules which could imply an HTTPS connection.
            return 'relative_host', parse_address('https:'+value)[1]
        if value.lower().startswith(('http://','https://')):
            return 'web', parse_address(value)[1]
        if value.lower().startswith('mailto:'):
            address=Address(addr_spec=unquote(urlsplit(value).path,errors='strict'))
            if not address.username or not address.domain: raise ValueError()
            return 'mailto', parse_address(address.domain)[1]
    except (ValueError,HeaderParseError,IndexError,AttributeError):
        pass
    return 'unsupported', None


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.hidden=0; self.links=[]; self.anchors=[]; self.anchor=None; self.uninspected_targets=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.hidden+=1
        if not self.hidden and (tag in _BLOCK_TAGS or tag == 'br'):
            self.parts.append('\n')
            if self.anchor: self.anchor[1].append('\n')
        if tag=='a' and not self.hidden:
            self.finish_anchor()
            href=next((v for k,v in attrs if k=='href' and v is not None), '')
            kind,_=href_target(href)
            if kind=='unsupported': self.uninspected_targets+=1
            if (kind=='unsupported' and href.strip(' ').lower().startswith(('http://','https://'))
                    and not unsupported_href_characters(href)):
                # Preserve the prior unknown malformed-web-link observation,
                # without sanitizing hidden characters into a trusted address.
                self.links.append(href.strip(' '))
            if kind in ('web','mailto','relative_host'):
                if kind=='web': self.links.append(href.strip(' '))
                self.anchor=(href, [])
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.hidden=max(0,self.hidden-1)
        if not self.hidden and tag in _BLOCK_TAGS:
            self.parts.append('\n')
            if self.anchor: self.anchor[1].append('\n')
        if tag=='a': self.finish_anchor()
    def handle_data(self,data):
        if not self.hidden:
            self.parts.append(data)
            if self.anchor: self.anchor[1].append(data)

    def finish_anchor(self):
        if self.anchor:
            self.anchors.append((self.anchor[0], ''.join(self.anchor[1]).strip()))
            self.anchor=None


def link_label_evidence(anchors):
    # shortcut: compare literal hosts/primary mailbox domains; CSS, redirects and extra mailto recipients need separate handling.
    evidence=[]
    seen=set()
    for href, label in anchors:
        kind,destination=href_target(href)
        if kind not in ('web','mailto','relative_host'): continue
        mailto=kind=='mailto'
        try:
            if mailto:
                address=Address(addr_spec=label)
                if not address.username or not address.domain: continue
                shown=parse_address(address.domain)[1]
            else:
                if not (label.lower().startswith(('http://','https://')) or re.fullmatch(r'[^\s/]+\.[^\s/]+(?:/[^\s]*)?', label)): continue
                _, shown=parse_address(label)
        except (ValueError,HeaderParseError,IndexError,AttributeError):
            continue
        if shown==destination or (shown,destination) in seen:
            continue
        seen.add((shown,destination))
        evidence.append(Evidence(id=f'email:link_mismatch:{len(evidence)}',evidence_class='verified',severity='medium',
            title='The displayed address and link destination differ',
            detail=(f'Displayed mailbox domain: {shown}. Primary recipient domain: {destination}. Different addresses can be legitimate; verify through a known contact before sending.' if mailto else
                    f'Displayed host: {shown}. Link host: {destination}. Legitimate tracking can also cause this; verify through a known address.'),
            source='Compared text and href in supplied HTML; neither destination was visited',weight=.3))
        if len(evidence)==8: break
    return evidence



def relative_target_evidence(anchors):
    # Reuse only explicitly scheme-independent rules. The adapter scheme is
    # never emitted, and future transport rules require a separate review.
    allowed={'url:host','url:userinfo','url:idn','url:subdomains','url:ip','url:short'}
    targets=list(dict.fromkeys(href.strip(' ') for href,_ in anchors if href_target(href)[0]=='relative_host'))
    evidence=[]
    for index,target in enumerate(targets[:8]):
        for item in analyze_url('https:'+target).evidence:
            if item.id not in allowed: continue
            updates={'id':('email:relative_host:' if item.id=='url:host' else item.id+':relative:')+str(index),
                     'source':'Local scheme-independent address rules for supplied scheme-relative HTML target; transport and ownership remain unknown'}
            if item.id=='url:host': updates['title']='The scheme-relative link points to this host'
            evidence.append(item.model_copy(update=updates))
    return evidence,max(0,len(targets)-8)


def body_parts(message, checked_parts=None):
    if message.get_content_disposition() == 'attachment':
        return
    if message.get_content_maintype() == 'multipart':
        if checked_parts is not None and message not in checked_parts: checked_parts.append(message)
        for part in message.iter_parts():
            yield from body_parts(part, checked_parts)
    elif message.get_content_type() in ('text/plain', 'text/html'):
        if checked_parts is not None and message not in checked_parts: checked_parts.append(message)
        yield message


def unscanned_parts_count(message):
    count=0
    pending=[message]
    while pending:
        part=pending.pop()
        if part.get_content_disposition()=='attachment':
            count+=1
        elif part.get_content_maintype()=='multipart':
            pending.extend(part.iter_parts())
        elif part.get_content_type() not in ('text/plain','text/html'):
            count+=1
    return count


def analyze_email(raw_email: str):
    try:
        message=Parser(policy=policy.default).parsestr(raw_email)
        decoded_body=None
        if not message.keys() and not message.is_multipart() and message.get_content_type()=='text/plain':
            # A header-free textarea paste is already decoded text, not wire
            # bytes for get_content() to reconstruct using a default charset.
            payload=message.get_payload(decode=False)
            if isinstance(payload,str):
                if any(0xD800 <= ord(char) <= 0xDFFF for char in payload):
                    raise ValueError('This pasted message contains unsupported Unicode surrogate characters. Paste readable text instead.')
                decoded_body=payload
        return analyze_message(message,_decoded_body=decoded_body)
    except (RecursionError, HeaderParseError, IndexError, AttributeError) as exc:
        raise ValueError('This email structure could not be read. Paste only the visible message body instead.') from exc


def analyze_email_bytes(content: bytes):
    if not content or not content.strip():
        raise ValueError('Choose a non-empty .eml message.')
    if len(content)>MAX_EMAIL_BYTES:
        raise ValueError('Choose an .eml message of at most 250,000 bytes. Attachments count toward this limit and are not scanned.')
    if b'\x00' in content:
        raise ValueError('This .eml contains unsupported binary content. Paste only the visible message body instead.')
    try:
        return analyze_message(BytesParser(policy=policy.default).parsebytes(content))
    except (RecursionError, HeaderParseError, IndexError, AttributeError) as exc:
        raise ValueError('This email structure could not be read. Paste the message text instead.') from exc


def analyze_message(message, _decoded_body=None):
    bodies=[]; anchors=[]; incomplete=[]; checked_parts=[message]; uninspected_targets=0
    for name in ('From','Reply-To'):
        if len(message.get_all(name,[]))>1:
            incomplete.append(f'Multiple {name} headers were supplied; no single address can be assumed.')
    for part in body_parts(message, checked_parts):
        if part is message and _decoded_body is not None:
            content=_decoded_body
        else:
            try:
                try: content=part.get_content(errors='strict')
                except UnicodeError:
                    incomplete.append('A message body contains bytes invalid for its declared encoding; readable content is shown only as a partial check.')
                    content=part.get_content()
            except (LookupError,UnicodeError,ValueError):
                incomplete.append('A message body could not be decoded with its declared encoding.')
                continue
        if not isinstance(content,str): continue
        if part.get_content_type()=='text/html':
            parser=VisibleText(); parser.feed(content); parser.close(); parser.finish_anchor()
            content=''.join(parser.parts)+'\n'+'\n'.join(parser.links)
            anchors.extend(parser.anchors)
            uninspected_targets+=parser.uninspected_targets
        bodies.append(content)
    for name, value in message.raw_items():
        if name.lower() != 'subject': continue
        try:
            for text, encoding in decode_header(value):
                if isinstance(text, bytes): text.decode(encoding or 'ascii', errors='strict')
                elif any(0xD800 <= ord(char) <= 0xDFFF for char in text): raise UnicodeError('Undecodable subject')
        except (LookupError, UnicodeError, ValueError, HeaderParseError):
            incomplete.append('A supplied subject could not be decoded reliably; readable body content is only a partial check.')
    subjects=message.get_all('Subject',[])
    if len(subjects)>1:
        incomplete.append('Multiple Subject headers were supplied; no single displayed subject can be assumed. All supplied subjects were checked as text.')
    subject='\n'.join(str(value) for value in subjects)
    report=analyze_text(subject+'\n'+'\n'.join(bodies))
    relative_evidence,relative_uninspected=relative_target_evidence(anchors)
    evidence=report.evidence+link_label_evidence(anchors)+relative_evidence
    uninspected_targets+=relative_uninspected
    if uninspected_targets:
        evidence.append(Evidence(id='email:links_incomplete',evidence_class='unknown',severity='info',weight=0,
            title='Some email link targets were not inspected',
            detail=f'{uninspected_targets} visible HTML link target(s) were not inspected because their address syntax or scheme is unsupported, or a bounded review limit was reached. No target was visited.',
            source='Count of uninspected targets in supplied HTML; no addresses or query values included'))
    unscanned=unscanned_parts_count(message)
    if unscanned:
        evidence.append(Evidence(id='email:unscanned',evidence_class='unknown',severity='info',
            title='Some email parts were not checked',
            detail=f'{unscanned} attachment or unsupported MIME part(s) were not scanned. Only readable subject and message-body content was checked; this does not establish attachment safety.',
            source='Local MIME part headers only; attached-message subtrees skipped; no filenames or attachment contents inspected'))
    if not any(body.strip() for body in bodies):
        incomplete.append('No readable message body was available. The subject, if present, does not establish the content or safety of the missing or unreadable body.')
    for part in checked_parts:
        for name in ('Content-Type', 'Content-Transfer-Encoding'):
            if len(part.get_all(name, [])) > 1:
                incomplete.append(f'Multiple {name} headers were supplied in a checked MIME part; its interpretation is ambiguous.')
    # Plain body-only pastes need no headers; MIME/header/decoding defects still limit a check.
    defects=[d for part in checked_parts for d in part.defects
             if type(d).__name__!='MissingHeaderBodySeparatorDefect' or message.keys()]
    header_defects=any(getattr(value,'defects',()) for name in ('From','Reply-To','Content-Type') for value in message.get_all(name,[]))
    if defects or header_defects:
        incomplete.append('Malformed headers or message encoding prevented a reliable full interpretation.')
    if incomplete:
        evidence.append(Evidence(id='email:incomplete',evidence_class='unknown',severity='medium',
            title='This email check is incomplete',detail=' '.join(dict.fromkeys(incomplete)),
            source='Local MIME/header validation; unreadable or ambiguous content is not evidence of safety'))
    sender=parseaddr(str(message.get('From','')))[1].lower() if len(message.get_all('From',[]))==1 else ''
    reply=parseaddr(str(message.get('Reply-To','')))[1].lower() if len(message.get_all('Reply-To',[]))==1 else ''
    if sender:
        evidence.append(Evidence(id='email:sender',evidence_class='unknown',severity='info',
            title='Claimed sender',detail=sender,source='Pasted From header; identity unverified'))
    if sender and reply and sender.rsplit('@',1)[-1]!=reply.rsplit('@',1)[-1]:
        evidence.append(Evidence(id='email:reply',evidence_class='inferred',severity='medium',
            title='Replies go to a different domain',detail='This can be legitimate, but verify before replying.',source='Pasted headers',weight=.4))
    if message.get('Authentication-Results'):
        evidence.append(Evidence(id='email:auth',evidence_class='unknown',severity='info',
            title='Authentication is reported, not independently verified',
            detail='Copied SPF, DKIM and DMARC headers can be forged. This app cannot authenticate the sending server from pasted text.',
            source='Untrusted pasted Authentication-Results header'))
    result=communication_report('email',evidence,[
        'Pasted headers are supplied text, not a trusted mail-server connection.',
        'Attachments are not scanned; message links are inspected as text without fetching them.',
        'Link-label comparisons require HTML. Pasted plain text or screenshots can omit the actual link destination. CSS layout and redirects are not inspected.',
        'Mailto comparisons cover one literal primary recipient domain, not mailbox ownership, same-domain aliases, or additional query recipients.',
        'For the first 8 unique scheme-relative // targets, host and scheme-independent address rules are checked; transport remains unknown. Duplicate matching targets are counted once after surrounding ASCII spaces are removed. Remaining targets are not inspected by these rules. Literal hostname-label comparisons are separate; relative paths and unsupported targets are not resolved. Empty and fragment-only anchors are not external target checks.',
        'A passed mail-authentication check would not establish that a request is safe.'])
    if unscanned:
        result.summary='Only readable subject and message-body content was checked; other parts were not scanned. '+result.summary
    if incomplete:
        result.summary='This email could not be fully interpreted. Review the original message through a trusted mail app. Any readable warning signs are shown below.'
        if result.risk_level=='low': result.risk_level='guarded'
    return result
