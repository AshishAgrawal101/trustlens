"""Add provenance evidence without changing the frozen image detector or training."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

from app.analyzers.image import analyze_image, decode_image, ImageModelUnavailable
from app.models import AnalysisReport, ContentCredentials, Evidence

PROJECT = Path(__file__).resolve().parents[2]
WORKER = Path(__file__).with_name('content_credentials_worker.py')


def credential_python() -> str | None:
    configured = os.environ.get('TRUSTLENS_CREDENTIALS_PYTHON')
    if configured: return configured if Path(configured).is_file() else None
    for candidate in (PROJECT/'.credentials-venv/Scripts/python.exe',
                      PROJECT.parent.parent/'work/credentials-venv/Scripts/python.exe',
                      PROJECT/'.credentials-venv/bin/python'):
        if candidate.is_file(): return str(candidate)
    return sys.executable if importlib.util.find_spec('c2pa') else None


def read_credentials(content: bytes) -> ContentCredentials:
    unavailable = ContentCredentials(status='unavailable', detail='Content Credentials verification is unavailable. No signed provenance was verified.')
    python = credential_python()
    if not python: return unavailable
    mime = 'image/png' if content.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if content.startswith(b'\xff\xd8') else 'image/webp'
    try:
        completed = subprocess.run([python, str(WORKER), mime], input=content, capture_output=True,
                                   timeout=15, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if completed.returncode or len(completed.stdout) > 16384: return unavailable
        return ContentCredentials.model_validate(json.loads(completed.stdout))
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return unavailable


def analyze_image_with_credentials(content: bytes) -> AnalysisReport:
    # Preserve the existing format, size and pixel limits before native parsing.
    image = decode_image(content)
    dimensions = image.size
    image.close()
    credentials = read_credentials(content)
    trusted = credentials.status == 'verified'
    if trusted and credentials.declaration == 'generated':
        signer = credentials.signer or 'A trusted signer'
        return AnalysisReport(kind='image', risk_index=None, risk_level='high', confidence='high',
            summary=f'{signer} signed this image and declared it AI-generated.',
            model_ran=False, decision_basis='content_credentials', content_credentials=credentials,
            evidence=[Evidence(id='image:credentials', evidence_class='verified', severity='info',
                title='Signed AI-generation declaration', detail=credentials.detail,
                source='C2PA manifest and local trust-list snapshot'),
                Evidence(id='image:decoded', evidence_class='verified', severity='info',
                title='Image decoded locally', detail=f'{dimensions[0]} × {dimensions[1]} pixels.', source='Uploaded image')],
            limitations=['Content Credentials verify who signed these statements and bind them to this file; they do not independently prove every statement is true.',
                         'The detector was not run because a trusted, asset-bound manifest explicitly declares AI generation.',
                         'Verification uses local trust-list snapshots. Remote manifests and live certificate-revocation lookups are not fetched.'])
    try:
        report = analyze_image(content)
        report.model_ran = True
    except ImageModelUnavailable:
        missing_credentials = credentials.status == 'unavailable'
        report = AnalysisReport(kind='image', risk_index=None, risk_level='low', confidence='low',
            summary=('Image checks unavailable. Neither the detector nor Content Credentials verification produced a result. Check any accompanying message in Message mode, or use the optional image setup in README.md.'
                     if missing_credentials else 'Image detector unavailable. Only the Content Credentials check is shown.'),
            evidence=[], limitations=[
                'Configure the optional image model and Content Credentials verifier using README.md, or paste any accompanying message in Message mode. No image-origin conclusion was produced.'
                if missing_credentials else 'Configure the local image weights and Python environment using the README. No model decision was produced.'],
            model_ran=False, decision_basis='content_credentials')
    report.content_credentials = credentials
    report.evidence.append(Evidence(id='image:credentials', evidence_class='verified' if trusted else 'unknown',
        severity='medium' if credentials.status == 'invalid' else 'info', title='C2PA Content Credentials',
        detail=credentials.detail, source='Embedded Content Credentials check'))
    if trusted:
        report.evidence = [item for item in report.evidence if item.id != 'image:origin']
        report.limitations.append('A trusted signature authenticates the signed declaration, not the truth of everything shown in the image.')
    return report
