"""Bounded local file intake; extracted QR content always needs user review."""
from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.analyzers.email import analyze_email_bytes, MAX_EMAIL_BYTES
from app.analyzers.image import InvalidImage, MAX_UPLOAD_BYTES
from app.analyzers.qr import extract_qr, QrUnavailable
from app.analyzers.media_context import inspect_media, MediaUnavailable
from app.guidance import add_guidance
from app.models import AnalysisReport

router = APIRouter()


@router.post('/api/inspect/media')
async def media_context_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read(MAX_UPLOAD_BYTES+1)
    finally:
        await file.close()
    try:
        return await run_in_threadpool(inspect_media, content)
    except InvalidImage as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except MediaUnavailable as exc:
        raise HTTPException(503, detail=str(exc)) from exc


@router.post('/api/extract/qr')
async def qr_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read(MAX_UPLOAD_BYTES+1)
    finally:
        await file.close()
    try:
        return await run_in_threadpool(extract_qr, content)
    except InvalidImage as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except QrUnavailable as exc:
        raise HTTPException(503, detail=str(exc)) from exc


@router.post('/api/analyze/email-file', response_model=AnalysisReport)
async def email_file_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read(MAX_EMAIL_BYTES+1)
    finally:
        await file.close()
    try:
        return add_guidance(await run_in_threadpool(analyze_email_bytes, content))
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
