"""CPU-only C2PA verifier. Reads an asset on stdin; never fetches asset URLs."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys

TRUST = Path(__file__).resolve().parents[1] / 'trust'
MAX_BYTES = 64 * 1024 * 1024
AI_SOURCE = 'http://cv.iptc.org/newscodes/digitalsourcetype/'
VERIFY = {'verify_after_reading': True, 'verify_trust': True,
          'verify_timestamp_trust': True, 'remote_manifest_fetch': False, 'ocsp_fetch': False}


def result(status: str, detail: str, **fields) -> dict:
    return {'status': status, 'detail': detail, **fields}


def text(value) -> str | None:
    return value[:256] if isinstance(value, str) and value.strip() else None


def summarize(store: dict, trust_list: str) -> dict:
    """Only assertions in the active, asset-bound claim can establish this result."""
    manifest = store.get('manifests', {}).get(store.get('active_manifest'))
    if not isinstance(manifest, dict):
        return result('invalid', 'Content Credentials could not be validated.')
    state = store.get('validation_state')
    checks = store.get('validation_results', {}).get('activeManifest', {})
    success = {q.get('code') for q in checks.get('success', [])}
    failures = {q.get('code') for q in checks.get('failure', [])}
    # A signature alone is insufficient: require a hard binding to these bytes.
    bound = bool(success & {'assertion.dataHash.match', 'assertion.bmffHash.match', 'assertion.boxesHash.match'})
    signed = 'claimSignature.validated' in success
    trusted = state == 'Trusted' and 'signingCredential.trusted' in success and not failures and bound and signed
    untrusted = state == 'Valid' and bound and signed and failures <= {'signingCredential.untrusted'}
    status = 'verified' if trusted else 'untrusted' if untrusted else 'invalid'
    signature = manifest.get('signature_info') or {}
    declaration = None
    tool = None
    # Do not infer a generation tool from the software that merely wrote the claim.
    for assertion in manifest.get('assertions', []):
        if assertion.get('label') not in {'c2pa.actions', 'c2pa.actions.v2'}:
            continue
        for action in assertion.get('data', {}).get('actions', []):
            source = action.get('digitalSourceType')
            candidate = ('generated' if action.get('action') == 'c2pa.created' and source == AI_SOURCE+'trainedAlgorithmicMedia'
                         else 'edited' if source == AI_SOURCE+'compositeWithTrainedAlgorithmicMedia' else None)
            if candidate and (declaration != 'generated' or candidate == 'generated'):
                declaration = candidate
                agent = action.get('softwareAgent')
                tool = text(agent.get('name')) if isinstance(agent, dict) else text(agent)
    details = {
        'verified': 'The embedded signature, image binding and signer trust validated against a local trust-list snapshot.',
        'untrusted': 'The signature matches this image, but its signer is not on the configured trust lists. Its declarations are unverified.',
        'invalid': 'Content Credentials failed validation. Their signer and origin declarations cannot be relied on.',
    }
    return result(status, details[status], signer=text(signature.get('issuer')) or text(signature.get('common_name')),
                  tool=tool, declaration=declaration, signed_at=text(signature.get('time')),
                  validation_state=text(state), trust_list=trust_list if trusted else None,
                  validation_codes=sorted(c for c in failures if isinstance(c, str))[:12])


def trust_configs() -> list[tuple[str, dict]]:
    snapshot = json.loads((TRUST/'snapshot.json').read_text(encoding='utf-8'))
    for item in snapshot['sources']:
        path = TRUST/item['name']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Trust-list snapshot integrity mismatch')
    return [
        ('Official C2PA trust list', {'trust_anchors': (TRUST/'c2pa-trust-list.pem').read_text(encoding='utf-8')}),
        ('Legacy Content Credentials interim trust list', {
            'trust_anchors': (TRUST/'interim-anchors.pem').read_text(encoding='utf-8'),
            'allowed_list': (TRUST/'interim-allowed.txt').read_text(encoding='utf-8'),
            'trust_config': (TRUST/'interim-config.txt').read_text(encoding='utf-8')}),
    ]


def verify(content: bytes, mime: str, configs=None) -> dict:
    import c2pa
    best = None
    for label, trust in (trust_configs() if configs is None else configs):
        config = {'verify': VERIFY, 'core': {'allowed_network_hosts': []}, 'trust': trust}
        try:
            with c2pa.Context.from_dict(config) as context, c2pa.Reader(mime, io.BytesIO(content), context=context) as reader:
                if not reader.is_embedded():
                    return result('external', 'This image refers to external credentials. Only embedded credentials are checked; external URLs are not fetched.')
                store = json.loads(reader.json())
                summary = summarize(store, label)
                if summary['status'] == 'verified': return summary
                if best is None or summary['status'] == 'untrusted': best = summary
        except c2pa.C2paError.ManifestNotFound:
            return result('absent', 'No embedded Content Credentials were found. This does not establish whether the image is real or AI-generated.')
        except c2pa.C2paError.RemoteManifest:
            return result('external', 'External Content Credentials were not fetched.')
        except c2pa.C2paError as exc:
            # The pinned SDK reports a disabled external-manifest read as a
            # generic Remote error. Do not expose or fetch the supplied URL.
            if str(exc).startswith('Remote: must fetch remote manifests from url '):
                return result('external', 'External Content Credentials were not fetched.')
            best = best or result('invalid', 'Content Credentials could not be validated.')
    return best or result('unavailable', 'Content Credentials verification is unavailable.')


def main() -> None:
    try:
        content = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES: raise ValueError('Asset too large')
        mime = sys.argv[1]
        if mime not in {'image/jpeg', 'image/png', 'image/webp'}: raise ValueError('Unsupported asset')
        answer = verify(content, mime)
    except Exception:
        answer = result('unavailable', 'Content Credentials verification is unavailable.')
    sys.stdout.write(json.dumps(answer, ensure_ascii=True))


if __name__ == '__main__':
    main()
