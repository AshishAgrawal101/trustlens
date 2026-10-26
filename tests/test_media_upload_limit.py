"""The metadata route must be bounded before multipart parsing, not just after upload."""
import pytest
from app.upload_limits import UPLOAD_LIMITS, IMAGE_BODY_LIMIT, UploadLimitMiddleware
from test_upload_limits import scope, invoke, result


def test_media_oversize_header_rejected_before_parser_or_body_read():
    assert UPLOAD_LIMITS['/api/inspect/media'] == IMAGE_BODY_LIMIT
    async def forbidden(*_): pytest.fail('The parser must not run')
    sent, reads = invoke(UploadLimitMiddleware(forbidden), scope('/api/inspect/media', [(b'content-length', str(IMAGE_BODY_LIMIT+1).encode())]), [b'private'])
    assert result(sent)[0] == 413 and reads == 0
