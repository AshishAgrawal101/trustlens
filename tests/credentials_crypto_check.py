"""Real C2PA signing/verification checks in the separate CPU SDK environment.

Test certificates are generated in memory and never added to app trust stores.
"""
import io
import json
from pathlib import Path
import struct
import sys
from datetime import datetime, timedelta, timezone
import zlib

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import c2pa

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.analyzers.content_credentials_worker import verify, VERIFY, AI_SOURCE


def run(source: bytes, destination: Path):
    now = datetime.now(timezone.utc)
    root_key, key = ec.generate_private_key(ec.SECP256R1()), ec.generate_private_key(ec.SECP256R1())
    root_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'TrustLens test root ONLY')])
    name = x509.Name([x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Test Generator ONLY'),
                      x509.NameAttribute(NameOID.COMMON_NAME, 'Test Signer ONLY')])
    root = (x509.CertificateBuilder().subject_name(root_name).issuer_name(root_name)
        .public_key(root_key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now-timedelta(days=1)).not_valid_after(now+timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(x509.KeyUsage(False,False,False,False,False,True,True,False,False),critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()),critical=False)
        .sign(root_key, hashes.SHA256()))
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(root_name)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now-timedelta(days=1)).not_valid_after(now+timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=False,path_length=None),critical=True)
        .add_extension(x509.KeyUsage(True,False,False,False,False,False,False,False,False),critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.EMAIL_PROTECTION]),critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),critical=False)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()),critical=False)
        .sign(root_key,hashes.SHA256()))
    pem = root.public_bytes(serialization.Encoding.PEM).decode()
    (destination/'test-root.pem').write_text(pem,encoding='utf-8')
    chain = cert.public_bytes(serialization.Encoding.PEM) + root.public_bytes(serialization.Encoding.PEM)
    private = key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
    config = {'verify':{**VERIFY,'verify_after_sign':False}, 'core':{'allowed_network_hosts':[]},
              'builder':{'thumbnail':{'enabled':False}},'trust':{'trust_anchors':pem}}
    trusted = [('Ephemeral test root ONLY', {'trust_anchors':pem})]

    def sign(source_type, tool='Test AI Tool ONLY', external=False):
        signer = c2pa.Signer.from_info(c2pa.C2paSignerInfo(c2pa.C2paSigningAlg.ES256,chain,private,None))
        action = {'action':'c2pa.created','digitalSourceType':AI_SOURCE+source_type}
        if tool: action['softwareAgent'] = {'name':tool}
        manifest = {'claim_generator_info':[{'name':'Test Manifest Writer ONLY'}], 'title':'Synthetic test asset',
            'assertions':[{'label':'c2pa.actions.v2','data':{'actions':[action]}}]}
        output = io.BytesIO()
        with c2pa.Context.from_dict(config,signer=signer) as ctx, c2pa.Builder(manifest,context=ctx) as builder:
            if external:
                builder.set_no_embed()
                builder.set_remote_url('https://example.invalid/never-fetch.c2pa')
            builder.sign('image/png',io.BytesIO(source),output)
        return output.getvalue()

    signed = sign('trainedAlgorithmicMedia')
    (destination/'signed.png').write_bytes(signed)
    # Insert a valid ancillary PNG chunk outside the manifest. Pillow can still
    # decode it; changing asset bytes must fail the C2PA hard binding.
    chunk = b'tEXt'+b'note\x00changed after signing'
    chunk = struct.pack('>I',len(chunk)-4)+chunk+struct.pack('>I',zlib.crc32(chunk)&0xffffffff)
    tampered = signed[:-12]+chunk+signed[-12:]
    (destination/'tampered.png').write_bytes(tampered)
    external = sign('trainedAlgorithmicMedia',external=True)
    (destination/'external.png').write_bytes(external)
    answers = {
        'trusted':verify(signed,'image/png',trusted),
        'untrusted':verify(signed,'image/png'),
        'tampered':verify(tampered,'image/png',trusted),
        'absent':verify(source,'image/png'),
        'edited':verify(sign('compositeWithTrainedAlgorithmicMedia'),'image/png',trusted),
        'conventional_edit':verify(sign('algorithmicallyEnhanced'),'image/png',trusted),
        'no_tool':verify(sign('trainedAlgorithmicMedia',tool=None),'image/png',trusted),
        'external':verify(external,'image/png',trusted),
    }
    (destination/'results.json').write_text(json.dumps(answers),encoding='utf-8')


if __name__ == '__main__':
    run(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]))
