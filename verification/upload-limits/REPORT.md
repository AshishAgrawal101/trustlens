# Upload body limits before multipart spooling

app/upload_limits.py exports UploadLimitMiddleware. Root registered it after defining privacy_headers, making this pure ASGI limiter the outermost user middleware. It applies only to POST /api/analyze/image, /api/extract/screenshot and /api/extract/qr (64 MiB + 64 KiB total body each), and POST /api/analyze/email-file (512 KiB total body). Endpoint limits remain separate and stricter for actual file bytes.

Valid oversized Content-Length rejects immediately, without receiving body bytes, invoking the inner app or starting multipart spooling. Otherwise the middleware counts each streamed http.request chunk, forwards accepted chunks unchanged, and raises HTTPException at the first excess without forwarding that chunk or reading the remainder. It never assembles the body in memory. Invalid, missing or understated length headers do not disable streamed counting. A downstream receive retry after overflow is rejected without another read.

The fixed JSON 413 contains no input data and includes no-store, nosniff, no-referrer and a restrictive JSON-appropriate CSP. A downstream custom error response cannot replace that fixed error with success or echo input. Unrelated app exceptions still propagate normally. No input logging or analyzer callback was added.

Actual upload routes complete multipart parsing before sending a response, so oversized streamed bodies return 413 before any analysis. If an unrelated ASGI app starts its response before consuming an upload, ASGI cannot change the already-sent status; the limiter safely ends its body without sending a second response start. That edge is tested and is not represented as retroactive status replacement.

Installed Starlette 1.7.0 MultiPartParser.parse was inspected: its `except BaseException` closes all partial files before reraising a read failure. Tests force a multipart file to roll onto disk after an accepted prefix, then cross the bound on the next chunk. With live file references still retained, every file is immediately rolled and closed; cleanup does not depend on garbage collection. Both absent and understated Content-Length paths were checked. This installed-runtime behavior is covered by regressions rather than assumed for arbitrary dependency versions.

27 dedicated upload-limit checks passed; combined with file-intake tests, 61 passed in 5.82 seconds. They cover all configured paths, exact limits, very long/zero-padded length headers, chunked and inaccurate lengths, normal file delivery and privacy headers through the actual main app, no analysis of partial input, early rejection before spooling, disk-rollover cleanup, no additional reads after overflow, response-started handling, and unchanged non-upload/non-HTTP scopes. Product worker independently reviewed the installed parser cleanup and middleware tests without finding another issue.

Skipped: proxy/server-wide body limits, unrelated API limits and a general resource framework.
Risk: the server may allocate one incoming ASGI chunk before the limiter sees it; multipart can spool the permitted prefix, but cannot receive the over-limit chunk through this middleware.
