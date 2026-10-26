# Local media context

Add a distinct image-metadata/context workspace: bounded local upload, explicit inspection, allowlisted format/dimensions/capture-clock/software/camera fields and GPS presence only. Never expose coordinates, raw metadata, filenames or serials in backend output; never infer AI origin, authenticity, location or story truth from metadata. An optional caption stays in the page and is not uploaded or parsed.

Reuse image intake limits and decoding, but do not load a detector or C2PA worker. Preserve every earlier model/runtime/benchmark artifact. Test constructed JPEG/PNG/WebP/EXIF, malformed metadata, privacy allowlists, streamed body bounds, UI cancellation/stale results/clear/source release and field validation. Use permitted browser page checks; file-upload denial remains respected. Freeze new semantic acceptance before predictions, independent review and a separately tested v12 package.
