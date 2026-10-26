from __future__ import annotations

import argparse
import json

import joblib
import numpy as np
from PIL import Image

from ai_detector.features import EncoderSpec, HybridFeatureExtractor, transformed_view


def sigmoid(z: np.ndarray | float):
    z = np.asarray(z, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--model", default="models/trustlens_image_detector.joblib")
    ap.add_argument("--device", default=None)
    ap.add_argument("--tta", default="clean,jpeg85,resize75")
    args = ap.parse_args()

    bundle = joblib.load(args.model)
    spec = EncoderSpec(**bundle["encoder_spec"])
    feature_mode = bundle.get("feature_mode", "hybrid")
    extractor = HybridFeatureExtractor(spec, device=args.device, feature_mode=feature_mode)

    modes = [m.strip() for m in args.tta.split(",") if m.strip()]
    with Image.open(args.image) as im:
        base = im.convert("RGB")
    views = [transformed_view(base, m) for m in modes]
    feats = extractor.extract_batch(views)
    x = bundle["scaler"].transform(feats)
    clf = bundle["classifier"]
    if hasattr(clf, "decision_function"):
        logits = np.asarray(clf.decision_function(x), dtype=np.float64)
    else:
        raw = np.clip(np.asarray(clf.predict_proba(x)[:, 1], dtype=np.float64), 1e-7, 1 - 1e-7)
        logits = np.log(raw / (1.0 - raw))
    probs = sigmoid(logits / float(bundle["temperature"]))

    # Median TTA is less sensitive to one particular encoding/resizing view.
    p = float(np.median(probs))
    spread = float(np.max(probs) - np.min(probs)) if len(probs) > 1 else 0.0
    ai_threshold = float(bundle.get("ai_threshold", bundle.get("threshold", 0.5)))
    real_threshold = float(bundle.get("real_threshold", 1.0 - ai_threshold))

    if p >= ai_threshold:
        prediction = "ai_generated"
    elif p <= real_threshold:
        prediction = "real"
    else:
        prediction = "unresolved"

    # If ordinary transformations cause a large disagreement, downgrade to unresolved.
    unstable = spread >= 0.30
    if unstable:
        prediction = "unresolved"

    result = {
        "ai_score": p,
        "view_scores": {m: float(v) for m, v in zip(modes, probs)},
        "stability_spread": spread,
        "ai_threshold": ai_threshold,
        "real_threshold": real_threshold,
        "prediction": prediction,
        "unstable_under_transforms": unstable,
        "warning": "Forensic model inference is probabilistic evidence, not proof of authorship.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
