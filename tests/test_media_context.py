import asyncio
import io
from fastapi import FastAPI
import httpx
from PIL import Image
import pytest
from app.analyzers import media_context as media
from app.analyzers.image import InvalidImage
from app.intake import router


def fixture(fmt='JPEG', orientation=None, **tags):
    exif=Image.Exif()
    if orientation is not None: exif[274]=orientation
    for tag,value in tags.items(): exif[int(tag)]=value
    stream=io.BytesIO()
    Image.new('RGB',(9,5),'white').save(stream,format=fmt,exif=exif)
    return stream.getvalue()


@pytest.mark.parametrize('fmt',['JPEG','PNG','WEBP'])
def test_allowlist_and_no_metadata_is_not_authenticity(fmt,monkeypatch):
    import app.analyzers.image as image
    monkeypatch.setattr(image,'load_runtime',lambda:pytest.fail('model must not load'))
    data=fixture(fmt)
    result=media.inspect_media(data)
    assert set(result)=={'format','width','height','display_width','display_height','bytes','capture_time','software','camera_make','camera_model','gps_present','notice'}
    assert result['format']==fmt and result['bytes']==len(data)
    assert result['capture_time'] is None and result['gps_present'] is False
    assert 'edited or removed' in result['notice']


@pytest.mark.parametrize('orientation,display',[(1,(9,5)),(3,(9,5)),(6,(5,9)),(8,(5,9))])
def test_original_and_adjusted_dimensions(orientation,display):
    r=media.inspect_media(fixture(orientation=orientation))
    assert (r['width'],r['height'])==(9,5)
    assert (r['display_width'],r['display_height'])==display


def test_allowlisted_exif_and_nested_time_only():
    r=media.inspect_media(fixture(**{'305':'Editor','271':'Camera maker','272':'Camera model','34665':{36867:'2024:02:29 23:59:59'},'315':'PRIVATE AUTHOR','42033':'PRIVATE SERIAL'}))
    assert r['software']=='Editor' and r['camera_make']=='Camera maker'
    assert r['camera_model']=='Camera model' and r['capture_time']=='2024:02:29 23:59:59'
    assert 'PRIVATE' not in str(r)


@pytest.mark.parametrize('value',[None,b'Editor','x'*121,'Editor\nPRIVATE','\u202eEditor'])
def test_software_optional_invalid_values(value):
    assert media._text(value,120) is None


@pytest.mark.parametrize('value',['2026:02:29 01:02:03','2024:02:29 24:00:00','2024:2:29 01:02:03','PRIVATE','2024:02:29 01:02:03\0'])
def test_time_invalid_unknown(value):
    assert media._time(value) is None


def test_gps_presence_without_accessing_coordinates(monkeypatch):
    original=Image.Image.getexif
    data=fixture()
    class Exif(dict):
        def get_ifd(self,tag):
            assert tag==34665
            return {}
    monkeypatch.setattr(Image.Image,'getexif',lambda self:Exif({34853:123}))
    # Stub shared decode only here to isolate prohibited GPS IFD access.
    monkeypatch.setattr(media,'decode_image',lambda content:Image.new('RGB',(9,5)))
    r=media.inspect_media(data)
    assert r['gps_present'] is True


def test_optional_exif_failure_is_unknown(monkeypatch):
    data=fixture()
    monkeypatch.setattr(media,'decode_image',lambda content:Image.new('RGB',(9,5)))
    monkeypatch.setattr(Image.Image,'getexif',lambda self:(_ for _ in ()).throw(ValueError('PRIVATE')))
    r=media.inspect_media(data)
    assert r['software'] is None and r['capture_time'] is None and 'PRIVATE' not in str(r)


@pytest.mark.parametrize('data',[b'',b'not an image',b'GIF89a'])
def test_bad_image_route_400_fixed(data):
    app=FastAPI();app.include_router(router)
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as client:
            return await client.post('/api/inspect/media',files={'file':('PRIVATE.png',data)})
    r=asyncio.run(run())
    assert r.status_code==400 and 'PRIVATE' not in r.text


def test_endpoint_real_fixture():
    app=FastAPI();app.include_router(router)
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as client:
            return await client.post('/api/inspect/media',files={'file':('PRIVATE.jpg',fixture(orientation=6))})
    r=asyncio.run(run())
    assert r.status_code==200 and r.json()['display_width']==5 and 'PRIVATE' not in r.text


def test_pixel_limit_preserves_shared_policy(monkeypatch):
    import app.analyzers.image as image
    monkeypatch.setattr(image,'MAX_PIXELS',44)
    with pytest.raises(InvalidImage,match='20 million pixels'):
        media.inspect_media(fixture())


def test_file_closed_and_read_bounded_on_error():
    from app.intake import media_context_endpoint, MAX_UPLOAD_BYTES
    class Upload:
        closed=False
        async def read(self,n):
            assert n==MAX_UPLOAD_BYTES+1
            return b'bad'
        async def close(self): self.closed=True
    upload=Upload()
    with pytest.raises(Exception) as error:
        asyncio.run(media_context_endpoint(upload))
    assert error.value.status_code==400 and upload.closed


def test_software_limit_pair_and_capture_not_generic_datetime():
    assert media._text('x'*120,120)=='x'*120
    assert media._text('x'*121,120) is None
    r=media.inspect_media(fixture(**{'306':'2024:02:29 01:02:03'}))
    assert r['capture_time'] is None


def test_native_rotated_gps_metadata_returns_only_presence():
    # Full shared decode path, unlike the isolated no-explicit-GPS-access test.
    data=fixture(orientation=6,**{'34853':{1:'N',2:(1,2,3),3:'E',4:(4,5,6)}})
    r=media.inspect_media(data)
    assert r['gps_present'] is True and (r['display_width'],r['display_height'])==(5,9)
    assert set(r)=={'format','width','height','display_width','display_height','bytes','capture_time','software','camera_make','camera_model','gps_present','notice'}


def test_decoded_pixels_closed_before_header_reopened(monkeypatch):
    data=fixture()
    class Decoded:
        size=(9,5)
        closed=False
        def close(self): self.closed=True
    decoded=Decoded()
    monkeypatch.setattr(media,'decode_image',lambda content:decoded)
    original=media.Image.open
    def open_header(*args,**kwargs):
        assert decoded.closed
        return original(*args,**kwargs)
    monkeypatch.setattr(media.Image,'open',open_header)
    assert media.inspect_media(data)['width']==9
