"""Nontransitional UTS #46 prevents distinct reference hosts collapsing together."""
import socket
from email.message import EmailMessage

import pytest

from app.analyzers.email import analyze_email
from app.analyzers.url import analyze_url, parse_address
from app.analyzers.url_details import inspect_url


@pytest.mark.parametrize('unicode_host,ascii_host',[
    ('straße.example','xn--strae-oqa.example'),
    ('STRAẞE.example','xn--strae-oqa.example'),
    ('ς.example','xn--3xa.example'),
    ('σ.example','xn--4xa.example'),
    ('example.ΟΣ','example.xn--0xai'),
    ('example.ος','example.xn--0xag'),
    ('bücher.example','xn--bcher-kva.example'),
    ('ｂａｎｋ．example','bank.example'),
    ('Bank.Example.','bank.example'),
    ('AB--CD.example','ab--cd.example'),
    ('ａｂ－－ｃｄ.example','ab--cd.example'),
    ('bank.example。','bank.example'),
    ('１２７．０．０．１','127.0.0.1'),
])
def test_hostname_normalization(unicode_host,ascii_host):
    assert parse_address('https://'+unicode_host)[1]==ascii_host


@pytest.mark.parametrize('left,right',[
    ('straße.example','strasse.example'),
    ('ς.example','σ.example'),
    ('example.ΟΣ','example.ος'),
])
def test_deviation_characters_do_not_false_match_distinct_reference_sites(left,right):
    report=analyze_url('https://'+left,known_website='https://'+right)
    comparison=next(e for e in report.evidence if e.id=='url:comparison')
    assert comparison.title=='Hostname differs from your reference'
    assert not inspect_url('https://'+left,'https://'+right)['reference_comparison']['exact_host_match']


def test_unicode_and_same_punycode_match_and_display_preserves_sharp_s():
    result=inspect_url('https://straße.example','https://xn--strae-oqa.example')
    assert result['reference_comparison']['exact_host_match']
    assert result['display_unicode_host']=='straße.example'


@pytest.mark.parametrize('value,host,port',[
    ('https://127.0.0.1','127.0.0.1',None),
    ('https://127.0.0.1.:0','127.0.0.1',0),
    ('https://[2001:0db8::1]:8443','2001:db8::1',8443),
    ('http://[::1]','::1',None),
])
def test_numeric_addresses_bypass_domain_encoding(value,host,port):
    parsed,actual=parse_address(value)
    assert actual==host and parsed.port==port


@pytest.mark.parametrize('value',[
    'https://a\u200db.example','https://a\u200cb.example','https://bad\u202e.example',
    'https://example.org/\x00','\nhttps://example.org','https://example.org/\x85',
    'https://bad host.example','https://bank.example\\@evil.example',
    'https://bank.example..','https://bank.example。。','https://-bad.example',
    'https://bad-.example','https://bad_name.example','https://xn--a.example',
    'https://999.1.2.3','https://0127.0.0.1','https://example.org:65536',
    'https://example.org:bad','https://[2001:db8::1',
])
def test_invalid_host_port_and_hidden_characters_remain_rejected(value):
    with pytest.raises(ValueError): parse_address(value)


def test_email_displayed_url_and_mailto_use_same_distinct_idna_domains():
    for html in (
        '<a href="https://strasse.example">https://straße.example</a>',
        '<a href="mailto:office@strasse.example">office@straße.example</a>',
    ):
        message=EmailMessage()
        message.set_content(html,subtype='html',charset='utf-8')
        report=analyze_email(message.as_string())
        assert any(e.id.startswith('email:link_mismatch:') for e in report.evidence)


def test_idna_normalization_does_not_resolve_domains(monkeypatch):
    def forbidden(*_,**__): pytest.fail('A hostname was resolved')
    monkeypatch.setattr(socket,'getaddrinfo',forbidden)
    monkeypatch.setattr(socket,'create_connection',forbidden)
    assert parse_address('https://straße.example')[1]=='xn--strae-oqa.example'
