"""Streaming upload limits run before Starlette multipart spooling."""
import asyncio
import json

import pytest
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.upload_limits import UploadLimitMiddleware, UPLOAD_LIMITS, IMAGE_BODY_LIMIT, EMAIL_BODY_LIMIT, DETAIL


def scope(path='/api/extract/qr',headers=(),method='POST'):
    return {'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':method,
        'scheme':'http','path':path,'raw_path':path.encode(),'query_string':b'',
        'headers':[(b'host',b'127.0.0.1'),*headers],'server':('127.0.0.1',80),'client':('127.0.0.1',12345),'root_path':''}


def invoke(app,request_scope,chunks):
    async def run():
        sent=[];reads=0;done=asyncio.Event()
        async def receive():
            nonlocal reads
            if reads<len(chunks):
                message={'type':'http.request','body':chunks[reads],'more_body':reads<len(chunks)-1}
                reads+=1
                return message
            await done.wait()
            return {'type':'http.disconnect'}
        async def send(message):
            sent.append(message)
            if message['type']=='http.response.body' and not message.get('more_body',False): done.set()
        await asyncio.wait_for(app(request_scope,receive,send),5)
        return sent,reads
    return asyncio.run(run())


def result(sent):
    starts=[m for m in sent if m['type']=='http.response.start']
    assert len(starts)==1
    body=b''.join(m.get('body',b'') for m in sent if m['type']=='http.response.body')
    return starts[0]['status'],body,dict(starts[0].get('headers',[]))


def multipart(content):
    return b'--b\r\nContent-Disposition: form-data; name="file"; filename="private-input.bin"\r\nContent-Type: application/octet-stream\r\n\r\n'+content+b'\r\n--b--\r\n'


def test_exact_production_upload_limits():
    assert IMAGE_BODY_LIMIT==64*1024*1024+64*1024
    assert EMAIL_BODY_LIMIT==512*1024
    assert set(UPLOAD_LIMITS)=={'/api/analyze/image','/api/extract/screenshot','/api/extract/qr','/api/analyze/email-file','/api/inspect/media'}


@pytest.mark.parametrize('header',[b'513',b'00000513',b' 513 ',b'9'*5000])
def test_valid_oversize_header_rejects_without_receiving_or_calling_app(monkeypatch,header):
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/extract/qr',512)
    async def inner(*_): pytest.fail('Oversized header must not call parser/app')
    sent,reads=invoke(UploadLimitMiddleware(inner),scope(headers=[(b'Content-Length',header)]),[b'PRIVATE'])
    status,body,headers=result(sent)
    assert status==413 and reads==0 and json.loads(body)=={'detail':DETAIL}
    assert b'PRIVATE' not in body and headers[b'cache-control']==b'no-store'
    assert headers[b'x-content-type-options']==b'nosniff' and b'content-security-policy' in headers


@pytest.mark.parametrize('header',[None,b'0',b'1',b'-1',b'unknown',b'1, 999'])
def test_stream_counter_rejects_chunked_missing_invalid_or_inaccurate_headers(monkeypatch,header):
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/extract/qr',10)
    received=[]
    async def inner(request_scope,receive,send):
        while True:
            message=await receive()
            received.append(message['body'])
            if not message.get('more_body'): break
        pytest.fail('A truncated body must never reach analysis')
    headers=[] if header is None else [(b'content-length',header)]
    sent,reads=invoke(UploadLimitMiddleware(inner),scope(headers=headers),[b'12345',b'PRIVATE',b'not-read'])
    assert result(sent)[0]==413 and reads==2 and received==[b'12345']
    assert json.loads(result(sent)[1])=={'detail':DETAIL}


def test_exact_limit_is_accepted_and_underlying_asgi_messages_are_unchanged(monkeypatch):
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/extract/qr',10)
    received=[]
    async def inner(request_scope,receive,send):
        received.append(await receive());received.append(await receive())
        await JSONResponse({'ok':True})(request_scope,receive,send)
    sent,reads=invoke(UploadLimitMiddleware(inner),scope(headers=[(b'content-length',b'00000000000010')]),[b'12345',b'67890'])
    assert result(sent)[0]==200 and reads==2
    assert received==[{'type':'http.request','body':b'12345','more_body':True},{'type':'http.request','body':b'67890','more_body':False}]


def test_custom_downstream_error_response_cannot_echo_or_return_success_after_limit(monkeypatch):
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/extract/qr',1)
    async def inner(request_scope,receive,send):
        try: await receive()
        except HTTPException:
            await JSONResponse({'unsafe':'PRIVATE'},status_code=200)(request_scope,receive,send)
    sent,_=invoke(UploadLimitMiddleware(inner),scope(),[b'PRIVATE'])
    assert result(sent)[0]==413 and json.loads(result(sent)[1])=={'detail':DETAIL}


def test_downstream_retry_cannot_read_more_after_overflow(monkeypatch):
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/extract/qr',1)
    async def inner(request_scope,receive,send):
        for _ in range(2):
            with pytest.raises(HTTPException): await receive()
        await JSONResponse({'unsafe':'must be replaced'})(request_scope,receive,send)
    sent,reads=invoke(UploadLimitMiddleware(inner),scope(),[b'PRIVATE',b'not-read'])
    assert reads==1 and result(sent)[0]==413


def test_response_already_started_is_closed_without_second_start_or_exception(monkeypatch):
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/extract/qr',1)
    async def inner(request_scope,receive,send):
        await send({'type':'http.response.start','status':200,'headers':[]})
        await send({'type':'http.response.body','body':b'already-sent','more_body':True})
        await receive()
    sent,_=invoke(UploadLimitMiddleware(inner),scope(),[b'PRIVATE'])
    assert result(sent)[:2]==(200,b'already-sent')
    assert sent[-1]=={'type':'http.response.body','body':b'','more_body':False}


def test_unrelated_exception_is_not_hidden():
    async def inner(*_): raise RuntimeError('ordinary app bug')
    with pytest.raises(RuntimeError,match='ordinary app bug'):
        invoke(UploadLimitMiddleware(inner),scope(),[b''])


@pytest.mark.parametrize('path,method',[('/api/analyze/text','POST'),('/api/extract/qr','GET'),('/unrelated','POST')])
def test_non_upload_scope_is_passed_without_mutation(path,method):
    request_scope=scope(path,[(b'content-length',b'9'*5000)],method)
    original=dict(request_scope)
    async def inner(actual,receive,send):
        assert actual is request_scope
        message=await receive()
        await JSONResponse({'bytes':len(message['body'])})(actual,receive,send)
    sent,reads=invoke(UploadLimitMiddleware(inner),request_scope,[b'unchanged'])
    assert result(sent)[0]==200 and reads==1 and request_scope==original


def test_non_http_scope_is_passed_without_mutation():
    actual=[]
    async def inner(request_scope,receive,send): actual.append(request_scope)
    request_scope={'type':'lifespan'}
    asyncio.run(UploadLimitMiddleware(inner)(request_scope,None,None))
    assert actual==[request_scope]


@pytest.mark.parametrize('path',['/api/analyze/image','/api/extract/screenshot','/api/extract/qr','/api/analyze/email-file'])
def test_actual_main_middleware_allows_normal_file_and_keeps_privacy_headers(monkeypatch,path):
    import app.main as main
    import app.intake as intake
    from app.analyzers.text import analyze_text
    calls=[]
    def analyzed(content):
        calls.append(content)
        return analyze_text('The library meeting is tomorrow.')
    def extracted(content):
        calls.append(content)
        return {'text':'review me','codes':['review me'],'review_required':True,'notice':'Review first.'}
    monkeypatch.setattr(main,'analyze_image_with_credentials',analyzed)
    monkeypatch.setattr(main,'extract_screenshot',extracted)
    monkeypatch.setattr(intake,'extract_qr',extracted)
    monkeypatch.setattr(intake,'analyze_email_bytes',analyzed)
    monkeypatch.setitem(UPLOAD_LIMITS,path,512)
    body=multipart(b'complete file')
    request_scope=scope(path,[(b'content-type',b'multipart/form-data; boundary=b'),(b'content-length',str(len(body)).encode())])
    sent,_=invoke(main.app,request_scope,[body])
    status,_,headers=result(sent)
    assert status==200 and calls==[b'complete file']
    assert headers[b'cache-control']==b'no-store' and b'content-security-policy' in headers
    assert main.app.user_middleware[0].cls is UploadLimitMiddleware


@pytest.mark.parametrize('header',[None,b'1'])
def test_actual_main_chunked_overflow_closes_spools_never_analyzes_prefix(monkeypatch,header):
    import app.main as main
    import app.intake as intake
    import starlette.formparsers as parsers
    files=[]
    factory=parsers.SpooledTemporaryFile
    def spool(*a,**kw):
        kw['max_size']=8
        file=factory(*a,**kw);files.append(file);return file
    monkeypatch.setattr(parsers,'SpooledTemporaryFile',spool)
    monkeypatch.setattr(intake,'extract_qr',lambda _:pytest.fail('Truncated input reached analyzer'))
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/extract/qr',512)
    first=multipart(b'prefix'*30)[:-9]
    headers=[(b'content-type',b'multipart/form-data; boundary=b')]
    if header is not None: headers.append((b'content-length',header))
    sent,reads=invoke(main.app,scope(headers=headers),[first,b'PRIVATE'*100,b'not-read'])
    assert result(sent)[0]==413 and reads==2
    assert json.loads(result(sent)[1])=={'detail':DETAIL}
    assert files and all(f._rolled and f.closed for f in files)


def test_actual_main_header_overflow_never_starts_multipart_spooling(monkeypatch):
    import app.main as main
    import starlette.formparsers as parsers
    monkeypatch.setitem(UPLOAD_LIMITS,'/api/analyze/email-file',512)
    monkeypatch.setattr(parsers,'SpooledTemporaryFile',lambda *a,**kw:pytest.fail('Multipart spooled before header rejection'))
    headers=[(b'content-type',b'multipart/form-data; boundary=b'),(b'content-length',b'513')]
    sent,reads=invoke(main.app,scope('/api/analyze/email-file',headers),[multipart(b'private')])
    assert result(sent)[0]==413 and reads==0
