"""Metadata-only diagnostic freeze; never imports inference libraries or reads images."""
import ctypes
import hashlib
import json
import msvcrt
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
APP = HERE.parents[1]
OLD = APP.parent / 'neighborhood_hacks_20261021'
WORK = Path('C:/Users/round/Documents/Codex/2026-10-05/con/work')
DATA = Path('D:/TrustLensData')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p): return {'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}

manifest = WORK/'training-v2-generalization-20261013/data/admitted.json'
assert pin(manifest)['sha256'] == '91dc9b6ddca57204b456f0bc2cae8aab1ce1df87e594c593f7b93f2928ca6135'
m = read(manifest)
assert m['sealed_tests_opened'] is False and m['source_roles_frozen_before_features'] is True
cohort = []
for label in (0, 1):
    rows = sorted((r for r in m['items'] if r['partition']=='validation' and r['label']==label), key=lambda r:r['id'])[:2]
    assert len(rows)==2 and all(r['official_split']=='train' for r in rows)
    for r in rows:
        q = dict(r)
        q['absolute_image_path'] = str(DATA/r['image_path'])
        q['file_exists_metadata_only'] = (DATA/r['image_path']).is_file()
        q['original_digest_verified_now'] = False
        q['license_scope'] = r['dataset_license'] if label==0 else 'CC-BY-NC-4.0 per locally pinned OpenFake README; underlying image rights not independently reverified'
        cohort.append(q)
assert len({r['original_bytes_sha256'] for r in cohort})==4
directories = [Path(p) for p in read(WORK/'training-v2-photo-adaptation-20261018/protocol.json')['lock_directories']]
locks=[]
for directory in directories:
    for name in ('runner.lock','gpu.lock'):
        p=directory/name
        result={'path':str(p),'exists':p.is_file(),'acquired':False}
        if p.is_file():
            before=pin(p)
            try:
                with p.open('rb') as stream:
                    msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
                    msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
                result['acquired']=True
            except OSError as e: result['error']=str(e)
            assert pin(p)==before
            result.update(before)
        locks.append(result)
stops = [WORK/'STOP',DATA/'STOP',OLD/'artifacts/sprint48/STOP',OLD/'artifacts/sprint48/image-comparison/STOP',OLD/'artifacts/sprint48/image-comparison/v2/STOP',APP/'artifacts/sprint48/STOP']+[p/'STOP' for p in directories]
pins=[pin(APP/p) for p in ('models/image_pipeline.json','models/clip_external_probe.joblib','ai_detector/image_ensemble.py','ai_detector/decision_policy.py','app/analyzers/image.py','app/main.py','serve.py','local-runtime.json')]
pins += [pin(DATA/'pinned_README.md'),pin(manifest),pin(OLD/'artifacts/sprint48/accuracy-request-20261023/AUDIT.md'),pin(OLD/'artifacts/sprint48/accuracy-request-20261023/evidence.json')]
protocol={'at_utc':datetime.now(timezone.utc).isoformat(),'status':'frozen_for_root_review_not_authorized_to_score','selection':'first two validation rows by lexical id per label, before payload reads or scores; examined development only','cohort':cohort,'source_manifest':pin(manifest),'runtime':read(APP/'models/image_pipeline.json'),'source_pins':pins,'native_entry':'ImageEnsemble.score_details plus is_inconclusive; ordinary local POST /api/analyze/image only if separately admitted and endpoint source/process proven','views':['original','EXIF-transpose then RGB JPEG quality=60, no resize, Pillow version and output hash to be pinned before scoring'],'budget':{'cpu_threads':6,'gpu':False,'network_external_bytes':0,'new_D_bytes':0,'max_output_bytes':10000000,'max_seconds':600,'combined_private_and_resident_abort_bytes':1879048192,'import_admission_bytes':1342177280,'supervisor_reserve_bytes':268435456},'missing_proof':['Current native scientific import/load admission under reviewed containment; prior smoke failed import/metadata admission','Full installed fitting/calibration/exact/near/prompt overlap lineage for these four rows; manifest admission is not installed-v1 independence proof','Root approval and scoped preservation of historical STOP','Proof endpoint process source directory/environment identity and CPU setting; listener is lazy, not warmed'],'scores':None,'population_accuracy':None,'release_acceptance':False}
receipt={'at_utc':protocol['at_utc'],'locks':locks,'stops':[pin(p) for p in stops if p.is_file()],'payloads_read':False,'scientific_imports':False,'inference':False,'new_downloads':False,'model_or_STOP_edits':False,'historical_import_failure':read(OLD/'artifacts/sprint48/image-comparison/v2/smoke/supervisor-result.json')}
for name,obj in [('protocol.json',protocol),('audit-receipt.json',receipt)]:
    path=HERE/name
    assert not path.exists(), 'Refuse replacing frozen receipt'
    path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'protocol':pin(HERE/'protocol.json'),'receipt':pin(HERE/'audit-receipt.json'),'locks_acquired':sum(r['acquired'] for r in locks),'stops':receipt['stops'],'cohort_exists':all(r['file_exists_metadata_only'] for r in cohort)},indent=2))
