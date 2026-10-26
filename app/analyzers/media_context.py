"""Allowlisted, editable image metadata; never an image-origin or truth verdict."""
from datetime import datetime
import io
import re
import threading
import warnings

from PIL import Image
from app.analyzers.image import decode_image

_lock = threading.Lock()


class MediaUnavailable(RuntimeError):
    pass

NOTICE = ('Metadata can be edited or removed. Its presence or absence proves neither '
          'authenticity nor AI origin. These fields do not verify the depicted story, '
          'capture date or location. No sources were visited.')


def _text(value, limit):
    if not isinstance(value, str) or len(value) > limit or not value or not value.isprintable():
        return None
    return value.strip() or None


def _time(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}', value):
        return None
    try:
        datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except ValueError:
        return None
    return value


def inspect_media(content):
    if not _lock.acquire(blocking=False):
        raise MediaUnavailable('Another media inspection is running. Wait a moment, then try again.')
    try:
        return _inspect_media(content)
    finally:
        _lock.release()


def _inspect_media(content):
    # Shared format/byte/pixel/decompression validation, with no model loading.
    decoded = decode_image(content)
    display_width, display_height = decoded.size
    decoded.close()
    with Image.open(io.BytesIO(content)) as image:
        result = dict(format=image.format, width=image.width, height=image.height,
                      display_width=display_width, display_height=display_height,
                      bytes=len(content), capture_time=None, software=None,
                      camera_make=None, camera_model=None, gps_present=False,
                      notice=NOTICE)
        # Optional EXIF failures do not invalidate an already validated image.
        # Do not enumerate tags or access GPS IFD, thumbnail or maker-note bytes.
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                exif = image.getexif()
                result['gps_present'] = 34853 in exif
                for name, tag, limit in [('software',305,120),('camera_make',271,80),('camera_model',272,80)]:
                    result[name] = _text(exif.get(tag), limit)
                try:
                    original = exif.get_ifd(34665).get(36867)
                except Exception:
                    original = None
                result['capture_time'] = _time(original)
        except Exception:
            pass
    return result
