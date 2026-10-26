import asyncio,io,threading
from concurrent.futures import ThreadPoolExecutor
import pytest
from PIL import Image
from starlette.datastructures import UploadFile
from fastapi import HTTPException
from app.analyzers import media_context as media
from app.analyzers.image import InvalidImage
from app import intake

def png():
 out=io.BytesIO();Image.new('RGB',(1,1)).save(out,format='PNG');return out.getvalue()

def test_busy_rejects_before_second_actual_decode_and_retry_is_identical(monkeypatch):
 content=png();baseline=media.inspect_media(content);actual=media.decode_image;entered=threading.Event();release=threading.Event();calls=[]
 def held(data):
  image=actual(data);calls.append(1);entered.set()
  if not release.wait(2):image.close();raise AssertionError('bounded test wait expired')
  return image
 monkeypatch.setattr(media,'decode_image',held)
 with ThreadPoolExecutor(max_workers=1) as pool:
  pending=pool.submit(media.inspect_media,content)
  try:
   assert entered.wait(2)
   with pytest.raises(media.MediaUnavailable,match='Another media inspection'):media.inspect_media(content)
   assert len(calls)==1
  finally:release.set()
  assert pending.result(timeout=2)==baseline
 monkeypatch.setattr(media,'decode_image',actual);assert media.inspect_media(content)==baseline

@pytest.mark.parametrize('error',[InvalidImage('fixed invalid'),OSError('constructed failure')])
def test_failure_releases_admission_for_retry(monkeypatch,error):
 actual=media.decode_image
 def fail(data):raise error
 monkeypatch.setattr(media,'decode_image',fail)
 with pytest.raises(type(error)):media.inspect_media(png())
 monkeypatch.setattr(media,'decode_image',actual);assert media.inspect_media(png())['width']==1

def test_busy_endpoint_is_private_503_and_closes_upload(monkeypatch):
 def busy(content):raise media.MediaUnavailable('Another media inspection is running. Wait a moment, then try again.')
 monkeypatch.setattr(intake,'inspect_media',busy);upload=UploadFile(io.BytesIO(png()),filename='PRIVATE.png')
 with pytest.raises(HTTPException) as error:asyncio.run(intake.media_context_endpoint(upload))
 assert error.value.status_code==503 and 'PRIVATE' not in error.value.detail
 assert upload.file.closed

def test_metadata_phase_failure_releases_admission(monkeypatch):
 actual=media._inspect_media
 def fail(content):raise RuntimeError('constructed metadata phase failure')
 monkeypatch.setattr(media,'_inspect_media',fail)
 with pytest.raises(RuntimeError):media.inspect_media(png())
 monkeypatch.setattr(media,'_inspect_media',actual);assert media.inspect_media(png())['width']==1
