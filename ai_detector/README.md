# TrustLens AI Image Detector — v2 local baseline

> This document describes the earlier general training CLI. The app now uses the measured CLIP ViT-L/14 development head and shared frozen_vision.py loader. See ../CURRENT_PROGRESS.md for current results and the corrected benchmark exclusions.

This module builds a **fully local** AI-vs-real image detector. The goal is not a misleading 100% random-split number; the goal is **unseen-generator generalization, low false-positive rates, and robustness to ordinary post-processing**.

## Model v2

The default detector combines:

1. Frozen **CLIP ViT-B/32** image features.
2. A content-reduced forensic branch with:
   - radial FFT profile
   - high-pass residual FFT profile
   - high-frequency energy ratios
   - edge/residual statistics
   - RGB residual-channel correlations
3. A local logistic-regression head.
4. Temperature calibration.
5. **Two safety thresholds**:
   - high threshold to call an image AI-generated
   - low threshold to call an image real
   - everything between them is **unresolved**
6. Worst-case calibration across ordinary transformed validation views.
7. Test-time augmentation (TTA) for single-image prediction.

The LLM is not involved.

## Why not aim for 100%?

AI-image detectors often look excellent when train/test data share generators or dataset artifacts, then deteriorate on new generators. TrustLens therefore treats the official **CommunityForensics-Eval / CompEval** split as the preferred untouched test set.

The local preparation script uses CommunityForensics-Small for train/validation and, by default, streams the official CompEval set for test.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate

# If torch installation needs a GPU-specific command, install it from pytorch.org first.
pip install -r requirements-ai.txt
```

## 1. Stream a manageable dataset

```bash
python -m ai_detector.prepare_cf_subset \
  --out data/cf_local \
  --train-per-class 5000 \
  --val-per-class 1000 \
  --test-per-class 2000
```

Default behavior:

- train/validation: `OwensLab/CommunityForensics-Small`
- fake validation generators are disjoint from fake training generators
- test: `OwensLab/CommunityForensics-Eval`, split `CompEval`
- NSFW-flagged rows are skipped
- all images are uniformly re-encoded to JPEG quality 95 to avoid original container-format shortcuts

For a quick first run, use `1000 / 250 / 500` per class.

Use `--internal-test` only for debugging when you explicitly want all three splits carved from CommunityForensics-Small.

## 2. Train locally

```bash
python -m ai_detector.train \
  --data data/cf_local \
  --out models/trustlens_image_detector.joblib \
  --feature-mode hybrid \
  --aug-copies 3 \
  --val-aug-copies 6
```

Device selection is automatic: CUDA -> Apple MPS -> CPU.

### Important v2 behavior

Training augmentations are drawn from:

- JPEG 85
- JPEG 60
- resize 75%
- mild blur
- crop 95%
- screenshot-like rescale/recompression

Validation includes robustness views too. Thresholds are selected from **one worst-case score per base validation image**:

- real image -> maximum AI score across its views
- AI image -> minimum AI score across its views

That means a screenshot/compression transformation has to survive the calibration protocol rather than being ignored.

Feature extraction is batched and cached under `data/feature_cache`, so rerunning the classifier does not require re-encoding every image.

## 3. Ablation study

Run all three:

```bash
python -m ai_detector.train --data data/cf_local --out models/clip.joblib --feature-mode clip
python -m ai_detector.train --data data/cf_local --out models/spectral.joblib --feature-mode spectral
python -m ai_detector.train --data data/cf_local --out models/hybrid.joblib --feature-mode hybrid
```

This lets you answer a real research question instead of merely reporting one model score:

> Do semantic foundation-model features and low-level forensic features provide complementary generalization on unseen generators?

## 4. Evaluate

```bash
python -m ai_detector.evaluate \
  --data data/cf_local \
  --model models/trustlens_image_detector.joblib
```

Robustness tests include:

- JPEG 85 / 60 / 40
- resize 75% / 50%
- mild / stronger Gaussian blur
- crop 95% / 90%
- screenshot-like rescaling/recompression

Reported metrics include:

- ROC-AUC / PR-AUC
- binary AI-call precision/recall/F1
- false-positive rate with 95% Wilson interval
- Brier score / ECE
- `real / AI / unresolved` coverage
- selective accuracy among resolved examples
- fake-as-real rate
- per-generator macro recall / 10th-percentile recall
- architecture-level recall where metadata exists

## 5. Predict one image

```bash
python -m ai_detector.predict path/to/image.jpg \
  --model models/trustlens_image_detector.joblib
```

By default the predictor evaluates clean, JPEG-85, and resized views and reports their score spread. A large disagreement forces **unresolved** rather than presenting an unstable verdict as certain.

## Smoke-test result

The code was exercised end-to-end on an intentionally artificial toy dataset containing smooth low-frequency images versus periodic synthetic textures. This test exists only to verify the pipeline, not to estimate real AI-image accuracy.

After v2 robustness calibration, the toy evaluation reached 100% AI recall and 0 observed false AI calls on clean, JPEG-85, JPEG-60, resize-75, mild-blur, and screenshot-like variants. These numbers are **not** a real benchmark claim.

The next meaningful result is the untouched CommunityForensics-Eval score.

## What counts as success?

Prioritize:

- strong CompEval ROC-AUC and balanced accuracy
- low real-image false-positive rate
- high per-generator macro and 10th-percentile recall
- robustness after screenshots/compression
- useful coverage at high selective accuracy
- a second frozen benchmark after model development is complete

A 93% detector that survives unseen generators is much more valuable than a 100% detector on a leaked/random split.
