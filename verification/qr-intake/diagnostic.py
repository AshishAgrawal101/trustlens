"""Freeze synthetic QR transforms, then report native decode behavior without tuning."""
import argparse
import ctypes as C
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
PROTOCOL=HERE/'protocol.json'
VALUES=['https://example.org/qr-review-only','Library meeting: bring your notes.']
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value): Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def freeze():
    assert not PROTOCOL.exists(),'Never replace the diagnostic freeze'
    import cv2
    import numpy as np
    from PIL import Image, ImageFilter, ImageDraw
    matrix=cv2.QRCodeEncoder_create().encode(VALUES[0])
    base=Image.fromarray(matrix).resize((matrix.shape[1]*10,matrix.shape[0]*10),Image.Resampling.NEAREST)
    padded=Image.new('L',(base.width+120,base.height+120),255)
    padded.paste(base,(60,60))
    cases=[]
    def add(name,image,expected,transform,format='PNG',**options):
        path=HERE/'fixtures'/(name+('.jpg' if format=='JPEG' else '.png'))
        path.parent.mkdir(exist_ok=True)
        image.save(path,format=format,**options)
        cases.append({'id':name,'path':str(path),'sha256':sha(path),'expected_codes':expected,'transform':transform})
    add('clean',padded,[VALUES[0]],'QR encoder default; 10x nearest scale; 60px white padding')
    add('rotate90',padded.rotate(90,expand=True,fillcolor=255),[VALUES[0]],'90 degree rotation')
    add('rotate17',padded.rotate(17,resample=Image.Resampling.BICUBIC,expand=True,fillcolor=255),[VALUES[0]],'17 degree bicubic rotation')
    add('halfsize',padded.resize((padded.width//2,padded.height//2),Image.Resampling.NEAREST),[VALUES[0]],'0.5 nearest scale')
    add('doublesize',padded.resize((padded.width*2,padded.height*2),Image.Resampling.NEAREST),[VALUES[0]],'2.0 nearest scale')
    add('blur1',padded.filter(ImageFilter.GaussianBlur(1)),[VALUES[0]],'Gaussian blur radius1')
    add('blur3',padded.filter(ImageFilter.GaussianBlur(3)),[VALUES[0]],'Gaussian blur radius3')
    array=np.array(padded)
    w,h=padded.size
    source=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    target=np.float32([[40,10],[w-45,35],[w-1,h-20],[5,h-1]])
    warped=cv2.warpPerspective(array,cv2.getPerspectiveTransform(source,target),(w,h),borderValue=255)
    add('perspective',Image.fromarray(warped),[VALUES[0]],'Corners(40,10),(w-45,35),(w-1,h-20),(5,h-1); linear warp, white border')
    add('jpeg45',padded,[VALUES[0]],'JPEG quality45',format='JPEG',quality=45)
    occluded=padded.copy()
    ImageDraw.Draw(occluded).rectangle((w*.4,h*.4,w*.6,h*.6),fill=255)
    add('center_occlusion',occluded,[VALUES[0]],'White rectangle covering central20% of image width/height')
    other=cv2.QRCodeEncoder_create().encode(VALUES[1])
    other=Image.fromarray(other).resize((other.shape[1]*10,other.shape[0]*10),Image.Resampling.NEAREST)
    multi=Image.new('L',(padded.width+other.width+180,max(padded.height,other.height)+120),255)
    multi.paste(padded,(0,30));multi.paste(other,(padded.width+60,60))
    add('multiple',multi,VALUES,'Two independently encoded QR payloads on white canvas')
    add('blank',Image.new('L',(400,400),255),[],'White blank negative fixture')
    admitted=json.loads((ROOT/'verification/professional-images/protocol.json').read_text())
    for item in admitted['cohort']:
        if item['label']==0:
            cases.append({'id':item['id'],'path':item['absolute_image_path'],'sha256':item['original_bytes_sha256'],'expected_codes':None,'transform':'Original admitted photograph; incidental QR presence not manually annotated','role':item['partition'],'license':item['dataset_license']})
    files=[ROOT/p for p in ('app/intake.py','app/analyzers/qr.py','app/analyzers/qr_worker.py','requirements-qr.txt')]+[Path(__file__)]
    cvroot=Path(cv2.__file__).parent
    files+=list(cvroot.glob('*.pyd'))
    files.append(cvroot.parent/'opencv_python_headless-5.0.0.93.dist-info/METADATA')
    save(PROTOCOL,{'at_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Native QR intake robustness only; no scam/origin accuracy or selection','payloads':VALUES,'cv2_version':cv2.__version__,'cases':cases,'code_pins':[{'path':str(p),'sha256':sha(p)} for p in files],'limits':{'timeout_seconds_each':15,'native_threads':1,'longest_side':3000,'codes':16,'text_chars':30000,'GPU':False,'network':False,'serial':True},'selection':'Transforms frozen before native results; retain failures, do not tune on them'})
    print('Frozen',sha(PROTOCOL),len(cases),'cases')


class Memory(C.Structure):
    _fields_=[('cb',C.c_ulong),('faults',C.c_ulong)]+[(n,C.c_size_t) for n in ('peak_ws','ws','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_private','private')]


def run():
    assert not (HERE/'results.json').exists(),'No diagnostic replay'
    protocol=json.loads(PROTOCOL.read_text())
    for p in protocol['code_pins']: assert sha(p['path'])==p['sha256']
    from app.analyzers import qr
    from app.analyzers.image import InvalidImage
    processes=[]
    popen=subprocess.Popen
    class Track(popen):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw)
            processes.append(self)
    subprocess.Popen=Track
    records=[]
    peak_worker={'peak_ws':0,'peak_private':0}
    kernel=C.WinDLL('kernel32',use_last_error=True) if sys.platform=='win32' else None
    if kernel:
        kernel.K32GetProcessMemoryInfo.argtypes=[C.c_void_p,C.c_void_p,C.c_ulong]
        kernel.K32GetProcessMemoryInfo.restype=C.c_int
    for case in protocol['cases']:
        assert sha(case['path'])==case['sha256']
        content=Path(case['path']).read_bytes()
        began=time.perf_counter()
        try:
            answer=qr.extract_qr(content)
            record={'status':'decoded','codes':answer['codes'],'review_required':answer['review_required']}
        except (InvalidImage,qr.QrUnavailable) as exc:
            record={'status':'no_decode' if isinstance(exc,InvalidImage) else 'unavailable','detail':str(exc),'codes':[]}
        record.update(id=case['id'],elapsed_seconds=time.perf_counter()-began,expected_codes=case['expected_codes'],matches_frozen_payloads=None if case['expected_codes'] is None else set(record['codes'])==set(case['expected_codes']))
        if processes:
            worker=processes[-1]
            record['worker_reaped']=worker.poll() is not None
            if kernel:
                mem=Memory();mem.cb=C.sizeof(mem)
                if kernel.K32GetProcessMemoryInfo(int(worker._handle),C.byref(mem),mem.cb):
                    record['worker_retained_memory']={'peak_ws':mem.peak_ws,'peak_private':mem.peak_private}
                    for key in peak_worker: peak_worker[key]=max(peak_worker[key],getattr(mem,key))
        records.append(record)
        save(HERE/'results.json',{'protocol_sha256':sha(PROTOCOL),'cases':records,'max_worker_retained_bytes':peak_worker,'aggregate_scam_or_origin_accuracy':None,'max_latency_seconds':max(r['elapsed_seconds'] for r in records)})
    print(json.dumps({'cases':len(records),'matched_labeled_cases':sum(r['matches_frozen_payloads'] is True for r in records),'failed_labeled_cases':[r['id'] for r in records if r['matches_frozen_payloads'] is False],'max_worker_retained_bytes':peak_worker,'max_latency_seconds':max(r['elapsed_seconds'] for r in records)},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['freeze','run'])
    args=parser.parse_args()
    (freeze if args.mode=='freeze' else run)()
