from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
from PIL import Image
from scipy.optimize import minimize_scalar
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from ai_detector.features import EncoderSpec, HybridFeatureExtractor, transformed_view


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
TRAIN_AUGS = ("jpeg85", "jpeg60", "resize75", "blur05", "crop95", "screenshot_like")


def iter_images(root: Path, split: str):
    for label, cls in ((0, "real"), (1, "ai")):
        folder = root / split / cls
        for p in sorted(folder.glob("*")):
            if p.suffix.lower() in IMAGE_EXTS:
                yield p, label


def _stable_aug(path: Path, copy_index: int) -> str:
    # Unique cycle for the first len(TRAIN_AUGS) copies, with a path-specific
    # offset so the dataset is not transformed in lockstep.
    raw = str(path).encode("utf-8", errors="ignore")
    offset = int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") % len(TRAIN_AUGS)
    return TRAIN_AUGS[(offset + copy_index) % len(TRAIN_AUGS)]


def _dataset_fingerprint(items: list[tuple[Path, int]]) -> str:
    h = hashlib.sha256()
    for p, label in items:
        st = p.stat()
        h.update(f"{p}|{label}|{st.st_size}|{st.st_mtime_ns}\n".encode())
    return h.hexdigest()[:16]


def _cache_path(cache_dir: Path, split: str, spec: EncoderSpec, feature_mode: str, aug_copies: int, items) -> Path:
    config = json.dumps(
        {
            "split": split,
            "spec": spec.__dict__,
            "feature_mode": feature_mode,
            "aug_copies": aug_copies,
            "data": _dataset_fingerprint(items),
        },
        sort_keys=True,
    )
    key = hashlib.sha256(config.encode()).hexdigest()[:20]
    return cache_dir / f"{split}_{feature_mode}_{key}.npz"


def extract_split(
    extractor: HybridFeatureExtractor,
    root: Path,
    split: str,
    aug_copies: int = 0,
    batch_size: int = 32,
    cache_dir: Path | None = None,
):
    items = list(iter_images(root, split))
    if not items:
        raise RuntimeError(f"No images found in {root / split}")

    cache_path = None
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = _cache_path(cache_dir, split, extractor.spec, extractor.feature_mode, aug_copies, items)
        if cache_path.exists():
            data = np.load(cache_path, allow_pickle=True)
            return data["X"], data["y"], data["paths"].tolist()

    feats: list[np.ndarray] = []
    labels: list[int] = []
    paths: list[str] = []
    batch_images: list[Image.Image] = []
    batch_labels: list[int] = []
    batch_paths: list[str] = []

    def flush():
        nonlocal batch_images, batch_labels, batch_paths
        if not batch_images:
            return
        x = extractor.extract_batch(batch_images)
        feats.extend(list(x))
        labels.extend(batch_labels)
        paths.extend(batch_paths)
        batch_images = []
        batch_labels = []
        batch_paths = []

    for path, label in tqdm(items, desc=f"features:{split}"):
        with Image.open(path) as im:
            base = im.convert("RGB")
        views = [(base, str(path))]
        if aug_copies > 0:
            for j in range(aug_copies):
                mode = _stable_aug(path, j)
                views.append((transformed_view(base, mode), f"{path}#aug={mode}"))
        for img, pstr in views:
            batch_images.append(img)
            batch_labels.append(label)
            batch_paths.append(pstr)
            if len(batch_images) >= batch_size:
                flush()
    flush()

    X = np.stack(feats).astype(np.float32)
    y = np.asarray(labels, dtype=np.int64)
    if cache_path is not None:
        np.savez_compressed(cache_path, X=X, y=y, paths=np.asarray(paths, dtype=object))
    return X, y, paths


def sigmoid(z):
    z = np.asarray(z, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))


def classifier_logits(clf, X: np.ndarray) -> np.ndarray:
    """Return a logit-like score for linear or probability classifiers."""
    if hasattr(clf, "decision_function"):
        return np.asarray(clf.decision_function(X), dtype=np.float64)
    if hasattr(clf, "predict_proba"):
        p = np.asarray(clf.predict_proba(X)[:, 1], dtype=np.float64)
        p = np.clip(p, 1e-7, 1.0 - 1e-7)
        return np.log(p / (1.0 - p))
    raise TypeError("Classifier must expose decision_function or predict_proba.")


def fit_temperature(logits: np.ndarray, y: np.ndarray) -> float:
    y = y.astype(np.float64)

    def nll(log_t):
        t = float(np.exp(log_t))
        p = np.clip(sigmoid(logits / t), 1e-7, 1 - 1e-7)
        return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())

    res = minimize_scalar(nll, bounds=(-3.0, 3.0), method="bounded")
    return float(np.exp(res.x))


def pick_ai_threshold(y: np.ndarray, p: np.ndarray, target_fpr: float = 0.02) -> tuple[float, dict]:
    """Threshold for safely calling an image AI-generated."""
    y = np.asarray(y)
    p = np.asarray(p)
    candidates = np.unique(np.concatenate(([0.0], p, [np.nextafter(1.0, 2.0)])))
    feasible = []
    for t in candidates:
        pred_ai = p >= t
        real = y == 0
        fake = y == 1
        fpr = float(pred_ai[real].mean()) if real.any() else 1.0
        tpr = float(pred_ai[fake].mean()) if fake.any() else 0.0
        if fpr <= target_fpr + 1e-12:
            feasible.append((tpr, -fpr, -t, float(t), {"fpr": fpr, "tpr": tpr}))
    if not feasible:
        return float(np.nextafter(1.0, 2.0)), {"fpr": 0.0, "tpr": 0.0}
    best = max(feasible)
    return best[3], best[4]


def pick_real_threshold(y: np.ndarray, p: np.ndarray, target_fake_as_real: float = 0.02) -> tuple[float, dict]:
    """Threshold for safely calling an image real.

    Images with p <= threshold are called real. Constraint limits the fraction
    of fake validation images incorrectly certified as real.
    """
    y = np.asarray(y)
    p = np.asarray(p)
    candidates = np.unique(np.concatenate(([-np.finfo(float).eps], p, [1.0])))
    feasible = []
    for t in candidates:
        pred_real = p <= t
        real = y == 0
        fake = y == 1
        real_recall = float(pred_real[real].mean()) if real.any() else 0.0
        fake_as_real = float(pred_real[fake].mean()) if fake.any() else 1.0
        if fake_as_real <= target_fake_as_real + 1e-12:
            feasible.append((real_recall, -fake_as_real, t, float(t), {"real_recall": real_recall, "fake_as_real": fake_as_real}))
    if not feasible:
        return float(-np.finfo(float).eps), {"real_recall": 0.0, "fake_as_real": 0.0}
    best = max(feasible)
    return best[3], best[4]




def collapse_worst_case(y: np.ndarray, p: np.ndarray, paths: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Collapse transformed validation views to one adversarial score per base image.

    For a real image, the dangerous view is the maximum AI score.
    For a fake image, the dangerous view is the minimum AI score.
    This avoids pretending correlated augmented views are independent samples.
    """
    groups: dict[str, list[tuple[int, float]]] = {}
    for label, prob, path in zip(y, p, paths):
        base = str(path).split("#aug=", 1)[0]
        groups.setdefault(base, []).append((int(label), float(prob)))

    out_y, out_p = [], []
    for rows in groups.values():
        labels = {r[0] for r in rows}
        if len(labels) != 1:
            raise RuntimeError("Validation augmentation group contains mixed labels.")
        label = rows[0][0]
        probs = [r[1] for r in rows]
        robust_prob = max(probs) if label == 0 else min(probs)
        out_y.append(label)
        out_p.append(robust_prob)
    return np.asarray(out_y, dtype=np.int64), np.asarray(out_p, dtype=np.float64)

def selective_summary(y: np.ndarray, p: np.ndarray, real_threshold: float, ai_threshold: float) -> dict:
    y = np.asarray(y)
    p = np.asarray(p)
    resolved_real = p <= real_threshold
    resolved_ai = p >= ai_threshold
    overlap = resolved_real & resolved_ai
    if overlap.any():
        resolved_real = resolved_real & ~overlap
        resolved_ai = resolved_ai & ~overlap
    resolved = resolved_real | resolved_ai
    pred = np.full(len(y), -1, dtype=int)
    pred[resolved_real] = 0
    pred[resolved_ai] = 1
    return {
        "coverage": float(resolved.mean()),
        "unresolved_rate": float(1.0 - resolved.mean()),
        "selective_accuracy": float((pred[resolved] == y[resolved]).mean()) if resolved.any() else 0.0,
        "real_certified_fraction": float(resolved_real.mean()),
        "ai_flagged_fraction": float(resolved_ai.mean()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/cf_local")
    ap.add_argument("--out", default="models/trustlens_image_detector.joblib")
    ap.add_argument("--model-name", default="ViT-B-32")
    ap.add_argument("--pretrained", default="openai")
    ap.add_argument("--feature-mode", choices=["hybrid", "hybrid_forensic", "clip", "spectral", "forensic"], default="hybrid")
    ap.add_argument("--classifier", choices=["logistic", "hgb"], default="logistic", help="hgb is the stronger small-data nonlinear baseline found in the real benchmark.")
    ap.add_argument("--device", default=None)
    ap.add_argument("--aug-copies", type=int, default=2)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--val-aug-copies", type=int, default=6, help="Include robustness views; thresholds are selected on the worst transformed view per image.")
    ap.add_argument("--cache-dir", default="data/feature_cache")
    ap.add_argument("--target-fpr", type=float, default=0.02)
    ap.add_argument("--target-fake-as-real", type=float, default=0.02)
    ap.add_argument("--C", type=float, default=0.5)
    args = ap.parse_args()

    root = Path(args.data)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    spec = EncoderSpec(model_name=args.model_name, pretrained=args.pretrained)
    extractor = HybridFeatureExtractor(spec, device=args.device, feature_mode=args.feature_mode)
    print(f"Device: {extractor.device}; features: {args.feature_mode}")

    cache_dir = Path(args.cache_dir) if args.cache_dir else None
    X_train, y_train, _ = extract_split(
        extractor, root, "train", aug_copies=args.aug_copies, batch_size=args.batch_size, cache_dir=cache_dir
    )
    X_val, y_val, val_paths = extract_split(
        extractor, root, "val", aug_copies=args.val_aug_copies, batch_size=args.batch_size, cache_dir=cache_dir
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    if args.classifier == "logistic":
        clf = LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            C=args.C,
            solver="lbfgs",
        )
    else:
        clf = HistGradientBoostingClassifier(
            max_iter=120,
            max_leaf_nodes=7,
            learning_rate=0.05,
            l2_regularization=2.0,
            random_state=42,
        )
    clf.fit(X_train_s, y_train)

    val_logits = classifier_logits(clf, X_val_s)
    temperature = fit_temperature(val_logits, y_val)
    val_prob = sigmoid(val_logits / temperature)
    robust_y, robust_prob = collapse_worst_case(y_val, val_prob, val_paths)
    ai_threshold, ai_stats = pick_ai_threshold(robust_y, robust_prob, target_fpr=args.target_fpr)
    real_threshold, real_stats = pick_real_threshold(robust_y, robust_prob, target_fake_as_real=args.target_fake_as_real)

    # A poor model can produce crossing safety thresholds. In that case collapse
    # the overlap to a single boundary rather than making contradictory calls.
    thresholds_crossed = real_threshold >= ai_threshold
    if thresholds_crossed:
        mid = float((real_threshold + ai_threshold) / 2.0)
        real_threshold = np.nextafter(mid, -np.inf)
        ai_threshold = np.nextafter(mid, np.inf)

    binary_pred = (robust_prob >= ai_threshold).astype(int)
    report = {
        "val_accuracy_at_ai_threshold": float((binary_pred == robust_y).mean()),
        "val_balanced_accuracy_at_ai_threshold": float(balanced_accuracy_score(robust_y, binary_pred)),
        "val_roc_auc_worst_case": float(roc_auc_score(robust_y, robust_prob)),
        "val_roc_auc_all_views": float(roc_auc_score(y_val, val_prob)),
        "ai_threshold": float(ai_threshold),
        "real_threshold": float(real_threshold),
        "temperature": temperature,
        "target_fpr": args.target_fpr,
        "target_fake_as_real": args.target_fake_as_real,
        "ai_threshold_stats": ai_stats,
        "real_threshold_stats": real_stats,
        "thresholds_crossed_before_fix": thresholds_crossed,
        "selective_worst_case": selective_summary(robust_y, robust_prob, real_threshold, ai_threshold),
        "feature_dim": int(X_train.shape[1]),
        "feature_mode": args.feature_mode,
        "classifier_kind": args.classifier,
        "train_examples_including_aug": int(len(y_train)),
        "val_examples_including_aug": int(len(y_val)),
        "val_base_images": int(len(robust_y)),
        "val_aug_copies": int(args.val_aug_copies),
        "encoder": spec.__dict__,
    }

    bundle = {
        "scaler": scaler,
        "classifier": clf,
        "temperature": temperature,
        "ai_threshold": float(ai_threshold),
        "real_threshold": float(real_threshold),
        "threshold": float(ai_threshold),  # backwards-compatible alias
        "feature_mode": args.feature_mode,
        "classifier_kind": args.classifier,
        "encoder_spec": spec.__dict__,
        "training_report": report,
    }
    joblib.dump(bundle, out)
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
