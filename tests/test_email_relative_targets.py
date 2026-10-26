"""Scheme-relative destinations must not disappear behind ordinary link labels."""
from email.message import EmailMessage
import pytest
from app.analyzers import email as analyzer
from app.analyzers.url import analyze_url
from app.guidance import add_guidance


def report(body):
    message=EmailMessage();message.set_content(body,subtype='html',charset='utf-8')
    return analyzer.analyze_email_bytes(message.as_bytes())
def hosts(r):return [e.detail for e in r.evidence if e.id.startswith('email:relative_host:')]
def partial(r):return next((e for e in r.evidence if e.id=='email:links_incomplete'),None)


@pytest.mark.parametrize('href,host,key,level',[
    ('//bank.example@other.example/pay','other.example','userinfo','high'),
    ('//127.0.0.1/pay','127.0.0.1','ip','guarded'),
    ('//bücher.example/pay','xn--bcher-kva.example','idn','guarded'),
    ('//bit.ly/PRIVATE','bit.ly','short','guarded'),
    ('//a.b.c.d.example/path','a.b.c.d.example','subdomains','guarded')])
def test_neutral_labels_retain_existing_scheme_independent_rules(href,host,key,level):
    r=add_guidance(report(f'<a href="{href}">Open statement</a>'))
    assert hosts(r)==[host]
    row=next(e for e in r.evidence if e.id.startswith('url:'+key+':relative:'))
    baseline=next(e for e in analyze_url('https:'+href).evidence if e.id=='url:'+key)
    assert (row.evidence_class,row.severity,row.weight,row.title,row.detail)==(baseline.evidence_class,baseline.severity,baseline.weight,baseline.title,baseline.detail)
    assert r.risk_level==level and not partial(r)
    assert not any(e.id.startswith('url:http') for e in r.evidence)
    assert not any('https:' in e.detail or 'https:' in e.source for e in r.evidence)
    if key=='userinfo':assert 'Use a known address instead of this link' in [a.title for a in r.actions]


def test_userinfo_path_and_query_private_values_never_echo_in_evidence_or_export():
    r=add_guidance(report('<a href="//PRIVATE-USER:PRIVATE-PASS@other.example/PRIVATE-PATH?SECRET=1">Open statement</a>'))
    assert hosts(r)==['other.example']
    combined=' '.join(e.detail+' '+e.source for e in r.evidence)+r.share_summary
    assert 'PRIVATE' not in combined and 'SECRET' not in combined
    assert 'https://' not in ' '.join(e.detail+' '+e.source for e in r.evidence)
    assert any('transport' in x.lower() and 'unknown' in x.lower() for x in r.limitations)


@pytest.mark.parametrize('count',[1,8])
def test_bounded_valid_targets_are_observed_without_partial_notice(count):
    r=report(''.join(f'<a href="//site{i}.example/p">Open</a>' for i in range(count)))
    assert hosts(r)==[f'site{i}.example' for i in range(count)]
    assert not partial(r) and r.risk_level=='low'
    assert not any(e.id=='analysis:links_incomplete' for e in r.evidence)


def test_ninth_target_is_partial_and_never_passed_to_shared_rules(monkeypatch):
    seen=[]
    def track(value):seen.append(value);return analyze_url(value)
    monkeypatch.setattr(analyzer,'analyze_url',track,raising=False)
    r=add_guidance(report(''.join(f'<a href="//site{i}.example/PRIVATE">Open</a>' for i in range(8))+'<a href="//PRIVATE@unexamined.example/SECRET">Open</a>'))
    assert len(seen)==8 and not any('unexamined' in s for s in seen)
    assert len(hosts(r))==8 and not any(e.id.startswith('url:userinfo') for e in r.evidence)
    row=partial(r);assert row and row.weight==0 and '1' in row.detail and 'limit' in row.detail
    assert 'HTML link review is incomplete' in r.summary
    assert 'HTML link review was incomplete' in r.share_summary
    assert 'PRIVATE' not in row.detail+r.share_summary and 'unexamined.example' not in row.detail+r.share_summary


def test_duplicate_targets_across_mime_parts_do_not_spend_slots():
    message=EmailMessage();message.make_mixed()
    for body in ['<a href="//site0.example/p">Open</a>'*12,''.join(f'<a href="//site{i}.example/p">Open</a>' for i in range(8))]:
        part=EmailMessage();part.set_content(body,subtype='html');message.attach(part)
    r=analyzer.analyze_email_bytes(message.as_bytes())
    assert hosts(r)==[f'site{i}.example' for i in range(8)] and not partial(r)


def test_overflow_and_literal_http_budget_remain_distinct():
    body=' '.join(f'https://literal{i}.example/p' for i in range(9))+''.join(f'<a href="//relative{i}.example/p">Open</a>' for i in range(10))
    r=add_guidance(report(body));assert len(hosts(r))==8
    assert any(e.id=='analysis:links_incomplete' for e in r.evidence)
    assert partial(r) and '2' in partial(r).detail
    assert 'Only the first 8 unique literal links' in r.share_summary and 'HTML link review was incomplete' in r.share_summary


def test_adapter_is_allowlist_not_future_transport_or_other_rules(monkeypatch):
    from app.models import Evidence
    original=analyze_url('https://example.org')
    original.evidence.extend([Evidence(id='url:future_transport',evidence_class='verified',severity='info',title='PRIVATE HTTPS assertion',detail='PRIVATE synthetic scheme',source='test'),Evidence(id='url:http',evidence_class='inferred',severity='medium',title='Unencrypted transport',detail='PRIVATE',source='test',weight=.3)])
    monkeypatch.setattr(analyzer,'analyze_url',lambda value:original,raising=False)
    r=report('<a href="//example.org/PRIVATE">Open</a>')
    assert hosts(r)==['example.org']
    assert not any(e.id.startswith(('url:http','url:future_transport')) for e in r.evidence)
    assert 'PRIVATE' not in ' '.join(e.title+e.detail for e in r.evidence)


def test_invalid_hidden_target_is_not_sanitized_into_an_inspected_host():
    r=report('<a href="//bank.\u200bexample/PRIVATE">Open</a>')
    assert not hosts(r) and partial(r)
