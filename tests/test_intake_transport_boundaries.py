"""Small mocked worker transport; no native OCR, QR, model or network."""
import asyncio
import io
import json
from types import SimpleNamespace
import httpx
from PIL import Image
import pytest
from app.main import app
from app.analyzers import qr,screenshot


def png():
    out=io.BytesIO();Image.new('RGB',(2,2)).save(out,format='PNG');return out.getvalue()


def request(path):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://127.0.0.1') as client:
            return await client.post(path,files={'file':('PRIVATE.png',png(),'image/png')})
    return asyncio.run(run())


@pytest.mark.parametrize('module,path,key',[(qr,'/api/extract/qr','codes'),(screenshot,'/api/extract/screenshot','text')])
@pytest.mark.parametrize('text',['PRIVATE\ud800','PRIVATE\udfff'])
def test_lone_surrogate_is_controlled_private_failure(module,path,key,text,monkeypatch):
    payload={'codes':[text]} if key=='codes' else {'text':text,'language':'en-US'}
    monkeypatch.setattr(module.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=json.dumps(payload).encode()))
    response=request(path)
    assert response.status_code==503
    assert 'PRIVATE' not in response.text and 'surrogate' not in response.text
    assert not module._lock.locked()


@pytest.mark.parametrize('module,path,key',[(qr,'/api/extract/qr','codes'),(screenshot,'/api/extract/screenshot','text')])
def test_valid_unicode_astral_worker_output_unchanged(module,path,key,monkeypatch):
    text='English café 東京 😀 𝄞'
    payload={'codes':[text]} if key=='codes' else {'text':text,'language':'en-US'}
    # ensure_ascii emits UTF16 surrogate pairs in JSON; parser must preserve them.
    monkeypatch.setattr(module.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=json.dumps(payload).encode()))
    response=request(path)
    assert response.status_code==200 and response.json()['text']==text
    assert response.json()['review_required'] is True


@pytest.mark.parametrize('failure',[True,False])
def test_derived_grayscale_pixels_closed_with_retained_worker_or_save_result(failure,monkeypatch):
    content=png();saved=[];original=Image.Image.save
    def save(image,*args,**kwargs):
        if image.mode=='L':
            saved.append(image)
            if failure:raise OSError('PRIVATE save failure')
        return original(image,*args,**kwargs)
    monkeypatch.setattr(Image.Image,'save',save)
    monkeypatch.setattr(qr.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=b'{"codes":["Read only"]}'))
    retained=None
    try:
        if failure:
            with pytest.raises(qr.QrUnavailable) as error:qr.extract_qr(content)
            retained=error.value
            assert 'PRIVATE' not in str(retained)
        else:assert qr.extract_qr(content)['text']=='Read only'
        assert len(saved)==1
        with pytest.raises(ValueError,match='closed'):saved[0].getpixel((0,0))
        assert not qr._lock.locked()
    finally:
        for image in saved:image.close()
