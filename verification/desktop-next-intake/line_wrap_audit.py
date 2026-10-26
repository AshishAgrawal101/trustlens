"""Paired constructed native OCR layout check; no model inference or source edits."""
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PIL import Image,ImageDraw,ImageFont
from app.analyzers.screenshot import extract_screenshot
from app.analyzers.text import analyze_text
from app.analyzers import image as visual


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def forbidden(*_,**__):raise AssertionError('Visual image model must not run')
visual.load_runtime=forbidden


def main():
    protocol=HERE/'line-wrap-protocol.json'
    assert not protocol.exists() and not (HERE/'line-wrap-results.json').exists(),'No automatic replay'
    cases=[]
    for name,text in [('single_line','Send us the verification code.'),('wrapped_line','Send us the\nverification code.')]:
        canvas=Image.new('RGB',(900,200),'white')
        font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',44)
        ImageDraw.Draw(canvas).multiline_text((30,30),text,font=font,fill='black',spacing=14)
        path=HERE/(name+'.png');canvas.save(path)
        cases.append({'id':name,'image':str(path),'sha256':sha(path),'constructed_text':text,'expected_request_warning':True})
    files=['app/analyzers/screenshot.py','app/ocr_worker.ps1','app/analyzers/text.py','app/analyzers/image.py']
    pins=[{'path':str(ROOT/p),'sha256':sha(ROOT/p)} for p in files]
    save(protocol,{'frozen_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Same constructed sentence, line layout only; native OCR and downstream rules, not scam accuracy','cases':cases,'source_pins':pins,'budget':{'native_OCR_calls':2,'seconds_each':30,'image_pixels_each':180000,'model':False,'GPU':False,'downloads':False},'original_source_or_archive_edits':False})
    records=[]
    for case in cases:
        began=time.perf_counter()
        try:
            extracted=extract_screenshot(Path(case['image']).read_bytes())
            report=analyze_text(extracted['text'])
            records.append({'id':case['id'],'elapsed_seconds':time.perf_counter()-began,'extracted':extracted,'risk_level':report.risk_level,'summary':report.summary,'evidence_ids':[e.id for e in report.evidence],'request_warning':any(e.id=='request:code' for e in report.evidence)})
        except Exception as exc:
            records.append({'id':case['id'],'elapsed_seconds':time.perf_counter()-began,'exception':type(exc).__name__,'message':str(exc)})
    assert all(sha(pin['path'])==pin['sha256'] for pin in pins)
    out={'verified_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(protocol),'records':records,'source_pins_unchanged':True,'source_edits':False,'visual_model_calls':False,'GPU':False,'downloads':False}
    save(HERE/'line-wrap-results.json',out)
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
