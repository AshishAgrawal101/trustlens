"""Frozen tiny generated metadata diagnostic; no model or external assets."""
import io,json,struct,hashlib,warnings
from pathlib import Path
from PIL import Image
from app.analyzers.media_context import inspect_media
HERE=Path(__file__).resolve().parent
def image(exif=None):
    b=io.BytesIO();Image.new('RGB',(2,3)).save(b,format='PNG',**({'exif':exif} if exif is not None else {}));return b.getvalue()
def tags(values):
    e=Image.Exif()
    for k,v in values.items():e[k]=v
    return image(e)
def raw(tag,kind,count,value,extra=b''):
    return image(b'Exif\0\0II'+struct.pack('<HIH',42,8,1)+struct.pack('<HHI',tag,kind,count)+value+struct.pack('<I',0)+extra)
cases=[('plain_png',image()),('truncated_png_12bytes',image()[:12]),('software_120',tags({305:'x'*120})),('software_121',tags({305:'x'*121})),('software_bidi',tags({305:'Editor\u202e'})),('valid_leap_time',tags({34665:{36867:'2024:02:29 12:00:00'}})),('invalid_leap_time',tags({34665:{36867:'2026:02:29 12:00:00'}})),('empty_GPS_IFD',tags({34853:{}})),('orientation6_GPS',tags({274:6,34853:{1:'N',2:(1,2,3)}})),('raw_EXIF_orientation_ASCII',raw(274,2,4,b'bad\0')),('raw_EXIF_orientation_rational',raw(274,5,1,struct.pack('<I',26),struct.pack('<II',0,0))),('raw_EXIF_orientation_short_tuple',raw(274,3,2,struct.pack('<HH',6,8))),('raw_EXIF_GPS_invalid_offset',raw(34853,4,1,struct.pack('<I',999999))),('raw_EXIF_ExifIFD_invalid_offset',raw(34665,4,1,struct.pack('<I',999999))),('raw_EXIF_make_invalid_offset',raw(271,2,80,struct.pack('<I',999999)))]
assert [n for n,b in cases]==json.loads((HERE/'protocol.json').read_text())['cases']
rows=[]
for name,data in cases:
    assert len(data)<10000
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:r={'result':inspect_media(data)}
        except Exception as e:r={'error_type':type(e).__name__,'error':str(e)}
    rows.append({'id':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'warnings':[str(x.message) for x in caught],**r})
(HERE/'results.json').write_text(json.dumps({'protocol_sha256':hashlib.sha256((HERE/'protocol.json').read_bytes()).hexdigest(),'rows':rows},indent=2)+'\n')
print(json.dumps([{'id':r['id'],'error':r.get('error_type'),'capture_time':r.get('result',{}).get('capture_time'),'gps':r.get('result',{}).get('gps_present')} for r in rows],indent=2))
