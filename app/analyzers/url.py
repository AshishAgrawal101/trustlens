import ipaddress
import re
import unicodedata
from urllib.parse import urlsplit
import idna
from app.models import AnalysisReport, Evidence


def parse_address(value: str):
    """Validate a literal web address; never resolve or visit it."""
    if any(unicodedata.category(c) in ('Cc','Cf','Cs') for c in value):
        raise ValueError('Enter an address without hidden control or formatting characters.')
    value = value.strip()
    if not value or re.search(r'[\s\\\x00-\x1f\x7f]', value):
        raise ValueError('Enter one web address without spaces or backslashes.')
    if re.match(r'https?:', value, re.I) and not re.match(r'https?://[^/\\?#\s]', value, re.I):
        raise ValueError('Enter a complete HTTP(S) address with // followed by its host.')
    if (re.match(r'^[a-z][a-z0-9+.-]*:', value, re.I) and '://' not in value
            and not re.match(r'^[^/?#]+:[0-9]+(?:[/?#]|$)', value)):
        raise ValueError('Enter a complete HTTP(S) address or a bare hostname with a decimal port; other scheme syntax is not supported.')
    try:
        parsed = urlsplit(value if '://' in value else 'https://'+value)
    except ValueError as exc:
        raise ValueError('This address could not be parsed. Check its brackets and domain.') from exc
    if parsed.scheme.lower() not in ('http','https') or not parsed.hostname:
        raise ValueError('Only http and https web addresses are supported.')
    host = parsed.hostname.removesuffix('.')
    if '%' in host:
        raise ValueError('Enter an address without escaped or scoped host syntax; use a plain domain or canonical IP address.')
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError('This address has an invalid domain or port.') from exc
    try:
        host = str(ipaddress.ip_address(host))
    except ValueError:
        # Normalize original host text: lowercasing first can change Greek final sigma.
        original = parsed.netloc.rsplit('@',1)[-1].split(':',1)[0]
        try:
            mapped = idna.uts46_remap(original,std3_rules=True,transitional=False)
            labels=[]
            for label in mapped.split('.'):
                # Ordinary ASCII DNS labels keep the existing validation below.
                if label and (not label.isascii() or label.startswith('xn--')):
                    label=idna.alabel(label).decode('ascii')
                labels.append(label)
            host='.'.join(labels).removesuffix('.')
        except idna.IDNAError as exc:
            raise ValueError('This address has an invalid domain or port.') from exc
        try:
            return parsed, str(ipaddress.ip_address(host))
        except ValueError:
            pass
        # WHATWG special hosts ending in a number are IPv4 candidates, not DNS
        # names. Reject noncanonical/radix spellings rather than assert a false
        # destination. Canonical IPv4 was accepted above, after UTS46 mapping.
        last = host.rsplit('.', 1)[-1]
        if re.fullmatch(r'[0-9]+|0[xX][0-9a-fA-F]*', last):
            raise ValueError('Enter a canonical dotted IPv4 address or an unambiguous domain name; numeric host shorthand is not supported.')
        if (len(host)>253 or re.fullmatch(r'[0-9.]+',host)
                or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label)
                       for label in host.split('.'))):
            raise ValueError('This address has an invalid domain. Check each part between the dots.')
    return parsed, host


def analyze_url(value: str, claimed_brand: str | None = None, known_website: str | None = None) -> AnalysisReport:
    parsed, host = parse_address(value)
    evidence = [Evidence(id='url:host', evidence_class='verified', severity='info',
        title='The address points to this host', detail=host, source='Parsed address, not a live reputation check')]
    if known_website is not None:
        try:
            reference, expected = parse_address(known_website)
            if reference.username is not None or reference.password is not None:
                raise ValueError()
        except ValueError as exc:
            raise ValueError('Enter a known HTTP(S) website without login details or text before @.') from exc
        evidence.append(Evidence(id='url:comparison', evidence_class='verified', severity='info',
            title='Exact hostname matches your reference' if host == expected else 'Hostname differs from your reference',
            detail=f'Checked host: {host}. Reference host: {expected}. Exact spelling comparison only; sender and safety remain unverified. Legitimate subdomains can differ.',
            source='Local comparison with a user-supplied reference; ownership not verified'))
    def flag(key,title,detail,severity='medium'):
        evidence.append(Evidence(id='url:'+key,evidence_class='inferred',severity=severity,
            title=title,detail=detail,source='Local address rules',weight=.7 if severity=='high' else .3))
    if parsed.username is not None or parsed.password is not None:
        flag('userinfo','Text before @ can hide the destination','The destination is the parsed host in this report, not the text before @.','high')
    if parsed.scheme=='http': flag('http','Connection is not HTTPS','This address does not request an encrypted HTTPS connection.')
    if 'xn--' in host: flag('idn','Internationalized domain','This can be legitimate. Check for lookalike characters against a known address.')
    if host.count('.')>=4: flag('subdomains','Long chain of subdomains','Brand names on the left do not establish who controls the destination.')
    try:
        ipaddress.ip_address(host)
        flag('ip','Numeric address instead of a domain','A numeric host makes the organization harder to identify.')
    except ValueError: pass
    if host in ('bit.ly','tinyurl.com','t.co','shorturl.at'):
        flag('short','The final destination is hidden','This checker does not expand redirects or visit the link.')
    if claimed_brand:
        evidence.append(Evidence(id='url:brand', evidence_class='unknown', severity='info',
            title='Organization ownership is unverified', detail='A name in an address is not proof of ownership.', source='User-supplied organization name'))
    concerns = any(e.weight>0 for e in evidence)
    serious = any(e.severity=='high' and e.weight>0 for e in evidence)
    return AnalysisReport(kind='url',risk_index=None,risk_level='high' if serious else 'guarded' if concerns else 'low',confidence='low',
        summary='Check the destination through a source you already trust.',evidence=evidence,
        model_ran=False, decision_basis='rules',
        limitations=['No page, redirect, domain registry or reputation service was contacted.',
                     'HTTPS protects the connection; it does not prove that a site or offer is legitimate.'])
