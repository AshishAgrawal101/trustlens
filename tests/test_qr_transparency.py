import importlib,io,hashlib
from pathlib import Path
import pytest
from PIL import Image
from app.analyzers.image import decode_image,InvalidImage

def module():return importlib.import_module('app.analyzers.qr_pixels')
def encoded(image,fmt='PNG',**kwargs):
 stream=io.BytesIO();image.save(stream,format=fmt,**kwargs);return stream.getvalue()

@pytest.mark.parametrize('mode,pixel,expected',[('RGBA',(0,0,0,0),(255,255,255)),('RGBA',(0,0,0,128),(127,127,127)),('LA',(0,0),(255,255,255))])
def test_alpha_white_background(mode,pixel,expected):
 raw=encoded(Image.new(mode,(2,3),pixel));result=module().decode_qr_image(raw)
 try:assert result.mode=='RGB' and result.getpixel((0,0))==expected
 finally:result.close()

def test_palette_transparency_and_orientation():
 image=Image.new('P',(2,3),0);image.putpalette([0,0,0]+[255,255,255]*255);exif=Image.Exif();exif[274]=6
 result=module().decode_qr_image(encoded(image,transparency=0,exif=exif))
 try:assert result.size==(3,2) and result.getpixel((0,0))==(255,255,255)
 finally:result.close()

@pytest.mark.parametrize('fmt',['PNG','JPEG','WEBP'])
def test_opaque_returns_exact_validated_object(monkeypatch,fmt):
 helper=module();raw=encoded(Image.new('RGB',(2,3),(10,20,30)),fmt);validated=decode_image(raw);monkeypatch.setattr(helper,'decode_image',lambda data:validated)
 result=helper.decode_qr_image(raw);assert result is validated;result.close()

def test_validation_first_and_failure_closes_initial_rgb(monkeypatch):
 helper=module()
 for raw in [b'',b'not an image']:
  with pytest.raises(InvalidImage):helper.decode_qr_image(raw)
 raw=encoded(Image.new('RGBA',(2,3),(0,0,0,0)));validated=decode_image(raw);monkeypatch.setattr(helper,'decode_image',lambda data:validated)
 def fail(*a,**k):raise OSError('constructed header failure')
 monkeypatch.setattr(helper.Image,'open',fail)
 with pytest.raises(InvalidImage):helper.decode_qr_image(raw)
 with pytest.raises(ValueError):validated.getpixel((0,0))

def test_transparent_first_rgb_closed_before_second_source_load(monkeypatch):
 helper=module();raw=encoded(Image.new('RGBA',(2,3),(0,0,0,0)));validated=decode_image(raw);original_open=helper.Image.open;calls=[];monkeypatch.setattr(helper,'decode_image',lambda data:validated)
 def opening(*a,**k):
  calls.append(1)
  if len(calls)==2:
   with pytest.raises(ValueError):validated.getpixel((0,0))
  return original_open(*a,**k)
 monkeypatch.setattr(helper.Image,'open',opening);result=helper.decode_qr_image(raw);result.close();assert len(calls)==2

def test_frozen_default_decoder_file_unchanged():
 assert hashlib.sha256((Path(__file__).resolve().parents[1]/'app/analyzers/image.py').read_bytes()).hexdigest()=='19ba25ed5e3b1ba331c90b9d4f2ef776336bc8da4810115998ce0bc0c6a8fe1f'

def test_existing_byte_and_pixel_gates_run_before_alpha_pass(monkeypatch):
 from app.analyzers import image as frozen
 helper=module();raw=encoded(Image.new('RGBA',(2,3),(0,0,0,0)))
 monkeypatch.setattr(frozen,'MAX_UPLOAD_BYTES',len(raw)-1)
 with pytest.raises(InvalidImage,match='64 MB'):helper.decode_qr_image(raw)
 monkeypatch.setattr(frozen,'MAX_UPLOAD_BYTES',64*1024*1024);monkeypatch.setattr(frozen,'MAX_PIXELS',5)
 with pytest.raises(InvalidImage,match='20 million'):helper.decode_qr_image(raw)

def test_alpha_failure_explicitly_closes_loaded_source_and_intermediates(monkeypatch):
 helper=module();raw=encoded(Image.new('RGBA',(2,3),(0,0,0,0)));validated=decode_image(raw);opened=[];converted=[];created=[]
 original_open=helper.Image.open;original_convert=helper.Image.Image.convert;original_new=helper.Image.new;original_channel=helper.Image.Image.getchannel
 monkeypatch.setattr(helper,'decode_image',lambda data:validated)
 def opening(*a,**k):
  result=original_open(*a,**k);opened.append(result);return result
 def convert(self,*a,**k):
  result=original_convert(self,*a,**k);converted.extend([self,result]);return result
 def new(*a,**k):
  result=original_new(*a,**k);created.append(result);return result
 def channel(self,*a,**k):
  result=original_channel(self,*a,**k);converted.append(result);return result
 def fail(self,*a,**k):raise OSError('constructed composite failure')
 monkeypatch.setattr(helper.Image,'open',opening);monkeypatch.setattr(helper.Image.Image,'convert',convert);monkeypatch.setattr(helper.Image,'new',new);monkeypatch.setattr(helper.Image.Image,'paste',fail);monkeypatch.setattr(helper.Image.Image,'getchannel',channel)
 with pytest.raises(InvalidImage):helper.decode_qr_image(raw)
 for image in [validated,*opened,*converted,*created]:
  with pytest.raises(ValueError):image.getpixel((0,0))



def test_native_transparent_qr_api_preserves_review_only_contract():
 import asyncio
 import httpx
 cv2=pytest.importorskip('cv2')
 from fastapi import FastAPI
 from app.intake import router
 from app.analyzers import qr
 matrix=cv2.QRCodeEncoder_create().encode('TRUSTLENS SAFE LOCAL TEST')
 mask=Image.fromarray(matrix)
 # Add a white quiet zone before enlarging the fixed, harmless payload.
 bordered=Image.new('L',(mask.width+8,mask.height+8),255);bordered.paste(mask,(4,4))
 alpha=bordered.resize((bordered.width*8,bordered.height*8),Image.Resampling.NEAREST).point(lambda p:255 if p==0 else 0)
 image=Image.new('RGBA',alpha.size,(0,0,0,0));image.putalpha(alpha);raw=encoded(image)
 app=FastAPI();app.include_router(router)
 async def run():
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as client:
   return await client.post('/api/extract/qr',files={'file':('constructed-transparent.png',raw,'image/png')})
 response=asyncio.run(run());assert response.status_code==200
 data=response.json();assert data['text']=='TRUSTLENS SAFE LOCAL TEST' and data['codes']==['TRUSTLENS SAFE LOCAL TEST']
 assert data['review_required'] is True and set(data)=={'text','codes','review_required','notice'}
 assert 'No address was opened' in data['notice'] and 'against white' in data['notice']
 assert not qr._lock.locked()
 assert qr._lock.acquire(blocking=False);qr._lock.release()
