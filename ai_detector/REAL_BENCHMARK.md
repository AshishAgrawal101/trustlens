# TrustLens real-image benchmark — 2026-10-05

> Historical results: the benchmark's exclusion list was corrected on 2026-10-06. These earlier scores used three placeholder images and are superseded by the corrected measurements in ../CURRENT_PROGRESS.md.

This is a **development benchmark**, not a claim of production-ready AI-image detection.

## Source and leakage controls

We used the 122-image experiment published in *An Assessment of Challenges and Opportunities for Forensic Investigators: Capitalizing on Artificial Intelligence and Digital Forensics* (Applied Science and Innovative Research, 2026, DOI 10.22158/asir.v10n3p1). The paper reports 61 AI-generated and 61 genuine images and publishes screenshot artifacts from the detector experiment.

To avoid learning the comparison tool's UI, TrustLens extracted only the source-image pane from the published AI-or-Not screenshots. Seven screenshots where the source image itself was replaced by an NSFW placeholder were excluded. Final usable set: **115 images = 57 AI + 58 genuine**.

The evaluation used **5 repeats of stratified 5-fold cross-validation**. Every reported fold tests on images that were not used to fit that fold's classifier. Because feature/classifier development was informed by this benchmark, these are development-CV results; a second untouched external benchmark is still required before making a final generalization claim.

## Clean-image development CV

| Detector | Balanced accuracy | ROC-AUC | False-positive rate | AI recall | F1 |
|---|---:|---:|---:|---:|---:|
| v2 spectral + logistic | 0.623 ± 0.100 | 0.672 ± 0.104 | 0.408 ± 0.154 | 0.653 ± 0.191 | 0.621 ± 0.128 |
| v3 forensic + logistic | 0.635 ± 0.115 | 0.710 ± 0.128 | 0.368 ± 0.135 | 0.637 ± 0.154 | 0.630 ± 0.130 |
| v3 forensic + ExtraTrees | 0.655 ± 0.100 | 0.728 ± 0.102 | 0.402 ± 0.132 | 0.713 ± 0.166 | 0.665 ± 0.118 |
| **v3 forensic + HistGradientBoosting** | **0.663 ± 0.081** | **0.747 ± 0.079** | **0.365 ± 0.122** | **0.691 ± 0.133** | **0.666 ± 0.090** |

The v3 feature branch improves ROC-AUC by about **0.075 absolute** over the original v2 spectral/logistic baseline, but the false-positive rate is still far too high for a product that makes definitive accusations.

## Robustness test

The same outer-fold protocol was evaluated after common post-processing.

### Train on clean images only

| Test view | Balanced accuracy | ROC-AUC |
|---|---:|---:|
| Clean | 0.663 | 0.747 |
| JPEG quality 60 | 0.637 | 0.735 |
| Resize to 50% and back | 0.509 | 0.545 |
| Screenshot-like transform | 0.534 | 0.543 |

### Train with clean + JPEG + resize + screenshot-like augmentation

| Test view | Balanced accuracy | ROC-AUC |
|---|---:|---:|
| Clean | 0.635 | 0.715 |
| JPEG quality 60 | 0.628 | 0.706 |
| Resize to 50% and back | **0.639** | **0.697** |
| Screenshot-like transform | **0.639** | **0.691** |

Augmentation trades a small amount of clean performance for a large gain under resizing and screenshot-like degradation. On the screenshot-like test, balanced accuracy increased from **0.534 to 0.639** and ROC-AUC from **0.543 to 0.691**.

## Abstention / unresolved behavior

We also tested the TrustLens design principle of allowing the detector to say **unresolved**. Thresholds were chosen inside each training fold using a held-out calibration subset with zero observed validation false-AI and false-real calls. On outer test folds the mean results were:

- Coverage: **27.1%**
- Accuracy on resolved cases: **83.9%**
- False-AI call rate on genuine images: **6.6%**
- False-real call rate on AI images: **4.5%**

The gap between zero observed calibration errors and non-zero outer-test errors is important: the calibration subset is too small to support a 0–2% safety claim. The app should therefore keep **Unresolved** and should not present its forensic score as proof.

## What changed in v3

`--feature-mode forensic` adds roughly 200 local forensic features, including:

- radial FFT and residual FFT features;
- multi-scale high-pass residual statistics;
- residual spatial autocorrelation at several lags;
- patch-wise noise dispersion;
- gradient orientation and Laplacian distributions;
- compact uniform-LBP texture features;
- directional Fourier energy;
- multi-scale detail energies and basic color statistics.

The training command now also supports `--classifier hgb`, a small regularized histogram-gradient-boosting classifier that performed better than the original logistic baseline on this development benchmark.

Example:

```bash
python -m ai_detector.train \
  --data data/cf_local \
  --out models/trustlens_forensic.joblib \
  --feature-mode forensic \
  --classifier hgb \
  --aug-copies 4 \
  --val-aug-copies 6
```

## Next benchmark

The next meaningful experiment should use a larger, untouched generator-disjoint benchmark such as Community Forensics / CompEval or a manageable subset of GenImage, with the model and thresholds frozen before evaluation. The current 115-image benchmark is useful for catching obvious failures and guiding engineering, but it is not sufficient evidence for a universal detector.
