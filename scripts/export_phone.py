"""Export the explicit static companion for user-controlled HTTPS device tests."""
import hashlib
import json
from pathlib import Path
import zipfile
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.pocket_workspaces import PAGES, ASSETS as WORKSPACE_ASSETS, render_pocket_workspace
ASSETS=('index.html','phone.css','phone.js','guide.js','compare.js','suggestions.js','practice.js','share.js','share-demo.html','share-demo.js','ios.html','ios.css','ios.js','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','sw.js','context.html')
README="""# TrustLens Pocket — iPhone device test

This archive contains the static, human-guided Pocket companion only. It does not include the desktop Python analyzer, screenshot OCR, image detector, private input, model weights or local configuration. It is not an installed native iPhone app and does not read Messages/SMS automatically.

## Connection before testing

Use a trusted HTTPS site you control, with phone/ served at /phone/ and static/ at /static/. Keep the fixed /phone/ paths intact. No hosting, public upload, certificate trust change, tunnel or network exposure is performed by exporting this file. Review the source and hosting permissions before you publish. Do not put private text into an address, query, fragment or hosting logs.

127.0.0.1 on an iPhone means that phone, not this desktop. A local loopback server address cannot connect the devices. Opening this ZIP in Files is not the same as installing or testing a Safari web app.

## Actual iPhone test

1. Open the trusted HTTPS /phone/ address in Safari. Use constructed text only for the first test.
2. Expand Offline access, prepare it, and wait for the exact ready status. If it fails, record the failure rather than claiming offline support.
3. Follow Set up on iPhone for Home Screen setup. Menu labels vary. Record device/iOS/browser and whether installation really succeeded.
4. Copy the constructed phrase: Read me your security code now. In Pocket, tap Paste copied text only when ready to grant that action, or paste manually. Pasting must not run a check.
5. Select the code request yourself, then show next steps. Pocket is user-guided, not an automatic scam classifier. Verify code-protection and independent-contact steps appear.
6. Clear private text. Check the textarea/topics/result are cleared. Clear does not erase the system clipboard or copies in other apps.
7. Reopen the prepared guide with the connection disabled, and repeat selection/steps/Clear. Record actual behavior separately from desktop-browser evidence.
8. Native Share is optional. Share fixed steps only to a destination you explicitly choose. Do not claim delivery merely because a share sheet opens.

The fixed context guide, three interactive claim/number/quote workspaces and twelve constructed Practice scenarios are included. After successful preparation, test the context guide and Practice while disconnected; no truth verdict or learning effect is claimed.

The desktop link at the bottom requires the separate backend and may be absent on a companion-only host. Screenshot reading stays in the desktop app; the iPhone guide explains Apple Live Text as a separate manual path.

Use docs/DEVICE-AND-USABILITY-TEST.md from the full source bundle for consent, task timing and blank observations. No physical-device or user-study result is implied by this archive. Never replace failed or unperformed checks with invented successes.
"""

def build_phone_bundle(destination):
    destination=Path(destination)
    if destination.exists(): raise FileExistsError('Preserve the previous phone bundle; choose a new name.')
    # Only known shell assets: a later private file in this directory must never be exported.
    files={f'phone/{name}':(ROOT/'static/phone'/name).read_bytes() for name in ASSETS}
    files.update({f'phone/workspace/{tool}.html':render_pocket_workspace(tool, ROOT/'static').encode() for tool in PAGES})
    files.update({name.lstrip('/'):(ROOT/name.lstrip('/')).read_bytes() for name in WORKSPACE_ASSETS})
    files['README-IPHONE-TEST.md']=README.encode()
    manifest={'purpose':'Static user-guided companion device test, no deployment performed','files':[{'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in files.items()]}
    with zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED) as archive:
        for name,data in files.items(): archive.writestr(name,data)
        archive.writestr('PHONE_TEST_MANIFEST.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        for item in manifest['files']:assert hashlib.sha256(archive.read(item['path'])).hexdigest()==item['sha256']
    return {'path':str(destination),'files':len(files)+1,'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'verified':True,'deployed':False,'physical_device_tested':False}

if __name__=='__main__':
    receipt=build_phone_bundle(ROOT.parent/'TrustLens-Pocket-iphone-test-v42.zip')
    Path(receipt['path']).with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
