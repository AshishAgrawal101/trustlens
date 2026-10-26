"""Local OCR only; recognized text must be reviewed before request analysis."""
import json
from contextlib import closing
import os
from pathlib import Path
import subprocess
import tempfile
import threading

from app.analyzers.image import decode_image, InvalidImage

_lock = threading.Lock()


class OcrUnavailable(RuntimeError):
    pass


def extract_screenshot(content: bytes) -> dict:
    if os.name != 'nt':
        raise OcrUnavailable('Screenshot reading needs Windows with English OCR installed. Paste or type the message instead.')
    if not _lock.acquire(blocking=False):
        raise OcrUnavailable('Another screenshot is being read. Wait a moment, then try again.')
    try:
        with closing(decode_image(content)) as image:
            # shortcut: very small text may be lost in large images; crop to the message or paste it manually.
            image.thumbnail((3000, 3000))
            with tempfile.TemporaryDirectory(prefix='trustlens-ocr-') as directory:
                path = Path(directory) / 'screenshot.png'
                image.save(path, format='PNG')
                powershell = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
                result = subprocess.run([str(powershell), '-NoProfile', '-NonInteractive', '-File',
                    str(Path(__file__).resolve().parents[1] / 'ocr_worker.ps1'), '-ImagePath', str(path)],
                    capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode:
                    raise OcrUnavailable('Windows could not read the screenshot. Make sure English OCR is installed, or paste the message instead.')
                data = json.loads(result.stdout.decode('utf-8-sig'))
        if not isinstance(data, dict) or data.get('language') != 'en-US':
            raise OcrUnavailable('Screenshot reading is unavailable or timed out. Paste or type the message instead.')
        text = data.get('text')
        if not isinstance(text, str) or len(text) > 30000:
            raise OcrUnavailable('Too much text was found. Crop to the message you want to check, or paste it instead.')
        # Reject malformed worker strings before HTTP response serialization.
        text.encode('utf-8')
        return {'text': text, 'language': 'en-US', 'review_required': True,
            'notice': 'Review and correct the text before checking it. OCR may miss words, punctuation or links. This does not check image origin.'}
    except InvalidImage:
        raise
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
        raise OcrUnavailable('Screenshot reading is unavailable or timed out. Paste or type the message instead.') from exc
    finally:
        _lock.release()
