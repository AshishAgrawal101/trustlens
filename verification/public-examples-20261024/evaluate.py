"""One retained source-excerpt diagnostic; never tunes or forces predictions to pass."""
import hashlib,json,time
from pathlib import Path
from app.analyzers.text import request_evidence
FOLDER=Path(__file__).parent
MANIFEST_SHA="1a20943215977476f11c71df256abd210ceb98ea68ce78828226e82256f9da17"
def main():
 target=FOLDER/"results.json"
 if target.exists(): raise RuntimeError("Refusing to overwrite retained diagnostic outputs")
 manifest_bytes=(FOLDER/"frozen-manifest.json").read_bytes()
 assert hashlib.sha256(manifest_bytes).hexdigest()==MANIFEST_SHA
 source=Path("app/analyzers/text.py");before=hashlib.sha256(source.read_bytes()).hexdigest()
 rows=[]
 for record in json.loads(manifest_bytes)["records"]:
  started=time.perf_counter();evidence=request_evidence(record["snippet"]);elapsed=(time.perf_counter()-started)*1000
  warning=any(e.weight>0 for e in evidence);expected=record["expected_warning"]
  rows.append({"id":record["id"],"hand_label":record["hand_label"],"expected_warning":expected,"actual_warning":warning,"expectation_met":None if expected is None else warning==expected,"elapsed_ms":elapsed,"request_evidence":[e.model_dump() for e in evidence]})
 assert hashlib.sha256(source.read_bytes()).hexdigest()==before
 target.write_text(json.dumps({"label":"Published educational excerpts; not a representative benchmark","manifest_sha256":MANIFEST_SHA,"source_sha256":before,"model_ran":False,"rows":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps([{k:r[k] for k in ["id","expected_warning","actual_warning"]}for r in rows],indent=2))
if __name__=="__main__": main()
