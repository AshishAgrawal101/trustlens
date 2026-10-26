"""URL fields preserve raw controls until the shared literal parser rejects them."""
import pytest
from pydantic import ValidationError
from app.models import UrlRequest,TextRequest,CallRequest,EmailRequest
from test_community import request

@pytest.mark.parametrize('endpoint',['analyze','inspect'])
@pytest.mark.parametrize('field',['url','known_website'])
@pytest.mark.parametrize('value',['\thttps://example.org/','https://example.org/\n','\ufeffhttps://example.org/','https://exam\tple.org/','\t'])
def test_raw_controls_reach_both_producers_and_reject_privately(endpoint,field,value):
    payload={'url':'https://example.org/',field:value}
    response=request('POST','/api/'+endpoint+'/url',json=payload)
    assert response.status_code==400
    assert value not in response.text
    assert response.headers['cache-control']=='no-store'

@pytest.mark.parametrize('endpoint',['analyze','inspect'])
@pytest.mark.parametrize('padding',[' ','\u00a0'])
def test_existing_ordinary_outer_whitespace_remains_accepted(endpoint,padding):
    r=request('POST','/api/'+endpoint+'/url',json={'url':padding+'https://example.org/'+padding,'known_website':padding+'example.org'+padding})
    assert r.status_code==200

@pytest.mark.parametrize('field',['url','known_website'])
def test_raw_length_bound_counts_outer_spaces(field):
    value='https://example.org/'+' '*(4096-len('https://example.org/'))
    m=UrlRequest(**({'url':'example.org',field:value}));assert getattr(m,field)==value
    with pytest.raises(ValidationError):UrlRequest(**({'url':'example.org',field:value+' '}))

def test_only_url_fields_override_global_trimming():
    m=UrlRequest(url=' https://example.org/ ',known_website=' example.org ',claimed_brand=' Example ')
    assert (m.url,m.known_website,m.claimed_brand)==(' https://example.org/ ',' example.org ','Example')
    assert TextRequest(text=' hi ').text=='hi'
    assert CallRequest(transcript=' hi ').transcript=='hi'
    assert EmailRequest(raw_email=' hi ').raw_email=='hi'
