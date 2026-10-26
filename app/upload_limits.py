"""Limit streamed upload bodies before multipart parsing can spool them."""
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

IMAGE_BODY_LIMIT = 64*1024*1024 + 64*1024
EMAIL_BODY_LIMIT = 512*1024
UPLOAD_LIMITS = {
    '/api/analyze/image': IMAGE_BODY_LIMIT,
    '/api/extract/screenshot': IMAGE_BODY_LIMIT,
    '/api/extract/qr': IMAGE_BODY_LIMIT,
    '/api/inspect/media': IMAGE_BODY_LIMIT,
    '/api/analyze/email-file': EMAIL_BODY_LIMIT,
}
DETAIL = 'This upload is too large. Choose a smaller file and try again.'


class UploadLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        limit = UPLOAD_LIMITS.get(scope.get('path'))
        if scope['type']!='http' or scope.get('method')!='POST' or limit is None:
            return await self.app(scope, receive, send)
        response = JSONResponse({'detail': DETAIL}, status_code=413, headers={
            'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
            'Referrer-Policy': 'no-referrer',
            'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
        })
        for name, value in scope.get('headers', []):
            if name.lower()==b'content-length':
                value = value.strip()
                if value.isdigit():
                    value = value.lstrip(b'0') or b'0'
                    if len(value)>len(str(limit)) or int(value)>limit:
                        return await response(scope, receive, send)
        consumed = 0
        exceeded = started = finished = False

        async def reject():
            nonlocal started, finished
            if not started:
                started = finished = True
                await response(scope, receive, send)
            elif not finished:
                # ASGI cannot replace a response already sent; end it without a second start.
                finished = True
                await send({'type': 'http.response.body', 'body': b'', 'more_body': False})

        async def bounded_receive():
            nonlocal consumed, exceeded
            if exceeded:
                raise HTTPException(413, detail=DETAIL)
            message = await receive()
            if message['type']=='http.request':
                consumed += len(message.get('body', b''))
                if consumed>limit:
                    exceeded = True
                    # FastAPI preserves HTTPException and Starlette closes partial multipart files.
                    raise HTTPException(413, detail=DETAIL)
            return message

        async def bounded_send(message):
            nonlocal started, finished
            if exceeded:
                await reject()
                return
            if message['type']=='http.response.start':
                started = True
            elif message['type']=='http.response.body' and not message.get('more_body', False):
                finished = True
            await send(message)

        try:
            await self.app(scope, bounded_receive, bounded_send)
        except Exception:
            if not exceeded:
                raise
            await reject()
        else:
            if exceeded:
                await reject()
