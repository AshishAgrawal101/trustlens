import io,json,time,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from app.analyzers.screenshot import extract_screenshot
font_path=Path('C:/Windows/Fonts/arial.ttf');font=ImageFont.truetype(str(font_path),44);phrase='Send me your verification code.';inputs=[]
for name,color,bg in [('black_transparent','black','white'),('white_transparent','white','black')]:
 source=Image.new('RGBA',(900,150),(0,0,0,0));ImageDraw.Draw(source).text((20,40),phrase,font=font,fill=color)
 reference=Image.new('RGBA',source.size,bg);reference.alpha_composite(source)
 inputs.extend([(name,source),(name+'_opaque_reference',reference.convert('RGB'))])
results=[]
for name,image in inputs:
 data=io.BytesIO();image.save(data,format='PNG');raw=data.getvalue();start=time.perf_counter();entry={'case':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 try:entry['output']=extract_screenshot(raw)
 except Exception as e:entry['error']={'type':type(e).__name__,'detail':str(e)}
 entry['seconds']=time.perf_counter()-start;results.append(entry)
Path('verification/ocr-transparency-v42-20261025/results.json').write_text(json.dumps({'font_sha256':hashlib.sha256(font_path.read_bytes()).hexdigest(),'results':results},indent=2));print(json.dumps(results))
