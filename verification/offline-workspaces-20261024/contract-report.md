# Offline workspace test-first contract

Only tests/test_pocket_workspaces.py is owned app/test source. No module, route, template, export or root file changed by this worker. The first run was captured before app.pocket_workspaces existed: one collection error, ModuleNotFoundError (contract-red.txt). This is an absent-implementation red baseline, not an assertion that individual behaviors were exercised before implementation.

The contract checks the exact three tool keys/template filenames and eight explicit asset paths; unknown/traversal/nonstring keys fail with fixed private-input-free ValueError. Renderer outputs must preserve all source DOM IDs, controller order and fragment links, while navigation stays within Pocket and accurately describes offline preparation. The meta CSP must precede every linked stylesheet/script and block content connections, form submissions and base changes. DOM parsing makes this order check independent of attribute quotation style.

Trusted tmp_path template edits must propagate into rendered output, establishing reuse of canonical templates rather than a second HTML copy. ASGI aliases must serve HTML before the phone mount, ignore query data without echo, and return fixed404 for unknown/traversal paths. Existing desktop source routes and /phone/ios.html must return unchanged file bytes and renderer/request operations must not write source templates.

Product integration is pending; no green result or browser/offline readiness claim yet. Pure renderer/ASGI tests do not establish service-worker cache behavior, actual offline browser operation, physical-device behavior, accessibility or CSP enforcement in a browser. Root's integration/browser/export/preservation receipts remain separate.

## Independent integration result

Product implemented the renderer/route after the captured absent-module red. Independent final rerun:25passed in0.87seconds (contract-green-final.txt); the preceding independent25pass0.88s receipt is retained too. Added an explicit assertion that the direct unknown key returns exactly {detail: Unknown Pocket workspace.}; encoded traversal paths remain fixed404 without echo. No app source was edited by this worker.

Actual source review confirms the renderer reads only a closed-map filename under trusted static_dir, injects fixed early meta CSP, performs fixed navigation/label substitutions and preserves existing algorithms/controllers. Query values are never interpolated. The route is registered before /phone mounting. Current templates preserve all IDs and script order; trusted tmp_path source edits propagate, and original desktop/ios routes still return exact file bytes with no renderer writes. No concrete current contract defect found.

This establishes renderer/ASGI behavior, not real browser offline cache admission or CSP enforcement. Root must separately cache the exact3aliases+8assets, exercise worker readiness and exported static copies, and verify actual browser/narrow/keyboard behavior. The aliases retain original browser-only logic and its limitations; they do not gain backend image/OCR/source verification or data transfer.

Renderer SHA256: a81f82650c0c0c3a3c0ca37b00c36c2e3c44bf58dab23a8b534228e1ead74549. Test source SHA256: 6637a08a0068933155f9078678e7df498828c66a1844372ecb61c8b0694f221f.
