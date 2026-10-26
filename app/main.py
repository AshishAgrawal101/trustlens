from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from starlette.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.analyzers.email import analyze_email
from app.analyzers.text import analyze_text
from app.analyzers.url import analyze_url
from app.analyzers.image import analyze_image, InvalidImage, ImageModelUnavailable, MAX_UPLOAD_BYTES
from app.analyzers.provenance import analyze_image_with_credentials
from app.models import AnalysisReport, EmailRequest, TextRequest, UrlRequest, CallRequest
from app.guidance import add_guidance, RECOVERY_PLANS
from app.analyzers.screenshot import extract_screenshot, OcrUnavailable
from frontend import render_frontend
from app.capabilities import configured_capabilities
from app.intake import router as intake_router
from app.upload_limits import UploadLimitMiddleware
from app.analyzers.url_details import inspect_url
from app.pocket_workspaces import render_pocket_workspace, render_desktop_context

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="TrustLens Community", version="1.0.0")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', '[::1]'])
app.include_router(intake_router)


@app.exception_handler(RequestValidationError)
async def private_validation_error(request, error):
    return JSONResponse({'detail':'Check the required fields, input format and length, then try again.'}, status_code=422)


@app.middleware('http')
async def privacy_headers(request, call_next):
    origin = request.headers.get('origin')
    if request.method == 'POST' and origin and origin != str(request.base_url).rstrip('/'):
        return JSONResponse({'detail': 'Use the checker on its own local page.'}, status_code=403)
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    return response


app.add_middleware(UploadLimitMiddleware)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get('/api/capabilities')
def capabilities():
    return configured_capabilities()


@app.post('/phone/share')
def phone_share_not_installed():
    return HTMLResponse('Open the phone companion and prepare offline access before sharing. Your shared text was not analyzed or saved.', status_code=409)


@app.get('/context-guide.html', response_class=HTMLResponse)
def desktop_context_guide():
    return HTMLResponse(render_desktop_context(), headers={'Cache-Control': 'no-store'})


@app.get('/phone/workspace/{tool}.html', response_class=HTMLResponse)
def pocket_workspace(tool: str):
    try:
        return HTMLResponse(render_pocket_workspace(tool))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Unknown Pocket workspace.') from exc


app.mount('/phone', StaticFiles(directory=STATIC / 'phone', html=True), name='phone')


@app.get('/api/recovery')
def recovery_guide():
    return {'plans': RECOVERY_PLANS,
            'source': 'https://consumer.ftc.gov/articles/what-do-if-you-were-scammed',
            'notice': 'General U.S. guidance, not a recovery service. If someone is in immediate danger, contact local emergency services.'}


@app.post("/api/analyze/text", response_model=AnalysisReport)
def analyze_text_endpoint(request: TextRequest) -> AnalysisReport:
    return add_guidance(analyze_text(request.text))


@app.post('/api/analyze/call', response_model=AnalysisReport)
def analyze_call_endpoint(request: CallRequest) -> AnalysisReport:
    return add_guidance(analyze_text(request.transcript, 'call'))


@app.post("/api/analyze/url", response_model=AnalysisReport)
def analyze_url_endpoint(request: UrlRequest) -> AnalysisReport:
    try:
        return add_guidance(analyze_url(request.url, request.claimed_brand, request.known_website))
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@app.post('/api/inspect/url')
def inspect_url_endpoint(request: UrlRequest):
    try:
        return inspect_url(request.url, request.known_website)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@app.post("/api/analyze/email", response_model=AnalysisReport)
def analyze_email_endpoint(request: EmailRequest) -> AnalysisReport:
    try:
        return add_guidance(analyze_email(request.raw_email))
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.post('/api/analyze/image', response_model=AnalysisReport)
async def analyze_image_endpoint(file: UploadFile = File(...)) -> AnalysisReport:
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()
    try:
        return add_guidance(await run_in_threadpool(analyze_image_with_credentials, content))
    except InvalidImage as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImageModelUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(render_frontend(), headers={'Cache-Control': 'no-store'})


@app.post('/api/extract/screenshot')
async def screenshot_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()
    try:
        return await run_in_threadpool(extract_screenshot, content)
    except InvalidImage as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except OcrUnavailable as exc:
        raise HTTPException(503, detail=str(exc)) from exc
