import io,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from app.analyzers.qr import extract_qr
from app.analyzers.image import decode_image
matrix=cv2.QRCodeEncoder_create().encode('TRUSTLENS SAFE LOCAL TEST');matrix=np.pad(matrix,4,constant_values=255);mask=Image.fromarray(matrix).resize((matrix.shape[1]*8,matrix.shape[0]*8),Image.Resampling.NEAREST)
transparent=Image.new('RGBA',mask.size,(0,0,0,0));transparent.putalpha(mask.point(lambda p:255 if p==0 else 0));white=Image.new('RGBA',mask.size,'white');white.alpha_composite(transparent);results={}
for label,image in [('transparent',transparent),('white_reference',white.convert('RGB'))]:
 stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue();decoded=decode_image(raw)
 result={'bytes':len(raw),'dimensions':decoded.size,'decoded_extrema':decoded.getextrema()};decoded.close()
 try:result['qr']=extract_qr(raw)
 except Exception as e:result['error']={'type':type(e).__name__,'detail':str(e)}
 results[label]=result
Path('verification/media-v41-20261025/after-native-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))

