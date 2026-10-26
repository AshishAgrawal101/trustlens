"""Cheap configuration checks, deliberately distinct from a successful analysis."""
import importlib.util
import os
from pathlib import Path

from app.analyzers.provenance import credential_python

ROOT = Path(__file__).resolve().parents[1]


def configured_capabilities():
    cache = Path(os.environ.get('TRUSTLENS_CLIP_CACHE', str(ROOT.parent.parent / 'work/clip-weights')))
    community = Path(os.environ.get('TRUSTLENS_COMMUNITY_WEIGHTS', str(ROOT.parent.parent / 'work/community-forensics/model.safetensors')))
    try:
        image = ((ROOT / 'models/image_pipeline.json').is_file()
                 and community.is_file() and any(cache.rglob('open_clip_model.safetensors'))
                 and all(importlib.util.find_spec(name) is not None for name in ('torch', 'open_clip', 'timm', 'joblib')))
    except OSError:
        image = False
    powershell = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    ocr = os.name == 'nt' and powershell.is_file() and (ROOT / 'app/ocr_worker.ps1').is_file()
    return {
        'message_rules': True,
        'qr_reader': {'configured': importlib.util.find_spec('cv2') is not None, 'detail': 'OpenCV is installed; successful decoding is checked only when you read a QR image. No destination is opened.' if importlib.util.find_spec('cv2') is not None else 'Optional OpenCV is not installed in this Python environment. Paste the printed address instead.'},
        'screenshot_ocr': {'configured': ocr, 'detail': 'Windows OCR worker is configured; installed English language support and recognition are checked only when you read a screenshot.' if ocr else 'Windows OCR is not configured here. Paste or type the message instead.'},
        'image_detector': {'configured': bool(image), 'detail': 'Local assets and Python dependencies were found; model loading, integrity and inference have not been verified by this check.' if image else 'Required local image assets or dependencies were not found. Message and link checks still work.'},
        'content_credentials': {'configured': credential_python() is not None, 'detail': 'Verifier configuration only; a file must be checked before any provenance result is available.'},
        'notice': 'Configuration is not readiness, accuracy or verification of a file. No model was loaded and no content was sent.'
    }
