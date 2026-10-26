"""Read-only source audit: tiny PNG metadata guard failure, no model/worker calls."""
import asyncio
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import zlib

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PIL import Image, PngImagePlugin
import PIL
import httpx
from app.main import app
from app.analyzers import image, qr, screenshot


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def forbidden(*_,**__): raise AssertionError('A visual model or subprocess must not run')
image.load_runtime=forbidden
subprocess.Popen=forbidden


def fixture():
    original=io.BytesIO()
    Image.new('RGB',(1,1),'white').save(original,format='PNG')
    compressed=zlib.compress(b'A'*(PngImagePlugin.MAX_TEXT_CHUNK+1))
    payload=b'keyword\0\0'+compressed
    chunk=b'zTXt'+payload
    chunk=struct.pack('>I',len(payload))+chunk+struct.pack('>I',zlib.crc32(chunk)&0xffffffff)
    data=original.getvalue()
    return data[:33]+chunk+data[33:]


async def main():
    content=fixture()
    assert len(content)<2048
    records=[]
    try:
        image.decode_image(content)
    except Exception as exc:
        records.append({'component':'decode_image','exception_type':type(exc).__name__,'message':str(exc),'is_InvalidImage':isinstance(exc,image.InvalidImage)})
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://127.0.0.1') as client:
        for path in ('/api/analyze/image','/api/extract/screenshot','/api/extract/qr'):
            response=await client.post(path,files={'file':('constructed.png',content,'image/png')})
            records.append({'path':path,'status':response.status_code,'body':response.text})
    receipt={'verified_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'Pillow':PIL.__version__,
        'fixture':{'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'pixels':1,'compressed_text_expansion_bytes':PngImagePlugin.MAX_TEXT_CHUNK+1,'kind':'locally constructed PNG zTXt, no source/user/final assets'},
        'records':records,'QR_lock_released':not qr._lock.locked(),'OCR_lock_released':not screenshot._lock.locked(),
        'source_pins':[{'path':str(ROOT/path),'sha256':sha(ROOT/path)} for path in ('app/analyzers/image.py','app/analyzers/qr.py','app/analyzers/screenshot.py','app/intake.py','app/main.py')],
        'model_or_subprocess_calls':False,'GPU':False,'downloads':False,'production_source_edits':False}
    (HERE/'png-metadata-reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'fixture_bytes':len(content),'records':records,'source_edits':False},indent=2))


if __name__=='__main__': asyncio.run(main())
