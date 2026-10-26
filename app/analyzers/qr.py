"""Extract QR text locally for review; never visit or analyze a destination."""
import json
from contextlib import closing
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unicodedata

from app.analyzers.image import InvalidImage
from app.analyzers.qr_pixels import decode_qr_image as decode_image

MAX_QR_TEXT = 30000
MAX_QR_CODES = 16
_lock = threading.Lock()


class QrUnavailable(RuntimeError):
    pass


def extract_qr(content: bytes) -> dict:
    if not _lock.acquire(blocking=False):
        raise QrUnavailable('Another QR image is being read. Wait a moment, then try again.')
    try:
        with closing(decode_image(content)) as image:
            # shortcut: small codes may be lost when large photos are reduced; crop the code and retry.
            image.thumbnail((3000, 3000))
            with tempfile.TemporaryDirectory(prefix='trustlens-qr-') as directory:
                path = Path(directory)/'qr.png'
                with closing(image.convert('L')) as grayscale:
                    grayscale.save(path, format='PNG')
                completed = subprocess.run([sys._base_executable, '-S', '-B',
                    str(Path(__file__).with_name('qr_worker.py')), str(path), sys.prefix],
                    capture_output=True, timeout=15, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                if completed.returncode or len(completed.stdout)>200000:
                    raise QrUnavailable('The local QR reader is unavailable. Install the optional OpenCV dependency in this Python environment, or paste the printed address instead.')
                data = json.loads(completed.stdout)
        if data.get('too_large'):
            raise InvalidImage('Too many QR codes or too much decoded text. Crop to one code and try again.')
        codes = data['codes']
        if not isinstance(codes, list) or any(not isinstance(code, str) for code in codes):
            raise ValueError('Invalid QR reader response')
        codes = list(dict.fromkeys(code for code in codes if code.strip()))
        text = '\n'.join(codes)
        if any((unicodedata.category(c)=='Cc' and c not in '\r\n\t') or c in '\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069' for c in text):
            raise InvalidImage('The QR code contains hidden control characters. Type the printed address or message instead.')
        if len(codes)>MAX_QR_CODES or len(text)>MAX_QR_TEXT:
            raise InvalidImage('Too many QR codes or too much decoded text. Crop to one code and try again.')
        if not codes:
            raise InvalidImage('No readable QR code was found. Try a clear, close crop, or type the printed address.')
        # JSON can encode lone surrogates which cannot become a UTF-8 response.
        text.encode('utf-8')
        return {'text': text, 'codes': codes, 'review_required': True,
            'notice': 'Transparent images are read against white. Review each decoded value before checking it. QR decoding can miss codes. No address was opened and this does not verify who created the code.'}
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError, AttributeError) as exc:
        if isinstance(exc, InvalidImage):
            raise
        raise QrUnavailable('QR reading is unavailable or timed out. Try a clear crop, or paste the printed address instead.') from exc
    finally:
        _lock.release()
