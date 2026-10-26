# Pocket selectable recovery handoff

## Scope

Changed only `static/phone/phone.js`, `static/phone/index.html`, `static/phone/phone.css`, `tests/phone_recovery.test.cjs`, and this report. The existing static recovery paragraphs were replaced with four selectable fixed checklists. Guidance wording follows `app/guidance.py` RECOVERY_PLANS; link instructions name the corresponding selectable checklists.

## Behavior

- Money, code/password, device access and opened-link choices show one short two-step checklist. Selection is visible through aria-pressed and the selected heading receives focus.
- The panel identifies English/general U.S. scope, asks for no incident details, promises no recovery, and labels the FTC guide as external/internet-dependent. Its fixed checklist requires no fetch.
- Copy and Download export only fixed guidance, its scope and FTC source link. Neither reads the message, extracted hostnames or any incident details. Download uses the existing blob URL pattern, now shared with the ordinary result download.
- Recovery clipboard requests use the existing three-second timeout approach and a separate selection version. Late success/failure cannot label a different checklist or survive Clear/page exit.
- Clear and pagehide clear selection, heading, steps and copy status, and disable stale recovery exports. Clearing does not erase the operating-system clipboard or prior user downloads.
- No storage, dependencies, new service workers, external messages or input-bearing requests introduced.

## Integration

New recovery IDs: recovery (details), recovery-money, recovery-account, recovery-device, recovery-link, recovery-result, recovery-title, recovery-steps, recovery-copy, recovery-download, recovery-status. All previous IDs remain.

At coordinator request, inserted known-site details directly after hosts with known-host, compare-hosts, compare-status, compare-results; appended compare.js after phone.js. Added matching touch/16px input styling. Coordinator owns compare logic/tests and the service-worker/version bump. This worker did not edit those files.

## Verification

`node --test tests/phone_recovery.test.cjs tests/phone_companion.test.cjs`: 20/20 passed. Five recovery regressions reuse the existing phonePage DOM double without changing its source file. They cover four selection states and focus, fixed input-free copy/download and blob cleanup, timeout and stale completion, Clear/page-exit cleanup and export guard, and visible limits/FTC wording.

`node --check static/phone/phone.js`: passed.

## Limits

No browser/device/rendering/clipboard-permission integration check performed here; coordinator owns browser verification. DOM tests do not establish screen-reader or Android behavior. Offline changes require coordinator's matching shell version/cache update. Clipboard timeout releases app status but cannot cancel an operating-system clipboard request that resolves later; exported material is fixed input-free guidance.
