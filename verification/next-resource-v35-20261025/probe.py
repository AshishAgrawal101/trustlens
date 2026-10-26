import io,threading,json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
from app.analyzers import media_context as media
b=io.BytesIO();Image.new('RGB',(1,1)).save(b,format='PNG');content=b.getvalue()
actual=media.decode_image;barrier=threading.Barrier(2);lock=threading.Lock();live=0;peak=0
class Held:
 def __init__(self,image):self.image=image;self.size=image.size
 def close(self):
  global live
  self.image.close()
  with lock:live-=1
def wrapped(data):
 global live,peak
 image=actual(data)
 with lock:live+=1;peak=max(peak,live)
 try:barrier.wait(timeout=2)
 except BaseException:image.close();raise
 return Held(image)
media.decode_image=wrapped
try:
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(media.inspect_media,[content,content]))
finally:media.decode_image=actual
r={'concurrent_decoded_rgb_peak':peak,'remaining_owned_images':live,'reports':len(results),'dimensions':[[r['width'],r['height']] for r in results],'input_bytes':len(content),'no_model_execution':True}
Path('verification/next-resource-v35-20261025/results.json').write_text(json.dumps(r,indent=2));print(r)
