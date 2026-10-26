# Transactional recovery response admission

Application scope is only `static/app.js`; tests added only `tests/recovery_response.test.cjs`. No HTML, API, fixed recovery content, other controller path, dependency, fixture or old-test assertion changed. `recovery-before-app.js` preserves pre-edit source.

The validator admits one to four records (the actual endpoint has four), unique ASCII identifier strings up to 32 characters, nonblank labels up to 80 and titles up to 160, and one to eight nonblank string steps of at most 1,000 characters. These caps include the fixed endpoint content with modest text/step headroom while preventing partial/unbounded menu construction. IDs are not treated as URLs or executable actions.

Open now reads into a local `plans`, validates the entire list, then checks current recovery token and open-dialog state before assigning the cache. No partial menu or copyable selection is created. Invalid/missing/empty/duplicate/partial data retains the existing fixed failure/FTC fallback and leaves the cache null, so ordinary close/reopen fetches the corrected response. Valid plans still cache once. Closing or page exit before a late response prevents it seeding the cache. Existing timeout, token, selected-plan and clipboard behavior is retained.

TDD: `contract.json` froze bounds/admission; `red.txt` records three failures and one valid-cache control passing before edits. Four dedicated regressions cover malformed-then-corrected retry, all record/list/text bounds and no partial render, valid caching/input-free copy, and closed/pagehide/restored-Back cache protection. `green.txt`: **35/35** focused new/existing recovery, main state/lifecycle and manual-guide tests pass. Full Node checkpoint `node-checkpoint.txt`: **611/611 pass**, zero failures/skips.

The original issue was constructed malformed-response fault injection, not evidence that current `/api/recovery` normally serves corrupt data. No browser upload, source fetch, native phone, model, storage or broader correctness/accuracy claim follows. Root owns independent/browser/final release checks.
