"""Privacy-safe literal URL anatomy; never a reputation or ownership verdict."""
import json
import socket

import pytest

from app.analyzers.url import parse_address
from app.analyzers.url_details import inspect_url


def test_components_expose_counts_but_never_credentials_path_query_or_fragment():
    details=inspect_url('https://private-user:private-password@example.org:8443/private-path/other?private-name=private-value&token=private-token#private-fragment')
    assert details['scheme']=='https' and details['port']==8443
    assert details['ascii_host']==details['display_unicode_host']=='example.org'
    assert details['username_present'] and details['path_segment_count']==2
    assert details['query_parameter_count']==2 and details['fragment_present']
    output=json.dumps(details)
    assert not any(value in output for value in ('private-user','private-password','private-path','private-name','private-value','private-token','private-fragment'))
    assert 'risk_level' not in details and 'risk_index' not in details


@pytest.mark.parametrize('value,scheme,port,assumed',[
    ('example.org','https',443,True),
    ('https://EXAMPLE.org.','https',443,False),
    ('HTTP://example.org','http',80,False),
    ('https://example.org:0','https',0,False),
    ('http://example.org:65535','http',65535,False),
    ('https://example.org:443','https',443,False),
])
def test_scheme_defaults_and_explicit_ports(value,scheme,port,assumed):
    result=inspect_url(value)
    assert result['scheme']==scheme and result['port']==port and result['scheme_assumed']==assumed
    assert result['ascii_host']=='example.org'


def test_unicode_host_is_display_only_and_reference_comparison_uses_same_ascii_normalization():
    result=inspect_url('https://bücher.example/secret','https://xn--bcher-kva.example:443/another?secret=value')
    assert result['ascii_host']=='xn--bcher-kva.example' and result['display_unicode_host']=='bücher.example'
    assert result['reference_comparison']=={'ascii_host':'xn--bcher-kva.example','exact_host_match':True,'same_scheme':True,'same_port':True}
    assert result['ascii_host']==parse_address('https://bücher.example')[1]
    assert 'secret' not in json.dumps(result) and 'another' not in json.dumps(result)


def test_invalid_punycode_is_rejected_instead_of_displayed_as_valid_host():
    with pytest.raises(ValueError): inspect_url('https://xn--a.example')


def test_nontransitional_idna_keeps_sharp_s_distinct_from_ss():
    result=inspect_url('https://straße.example','https://strasse.example')
    assert result['ascii_host']==parse_address('https://straße.example')[1]=='xn--strae-oqa.example'
    assert result['display_unicode_host']=='straße.example'
    assert not result['reference_comparison']['exact_host_match']
    assert 'nontransitional UTS #46' in result['notice'] and 'not the original spelling' in result['notice']


def test_reference_flags_host_scheme_and_effective_port_independently():
    result=inspect_url('http://sub.example.org:8080','https://example.org')
    assert result['reference_comparison']=={'ascii_host':'example.org','exact_host_match':False,'same_scheme':False,'same_port':False}
    assert inspect_url('https://example.org','https://example.org:443')['reference_comparison']['same_port']
    assert not inspect_url('https://example.org:0','https://example.org')['reference_comparison']['same_port']


@pytest.mark.parametrize('value,host,port',[
    ('https://[2001:0db8::1]:8443/a','2001:db8::1',8443),
    ('http://127.0.0.1','127.0.0.1',80),
])
def test_numeric_hosts_are_literal_without_resolution(value,host,port):
    result=inspect_url(value)
    assert result['ascii_host']==host and result['port']==port


def test_percent_encoding_and_path_at_sign_never_become_authority_or_decoded_segments():
    result=inspect_url('https://example.org/a%2Fb/user@somewhere.example?redirect=https%3A%2F%2Fother.example%2F%40user&private=value')
    assert result['ascii_host']=='example.org' and not result['username_present']
    assert result['path_segment_count']==2 and result['query_parameter_count']==2
    assert 'other.example' not in json.dumps(result)


def test_percent_encoded_userinfo_is_omitted_and_destination_stays_actual_host():
    result=inspect_url('https://bank.example%40private:private-secret@actual.example/path')
    assert result['ascii_host']=='actual.example' and result['username_present']
    assert 'bank.example' not in json.dumps(result) and 'private-secret' not in json.dumps(result)


def test_literal_counts_ignore_empty_segments_and_keep_duplicate_and_bare_query_fields():
    result=inspect_url('https://example.org//one///two/?a=1&&a=2&bare&=value&')
    assert result['path_segment_count']==2 and result['query_parameter_count']==4
    assert '&-delimited fields' in result['notice'] and 'not unique keys' in result['notice']


def test_percent_escaped_controls_are_not_decoded_or_echoed():
    result=inspect_url('https://example.org/%00%0A%2F?%E2%80%AE=private#%00')
    assert result['path_segment_count']==1 and result['query_parameter_count']==1
    assert '%00' not in json.dumps(result) and 'private' not in json.dumps(result)


@pytest.mark.parametrize('value',[
    '',None,123,'https://example.org/'+('x'*4096),'ftp://example.org',
    'https://bad host.example','https://example.org:65536','https://example.org:not-a-port',
    'https://[2001:db8::1','https://bank.example%40actual.example',
    'https://example.org/\nsecret','\thttps://example.org','https://example.org/\x00',
    'https://example.org/\x85','https://example.org/\u202eevil',
    'https://example.org/\u2066hidden\u2069','https://example.org/\u200bhidden',
    'https://example.org/\ud800',
])
def test_invalid_or_hidden_input_is_rejected_with_no_private_value_echo(value):
    with pytest.raises(ValueError) as error: inspect_url(value)
    assert 'secret' not in str(error.value) and 'evil' not in str(error.value) and 'hidden\u2069' not in str(error.value)


@pytest.mark.parametrize('reference',['https://private-user:private-pass@example.org','https://@example.org','ftp://example.org','https://example.org/\u202eprivate'])
def test_invalid_or_credential_bearing_reference_is_rejected_privately(reference):
    with pytest.raises(ValueError,match='known HTTP') as error:
        inspect_url('https://example.org',reference)
    assert 'private-user' not in str(error.value) and 'private-pass' not in str(error.value)


def test_decoded_host_controls_cannot_enter_display_even_if_parser_accepts_ascii_label(monkeypatch):
    import app.analyzers.url_details as helper
    class HiddenHost(str):
        pass
    parsed,_=parse_address('https://example.org')
    monkeypatch.setattr(helper,'parse_address',lambda _: (parsed,HiddenHost('example.org')))
    monkeypatch.setattr(helper.idna,'decode',lambda *_,**__: 'example\u202e.org')
    with pytest.raises(ValueError,match='Unicode host'):
        helper.inspect_url('https://example.org')


def test_inspection_never_calls_dns_or_opens_a_socket(monkeypatch):
    def forbidden(*_,**__): pytest.fail('Literal inspection attempted network access')
    monkeypatch.setattr(socket,'getaddrinfo',forbidden)
    monkeypatch.setattr(socket,'create_connection',forbidden)
    result=inspect_url('https://not-resolved.example/private?private=secret','https://known.example')
    assert result['ascii_host']=='not-resolved.example'
