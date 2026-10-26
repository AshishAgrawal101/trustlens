"""Temporary loopback browser fault injection, no analysis or private inputs."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from frontend import render_frontend,STATIC
from app.guidance import RECOVERY_PLANS
import uvicorn
app=FastAPI()
count=0
@app.get('/',response_class=HTMLResponse)
def index():return HTMLResponse(render_frontend(),headers={'Cache-Control':'no-store'})
@app.get('/api/recovery')
def recovery():
 global count
 count+=1
 print('RECOVERY_REQUEST '+str(count),flush=True)
 return {'plans':[] if count==1 else RECOVERY_PLANS}
app.mount('/static',StaticFiles(directory=STATIC),name='static')
if __name__=='__main__':uvicorn.run(app,host='127.0.0.1',port=8767)
