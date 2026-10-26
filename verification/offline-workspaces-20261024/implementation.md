# v18 Pocket workspace renderer implementation

Owned app changes only: app/pocket_workspaces.py and app/main.py. No source templates, controllers, math, models, CSS, worker, private input or historical archive were edited by this task.

Module exports PAGES closed claims/numbers/quotes map to existing template filenames; ASSETS tuple of eight explicit /static CSS/JS dependencies; render_pocket_workspace(tool,static_dir=STATIC) returning saved-template HTML. static_dir is trusted server/export configuration, not request input. Unknown/non-string key fails with fixed ValueError before file access. Renderer accepts no user HTML, query, body or data field.

Fixed attribute/text rewrites keep navigation inside Pocket/home/context guide or the claims.html alias. Existing fragments, IDs, limits, no-script/unnamed/disabled controls and controller order are retained. Titles/brand/edition/back/footer/local labels identify Pocket. Existing facts receive Pocket/offline-after-preparation chips; no second template implementation or copied source HTML is maintained. Early meta CSP restricts connect-src/form-action/base-uri to none; the server's existing policy intersects it, and exported pages retain the same meta without server middleware. Actual browser CSP enforcement belongs to root verification, not these parser tests.

Canonical GET /phone/workspace/{tool}.html is registered BEFORE the /phone StaticFiles mount, returns200text/html for the three known keys and fixed404 for unknown keys. Query text is never consumed or interpolated. Original desktop static pages and Pocket iOS route remain unchanged.

Independent communication agent created acceptance tests first; initial ModuleNotFoundError red receipt is preserved. Implementation then passed25tests. That agent independently reran25passed in0.88s and found no concrete contract gap. Coverage: exact closed keys/assets; traversal/non-string fixed errors; IDs/script ordering/fragments/fixed Pocket navigation; early meta policy; trusted template edit propagation; canonical ASGI HTML/query-no-echo/unknown404; original desktop/iOS bytes unchanged.

Root owns exact worker cache/alias/assets integration, canonical static export materialization using this same renderer, completeness tests, cache bump and source/static archive receipts. Offline browser computations, CSP behavior, actual clipboard/download, physical phone/setup, assistive technology and user learning were not performed or claimed here. No browser/upload/profile changes occurred.
