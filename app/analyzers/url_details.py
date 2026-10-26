"""Literal URL anatomy without fetching, resolving or returning private components."""
import unicodedata
import idna

from app.analyzers.url import parse_address


def _hidden_characters(value):
    return any(unicodedata.category(character) in ('Cc','Cf','Cs') for character in value)


def _components(value):
    if not isinstance(value,str) or not value.strip() or len(value)>4096:
        raise ValueError('Enter one web address of at most 4,096 characters.')
    if _hidden_characters(value):
        raise ValueError('This address contains hidden control or formatting characters. Type a known address instead.')
    parsed,host=parse_address(value)
    try:
        display=idna.decode(host,uts46=True,std3_rules=True)
    except UnicodeError:
        display=host
    if _hidden_characters(display):
        raise ValueError('The Unicode host contains hidden control or formatting characters. Type a known address instead.')
    return {'scheme':parsed.scheme,'scheme_assumed':'://' not in value.strip(),
        'ascii_host':host,'display_unicode_host':display,
        'port':parsed.port if parsed.port is not None else 443 if parsed.scheme=='https' else 80,
        'username_present':parsed.username is not None or parsed.password is not None,
        'path_segment_count':sum(bool(segment) for segment in parsed.path.split('/')),
        'query_parameter_count':sum(bool(field) for field in parsed.query.split('&')),
        'fragment_present':bool(parsed.fragment)}


def inspect_url(value: str, known_website: str | None = None) -> dict:
    details=_components(value)
    details['reference_comparison']=None
    if known_website is not None:
        try:
            reference=_components(known_website)
            if reference['username_present']: raise ValueError()
        except ValueError as exc:
            raise ValueError('Enter a known HTTP(S) website without login details, hidden characters or text before @.') from exc
        details['reference_comparison']={
            'ascii_host':reference['ascii_host'],
            'exact_host_match':details['ascii_host']==reference['ascii_host'],
            'same_scheme':details['scheme']==reference['scheme'],
            'same_port':details['port']==reference['port']}
    details['notice']=('Literal inspection only: no site, DNS or reputation lookup. ASCII host uses nontransitional UTS #46 IDNA normalization; Unicode spelling is a display aid, not the original spelling or browser validation. '
        'An omitted port shows the scheme default. Path segments split on literal /; query count is nonempty &-delimited fields, not unique keys. Percent escapes are not decoded. '
        'Credentials, paths, query names/values and fragment content are omitted. HTTPS or matching components do not establish safety or ownership.')
    return details
