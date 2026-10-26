import pytest

from test_community import request


def test_inspector_is_post_only_and_omits_private_components():
    response=request('POST','/api/inspect/url',json={'url':'https://PRIVATE-USER@straße.example:8443/SECRET?token=PRIVATE-TOKEN#PRIVATE-FRAGMENT','known_website':'strasse.example'})
    assert response.status_code==200
    data=response.json()
    assert data['ascii_host']=='xn--strae-oqa.example' and data['username_present']
    assert data['path_segment_count']==1 and data['query_parameter_count']==1
    assert data['reference_comparison']['exact_host_match'] is False
    assert 'PRIVATE' not in response.text and 'SECRET' not in response.text and 'token=' not in response.text
    assert response.headers['cache-control']=='no-store'
    assert request('GET','/api/inspect/url').status_code==405
    assert request('POST','/api/inspect/url',json={'url':'bank.example'},headers={'origin':'https://other.test'}).status_code==403


@pytest.mark.parametrize('path,payload',[
    ('/api/inspect/url',{'url':'https://example.test/?PRIVATE='+('X'*4096)}),
    ('/api/analyze/text',{'text':'PRIVATE-CONTENT','PRIVATE-FIELD':'PRIVATE-VALUE'}),
    ('/api/analyze/email',{'raw_email':['PRIVATE-EMAIL']}),
])
def test_request_validation_errors_never_reflect_private_inputs(path,payload):
    response=request('POST',path,json=payload)
    assert response.status_code==422
    assert response.json()=={'detail':'Check the required fields, input format and length, then try again.'}
    assert 'PRIVATE' not in response.text
    assert response.headers['cache-control']=='no-store'
