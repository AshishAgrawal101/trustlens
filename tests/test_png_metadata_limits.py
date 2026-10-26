"""Pillow's small compressed-metadata rejection must remain an input error."""
import io
import struct
import subprocess
import zlib

from PIL import Image, PngImagePlugin
import pytest

from app.analyzers import image, qr, screenshot
from test_community import request


def image_bytes(format='PNG'):
    output=io.BytesIO()
    Image.new('RGB',(1,1),'white').save(output,format=format)
    return output.getvalue()


def metadata_limit_png():
    data=image_bytes()
    payload=b'keyword\0\0'+zlib.compress(b'A'*(PngImagePlugin.MAX_TEXT_CHUNK+1))
    chunk=b'zTXt'+payload
    chunk=struct.pack('>I',len(payload))+chunk+struct.pack('>I',zlib.crc32(chunk)&0xffffffff)
    result=data[:33]+chunk+data[33:]
    assert len(result)<2048
    return result


def test_compressed_metadata_value_error_is_normalized_without_raising_pillow_limits():
    limit=PngImagePlugin.MAX_TEXT_CHUNK
    with pytest.raises(image.InvalidImage,match='could not be read') as error:
        image.decode_image(metadata_limit_png())
    assert isinstance(error.value.__cause__,ValueError)
    assert 'MAX_TEXT_CHUNK' in str(error.value.__cause__)
    assert PngImagePlugin.MAX_TEXT_CHUNK==limit


@pytest.mark.parametrize('path',['/api/analyze/image','/api/extract/screenshot','/api/extract/qr'])
def test_metadata_limit_routes_return_400_without_runtime_or_worker(path,monkeypatch):
    content=metadata_limit_png()
    def forbidden(*_,**__): pytest.fail('Malformed input invoked a visual model or worker')
    monkeypatch.setattr(image,'load_runtime',forbidden)
    monkeypatch.setattr(subprocess,'Popen',forbidden)
    response=request('POST',path,files={'file':('tiny.png',content,'image/png')})
    assert response.status_code==400,response.text
    assert response.json()=={'detail':'This file could not be read as an image.'}
    assert not qr._lock.locked() and not screenshot._lock.locked()


@pytest.mark.parametrize('content,message',[
    (b'','smaller than 64 MB'),
    (image_bytes('BMP'),'JPEG, PNG, or WebP'),
])
def test_existing_explicit_invalid_image_messages_are_preserved(content,message):
    with pytest.raises(image.InvalidImage,match=message): image.decode_image(content)


def test_existing_pixel_bound_and_normal_decoding_are_preserved(monkeypatch):
    content=image_bytes()
    with image.decode_image(content) as decoded:
        assert decoded.size==(1,1) and decoded.mode=='RGB'
    monkeypatch.setattr(image,'MAX_PIXELS',0)
    with pytest.raises(image.InvalidImage,match='20 million pixels'):
        image.decode_image(content)
