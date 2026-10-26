"""Inspectable English-language request patterns, not a trained scam classifier."""
import re
from app.models import AnalysisReport, Evidence
from app.analyzers.url import analyze_url

# Match Python splitlines boundaries without rewriting source text or offsets.
_HARD_LINE_BREAKS = r"\n\r\v\f\x1c-\x1e\x85\u2028\u2029"
_HORIZONTAL_SPACE = r"[^\S" + _HARD_LINE_BREAKS + r"]"
_PROHIBITION = r"(?:do|should|must)" + _HORIZONTAL_SPACE + r"+not"

RULES = [
    ('code', 'Request to share a security code',
     r'\b(?:send|share|read|tell|give|reply|forward|provide)\b.{0,85}?\b(?:(?:verification|security|login|one(?:[-\u2010\u2011]|' + _HORIZONTAL_SPACE + r'+)time|six(?:[-\u2010\u2011]|' + _HORIZONTAL_SPACE + r'+)digit|6(?:[-\u2010\u2011]|' + _HORIZONTAL_SPACE + r'+)digit|authentication|2fa)\s+codes?|passcodes?|otp|passwords?|pin'
     r'|the\s+code\s+we\s+just\s+sent\b[^,;]{0,85}?\b(?:security|account|login|sign[- ]in|authentication))\b', 'high'),
    ('payment', 'Payment request to verify',
     r'\b(?:(?:buy|pay|send|move|transfer|purchase|deposit)\b.{0,90}?\b(?:gift\s*cards?|crypto|bitcoin|wire|(?:safe|secure) account|release fee|processing fee)\b'
     r'|(?:send|move|transfer|wire)\s+(?:(?:me|us|them|him|her)\s+)?(?:[$£€]\s*\d[\d,]*|\d[\d,]*\s+dollars?\b)'
     r'|wire\b[^,;]{0,65}?\b(?:payment|funds|money)\b)', 'high'),
    ('balance', 'Request to settle a balance', r'\bsettle\s+(?:your|the)\s+(?:outstanding\s+)?balance\b', 'medium'),
    ('overpayment', 'Request to return an excess payment', r'\b(?:send|transfer|wire|refund|return)\b.{0,65}?\b(?:difference|extra money|overpayment|excess payment)\b', 'high'),
    ('advance_fee', 'Upfront fee to receive money', r'\b(?:pay|send|transfer)\b.{0,70}?\b(?:fee|deposit)\b.{0,65}?\b(?:unlock|release|receive|claim)\b.{0,45}?\b(?:prize|grant|loan|winnings|funds)\b', 'high'),
    ('personal', 'Request for sensitive personal details', r'\b(?:send|share|provide|give|reply|tell)\b.{0,70}?\b' + r'(?:social security number|ssn|bank account number|card number)'.replace(' ', _HORIZONTAL_SPACE + '+') + r'\b', 'high'),
    ('remote', 'Request for remote access', r'\b(?:install|download|open|enable)\b.{0,65}?\b(?:anydesk|teamviewer|remote access|remote desktop|screen[- ]sharing)\b', 'high'),
    ('threat', 'Threat used to pressure a decision', r'\b(?:arrest|legal action|account.{0,25}(?:closed|suspended)|disconnect.{0,25}(?:power|electricity))\b', 'medium'),
    ('secrecy', 'Request to keep this secret', r"\b(?:" + _PROHIBITION + r"|don[\x27’]t|never)" + _HORIZONTAL_SPACE + r"+(?:tell|contact|call)\b.{0,60}\b(?:anyone|family|bank|police|parents)\b|\bkeep (?:this|it) (?:a )?secret\b", 'high'),
    ('urgency', 'Pressure to act quickly', r'\b(?:act now|immediately|urgent|within \d+ minutes|last chance)\b', 'medium'),
    ('prize', 'Unexpected reward or guaranteed return', r'\b(?:you(?:.ve| have)? won|claim your prize|guaranteed.{0,30}(?:profit|return))\b', 'medium'),
]


def _negative_clause_before(text: str, position: int) -> bool:
    # shortcut: bounded and/or and ask-person-to clauses only; other grammar stays unresolved.
    prefix = text[max(0, position-240):position]
    negatives = list(re.finditer(r"\b(?:" + _PROHIBITION + r"|don[\x27’]t|never|avoid)" + _HORIZONTAL_SPACE + r"+", prefix, re.I))
    if not negatives:
        return False
    clause = prefix[negatives[-1].end():]
    if not re.match(r'^(?:ask|visit|buy|pay|send|move|transfer|purchase|deposit|settle|return|wire|share|read|tell|give|reply|forward|provide|install|download|open|enable|refund)\b', clause, re.I):
        return False
    if not (re.search(r'\b(?:and|or)\s*$', clause, re.I)
            or re.fullmatch(r'ask\b.{1,80}?\bto\s*', clause, re.I)):
        return False
    for boundary in re.finditer(r"[.!?" + _HARD_LINE_BREAKS + r";\x27\"“”‘’]|\b(?:but|however)\b", clause, re.I):
        dot = boundary.start()
        if boundary.group() == '.':
            if (dot > 0 and dot+1 < len(clause)
                    and clause[dot-1].isalnum() and clause[dot+1].isalnum()):
                continue
            if re.search(r'\b(?:Mr|Mrs|Ms|Dr|Prof)$', clause[:dot], re.I):
                continue
        return False
    return True


def _wording_view(text: str) -> tuple[str, list[int] | None]:
    """Ignore only intra-letter soft hyphens; retain a source index per kept character."""
    if '\u00ad' not in text:
        return text, None
    indices = [index for index, char in enumerate(text)
               if not (char == '\u00ad' and 0 < index < len(text)-1
                       and text[index-1].isalpha() and text[index+1].isalpha())]
    return ''.join(text[index] for index in indices), indices


def _source_excerpt(original: str, indices: list[int] | None, start: int, end: int) -> str:
    if start >= end:
        return ''
    if indices is None:
        return original[start:end].strip()
    return original[indices[start]:indices[end-1]+1].strip()


def _credential_privacy_advice(sentence: str, match) -> bool:
    # Only direct tell-anyone prohibitions with an adjacent credential object qualify.
    head = r"(?:" + _PROHIBITION + r"|don[\x27’]t|never)" + _HORIZONTAL_SPACE + r"+tell" + _HORIZONTAL_SPACE + r"+anyone"
    if not re.fullmatch(head, match.group(), re.I):
        return False
    credential = r"(?:passwords?|passcodes?|pins?|otp|(?:verification|security|login|authentication)" + _HORIZONTAL_SPACE + r"+codes?)"
    tail = _HORIZONTAL_SPACE + r"+(?:(?:your|my|the|a)" + _HORIZONTAL_SPACE + r"+)?" + credential + _HORIZONTAL_SPACE + r"*$"
    return re.match(tail, sentence[match.end():], re.I) is not None


def request_evidence(text: str) -> list[Evidence]:
    original = text
    text, source_indices = _wording_view(text)
    found = {}
    # shortcut: only explicit completed teaching frames qualify; ambiguous quotations retain warnings.
    history = list(re.finditer(
        r'\b(?:(?:at|in)\s+(?:last week[\x27’]s|yesterday[\x27’]s)\s+(?:safety class|training role-play),?\s+'
        r'(?:the instructor displayed (?:the|an) example|the actor said)'
        r'|(?:for (?:the|our) workshop handout )?we used (?:the|an) invented (?:line|example)'
        r'|(?:our|the) completed (?:poster|handout) includes (?:the|a) fake example)\s*,?\s*'
        r'(?P<quote>"[^"\n]{1,1000}"|\x27[^\x27\n]{1,1000}\x27|“[^”\n]{1,1000}”|‘[^’\n]{1,1000}’)',
        text, re.I))
    sentences = list(re.finditer(r'[^' + _HARD_LINE_BREAKS + r'.!?]+', text))
    # shortcut: finite adjacent delivery/disclosure templates only; unfamiliar references remain unmatched.
    for previous, current in zip(sentences, sentences[1:]):
        antecedent = previous.group().strip(' \t')
        request = current.group().strip(' \t')
        current_start = current.start() + len(current.group()) - len(current.group().lstrip(' \t'))
        if (len(antecedent) > 160 or len(request) > 160
                or not re.fullmatch(r'\.[ \t]+', text[previous.end():current_start])
                or any(item.start('quote') < current.end() and previous.start() < item.end('quote') for item in history)):
            continue
        if (re.fullmatch(r'(?:A (?:login|verification|security) code should arrive by text(?: in a moment)?'
                         r'|Your (?:banking app|app) has (?:just )?sent (?:a login code|a verification code|a security code|a one-time passcode))', antecedent, re.I)
                and re.fullmatch(r'(?:Tell me those six numbers(?: when you see them)?(?: so I can complete the sign-in)?'
                                 r'|Reply here with those characters(?: so I can cancel the attempted login)?)', request, re.I)):
            found['reference:code'] = Evidence(id='reference:code', evidence_class='unknown', severity='info', weight=0,
                title='Possible security-code reference',
                detail='A security-code delivery statement is followed by a request for numbers or characters. Whether they refer to the same thing, and whether this is a current request, are unknown. Keep security codes private and verify through a separate route.',
                source='Local adjacent code-reference rules')
            break
    # shortcut: sentence-level English rules miss context and other languages; expand only with labeled evaluations.
    for sentence_match in sentences:
        sentence = sentence_match.group()
        # shortcut: only explicit if-asked/stop clauses are recognized; expand with paired context cases.
        advice = re.match(r'\s*if\s+(?:someone|anyone|a caller|an unexpected caller|the caller)\s+asks\s+you\s+to\b(?P<request>[^,;]{1,180})[,;]\s*(?:hang up|stop|end the call)(?=\s*(?:[,;]|$))', sentence, re.I)
        passive_refusal = re.match(r'\s*if' + _HORIZONTAL_SPACE + r'+you' + _HORIZONTAL_SPACE + r'+are' + _HORIZONTAL_SPACE + r'+asked' + _HORIZONTAL_SPACE + r'+to(?=' + _HORIZONTAL_SPACE + r')(?P<request>[^,;]{1,180}),' + _HORIZONTAL_SPACE + r'*refuse(?=' + _HORIZONTAL_SPACE + r'*(?:[,;]|$))', sentence, re.I)
        for key, title, pattern, severity in RULES:
            negated_end = None
            for match in re.finditer(pattern, sentence, re.I):
                if key in found:
                    break
                prefix = sentence[max(0, match.start()-45):match.start()]
                if (key == 'urgency' and match.group().lower() == 'urgent'
                        and re.fullmatch(_HORIZONTAL_SPACE + r'*this' + _HORIZONTAL_SPACE + r'+is' + _HORIZONTAL_SPACE + r'+not' + _HORIZONTAL_SPACE + r'+', sentence[:match.start()], re.I)
                        and re.match(_HORIZONTAL_SPACE + r'*(?:[,;]|$)', sentence[match.end():])):
                    if '?' not in re.match(r'[.!?]*', text[sentence_match.end():]).group():
                        found['context:negative_urgency'] = Evidence(id='context:negative_urgency', evidence_class='unknown', severity='info',
                            title='Explicit wording: not urgent',
                            detail='This complete clause explicitly says it is not urgent: “'+_source_excerpt(original, source_indices, sentence_match.start(), sentence_match.start()+match.end())+'”. That wording does not verify the sender or establish safety.',
                            source='Local wording and context rules')
                        continue
                if key == 'secrecy' and _credential_privacy_advice(sentence, match):
                    continue
                if (key in ('code', 'payment', 'balance', 'overpayment', 'advance_fee', 'personal', 'remote')
                        and re.search(r'\bremember' + _HORIZONTAL_SPACE + r'+not' + _HORIZONTAL_SPACE + r'+to' + _HORIZONTAL_SPACE + r'+$', prefix, re.I)):
                    negated_end = match.end()
                    continue
                if (key in ('code', 'payment', 'balance', 'overpayment', 'advance_fee', 'personal', 'remote')
                        and re.search(r"\bI" + _HORIZONTAL_SPACE + r"+(?:will" + _HORIZONTAL_SPACE + r"+not|won[\x27’]t)" + _HORIZONTAL_SPACE + r"+(?:ever" + _HORIZONTAL_SPACE + r"+)?$", prefix, re.I)):
                    negated_end = match.end()
                    continue
                if (key in ('code', 'payment', 'balance', 'overpayment', 'advance_fee', 'personal', 'remote')
                        and _negative_clause_before(text, sentence_match.start() + match.start())):
                    negated_end = match.end()
                    continue
                if key != 'secrecy' and (re.search(r"(?:" + _PROHIBITION + r"|don.t|never|avoid|(?:never|won.t|will" + _HORIZONTAL_SPACE + r"+not|do" + _HORIZONTAL_SPACE + r"+not|don.t)\s+(?:ever\s+)?ask you to)\s+(?:ever\s+)?$", prefix, re.I)
                        or (negated_end is not None and re.fullmatch(r'\s*(?:or|and)\s*', sentence[negated_end:match.start()], re.I))):
                    negated_end = match.end()
                    continue
                if any(item.start('quote') < sentence_match.start() + match.start()
                       and sentence_match.start() + match.end() < item.end('quote') for item in history):
                    found['context:'+key] = Evidence(id='context:'+key, evidence_class='unknown', severity='info',
                        title='Historical teaching quotation',
                        detail='The matched wording is inside a quoted example described as completed teaching material. Whether a current request exists is unknown.',
                        source='Local wording and context rules')
                    continue
                if (advice and key in ('code', 'payment', 'balance', 'overpayment', 'advance_fee', 'personal', 'remote')
                        and advice.start('request') <= match.start() and match.end() <= advice.end('request')):
                    found['context:'+key] = Evidence(id='context:'+key, evidence_class='unknown', severity='info',
                        title='Conditional safety advice',
                        detail='This wording gives advice to stop or hang up: “'+_source_excerpt(original, source_indices, sentence_match.start()+advice.start(), sentence_match.start()+advice.end())+'”. Whether a current request exists is unknown.',
                        source='Local wording and context rules')
                    continue
                if (passive_refusal and key in ('code', 'payment', 'balance', 'overpayment', 'advance_fee', 'personal', 'remote')
                        and passive_refusal.start('request') <= match.start() and match.end() <= passive_refusal.end('request')):
                    found['context:passive_refusal:'+key] = Evidence(id='context:passive_refusal:'+key, evidence_class='unknown', severity='info',
                        title='Conditional refusal advice',
                        detail='This wording advises refusing a conditional request: “'+_source_excerpt(original, source_indices, sentence_match.start()+passive_refusal.start(), sentence_match.start()+passive_refusal.end())+'”. Whether a current request exists is unknown.',
                        source='Local wording and context rules')
                    continue
                excerpt = _source_excerpt(original, source_indices,
                    sentence_match.start()+max(0, match.start()-30),
                    sentence_match.start()+min(len(sentence), match.end()+55))
                found[key] = Evidence(id='request:'+key, evidence_class='inferred', severity=severity,
                    title=title, detail='Matched wording: “'+excerpt+'”. Context may change its meaning.',
                    source='Local request-pattern rules', weight=.8 if severity=='high' else .35)
    return list(found.values())


def communication_report(kind: str, evidence: list[Evidence], limitations=None) -> AnalysisReport:
    concerns = [e for e in evidence if e.weight > 0]
    serious = any(e.severity == 'high' for e in concerns)
    level = 'high' if serious else 'guarded' if concerns else 'low'
    summary = ('Pause before responding. This contains a request worth verifying independently.' if serious else
               'Check the context before you act. Some warning signs need a closer look.' if concerns else
               'No strong warning signs matched. That does not verify who sent this or make it safe.')
    limits = ['English-language rules identify wording and link structure, not intent or sender identity.'] + list(limitations or [
        'A legitimate message can trigger a rule; a scam can avoid every rule. No links were visited.'])
    if any(e.id == 'email:links_incomplete' for e in evidence):
        summary = 'HTML link review is incomplete. ' + summary
        limits.append('Some supplied HTML link targets could not be inspected locally. Review the original message in a trusted mail app; use an app or address you already trust instead of opening unknown links.')
    malformed_links = sum(e.id == 'url:malformed' or e.id.startswith('url:malformed:') for e in evidence)
    if malformed_links:
        summary = f'{malformed_links} link address(es) could not be parsed. Link review is incomplete. ' + summary
        limits.append(f'{malformed_links} link address(es) could not be parsed; their destination hosts remain unchecked. No links were visited.')
    if any(e.id == 'analysis:links_incomplete' for e in evidence):
        summary = 'Link review is incomplete. ' + summary
        limits.append('Only the first 8 unique literal HTTP(S) links are inspected, in appearance order; duplicate matching text is counted once before trailing punctuation is trimmed. Remaining links were not inspected. No links were visited.')
    return AnalysisReport(kind=kind, risk_index=None, risk_level=level, confidence='low', summary=summary,
        model_ran=False, decision_basis='rules',
        evidence=evidence, limitations=limits)


def analyze_text(text: str, kind='text') -> AnalysisReport:
    evidence = request_evidence(text)
    links = list(dict.fromkeys(re.findall(r'https?://[^\s<>"\x27]+', text, re.I)))
    if len(links) > 8:
        evidence.append(Evidence(id='analysis:links_incomplete', evidence_class='unknown', severity='info',
            title='Link review is incomplete',
            detail=f'{len(links)} unique literal links found; only the first 8 were inspected. Remaining links not inspected: {len(links)-8}.',
            source='Local bounded link coverage', weight=0))
    for index, url in enumerate(links[:8]):
        try:
            address=url.rstrip('.,!);')
            if '[' not in address: address=address.rstrip(']')
            items = analyze_url(address).evidence
        except ValueError:
            items = [Evidence(id='url:malformed', evidence_class='unknown', severity='medium',
                title='A link could not be parsed', detail='Check the address independently before opening it.', source='Local URL parser')]
        for item in items:
            item.id += ':'+str(index)
        evidence.extend(items)
    if not evidence:
        evidence.append(Evidence(id='text:none', evidence_class='unknown', severity='info',
            title='Sender and intent are unverified', detail='No strong wording patterns matched this input.', source='Local rules'))
    return communication_report(kind, evidence)
