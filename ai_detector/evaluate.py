from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import joblib
import numpy as np
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from tqdm import tqdm

from ai_detector.features import EncoderSpec, HybridFeatureExtractor, transformed_view


def sigmoid(z):
    z = np.asarray(z, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))


def ece(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    y = np.asarray(y)
    p = np.asarray(p)
    edges = np.linspace(0, 1, bins + 1)
    out = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & (p < hi if hi < 1 else p <= hi)
        if not mask.any():
            continue
        out += (mask.mean()) * abs(float(p[mask].mean()) - float(y[mask].mean()))
    return float(out)


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n <= 0:
        return [0.0, 0.0]
    phat = k / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return [float(max(0.0, center - margin)), float(min(1.0, center + margin))]


def metrics(y: np.ndarray, p: np.ndarray, real_threshold: float, ai_threshold: float) -> dict:
    pred = (p >= ai_threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()

    resolved_real = p <= real_threshold
    resolved_ai = p >= ai_threshold
    overlap = resolved_real & resolved_ai
    resolved_real &= ~overlap
    resolved_ai &= ~overlap
    resolved = resolved_real | resolved_ai
    selective_pred = np.full(len(y), -1, dtype=int)
    selective_pred[resolved_real] = 0
    selective_pred[resolved_ai] = 1

    fake = y == 1
    real = y == 0
    fake_as_real = int(np.sum(fake & resolved_real))
    real_certified = int(np.sum(real & resolved_real))

    return {
        "accuracy_at_ai_threshold": float(accuracy_score(y, pred)),
        "balanced_accuracy_at_ai_threshold": float(balanced_accuracy_score(y, pred)),
        "precision_ai": float(precision_score(y, pred, zero_division=0)),
        "recall_ai": float(recall_score(y, pred, zero_division=0)),
        "f1_ai": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "ece_10": ece(y, p, 10),
        "fpr_ai_call": float(fp / max(fp + tn, 1)),
        "fpr_ai_call_95ci": wilson(int(fp), int(fp + tn)),
        "tpr_ai_call": float(tp / max(tp + fn, 1)),
        "tpr_ai_call_95ci": wilson(int(tp), int(tp + fn)),
        "fake_as_real_rate": float(fake_as_real / max(int(fake.sum()), 1)),
        "real_certification_rate": float(real_certified / max(int(real.sum()), 1)),
        "coverage": float(resolved.mean()),
        "unresolved_rate": float(1.0 - resolved.mean()),
        "selective_accuracy": float((selective_pred[resolved] == y[resolved]).mean()) if resolved.any() else 0.0,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def load_metadata(root: Path) -> dict[str, dict]:
    result = {}
    path = root / "metadata.jsonl"
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        key = row.get("relpath") or Path(row["path"]).name
        result[str(key)] = row
    return result


def test_items(root: Path):
    for label, cls in ((0, "real"), (1, "ai")):
        for p in sorted((root / "test" / cls).glob("*")):
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                yield p, label


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/cf_local")
    ap.add_argument("--model", default="models/trustlens_image_detector.joblib")
    ap.add_argument("--device", default=None)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--transforms", default="clean,jpeg85,jpeg60,jpeg40,resize75,resize50,blur05,blur,crop95,crop90,screenshot_like")
    ap.add_argument("--out", default="models/evaluation.json")
    args = ap.parse_args()

    root = Path(args.data)
    bundle = joblib.load(args.model)
    spec = EncoderSpec(**bundle["encoder_spec"])
    feature_mode = bundle.get("feature_mode", "hybrid")
    extractor = HybridFeatureExtractor(spec, device=args.device, feature_mode=feature_mode)
    scaler = bundle["scaler"]
    clf = bundle["classifier"]
    temp = float(bundle["temperature"])
    ai_threshold = float(bundle.get("ai_threshold", bundle.get("threshold", 0.5)))
    real_threshold = float(bundle.get("real_threshold", 1.0 - ai_threshold))
    metadata = load_metadata(root)

    items = list(test_items(root))
    if not items:
        raise RuntimeError(f"No test images found under {root / 'test'}")

    full = {}
    for mode in [x.strip() for x in args.transforms.split(",") if x.strip()]:
        feats, y, paths = [], [], []
        images, labels, names = [], [], []

        def flush():
            nonlocal images, labels, names
            if not images:
                return
            feats.extend(list(extractor.extract_batch(images)))
            y.extend(labels)
            paths.extend(names)
            images, labels, names = [], [], []

        for path, label in tqdm(items, desc=f"eval:{mode}"):
            with Image.open(path) as im:
                img = transformed_view(im.convert("RGB"), mode)
            images.append(img)
            labels.append(label)
            names.append(path.relative_to(root).as_posix())
            if len(images) >= args.batch_size:
                flush()
        flush()

        X = scaler.transform(np.stack(feats))
        y_arr = np.asarray(y, dtype=np.int64)
        if hasattr(clf, "decision_function"):
            logits = np.asarray(clf.decision_function(X), dtype=np.float64)
        else:
            raw = np.clip(np.asarray(clf.predict_proba(X)[:, 1], dtype=np.float64), 1e-7, 1 - 1e-7)
            logits = np.log(raw / (1.0 - raw))
        p = sigmoid(logits / temp)
        m = metrics(y_arr, p, real_threshold, ai_threshold)

        if mode == "clean" and metadata:
            by_generator = defaultdict(list)
            by_arch = defaultdict(list)
            for name, label, prob in zip(paths, y_arr, p):
                if label != 1:
                    continue
                row = metadata.get(name)
                if row:
                    hit = float(prob >= ai_threshold)
                    by_generator[row.get("model_name") or "unknown"].append(hit)
                    by_arch[row.get("architecture") or "unknown"].append(hit)
            gen_rec = {g: float(np.mean(v)) for g, v in by_generator.items() if v}
            if gen_rec:
                vals = np.asarray(list(gen_rec.values()), dtype=float)
                m["fake_generator_count"] = len(gen_rec)
                m["fake_generator_macro_recall"] = float(vals.mean())
                m["fake_generator_p10_recall"] = float(np.quantile(vals, 0.10))
                m["fake_generator_worst_10"] = sorted(gen_rec.items(), key=lambda x: x[1])[:10]
            if by_arch:
                m["fake_architecture_recall"] = {k: float(np.mean(v)) for k, v in sorted(by_arch.items())}

        full[mode] = m
        print(mode, json.dumps(m, indent=2))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(full, indent=2), encoding="utf-8")
    print(f"\nSaved evaluation: {out}")


if __name__ == "__main__":
    main()
