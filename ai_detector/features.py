from __future__ import annotations

import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from PIL import Image, ImageEnhance, ImageFilter
from scipy.ndimage import gaussian_filter


@dataclass(frozen=True)
class EncoderSpec:
    model_name: str = "ViT-B-32"
    pretrained: str = "openai"
    spectral_bins: int = 32
    residual_bins: int = 16
    spectral_size: int = 256


class HybridFeatureExtractor:
    """Frozen CLIP features + low-level forensic features.

    feature_mode can be:
      - clip: CLIP only
      - spectral: local spectral/noise features only (no model download needed)
      - forensic: richer handcrafted forensic features
      - hybrid: concatenate CLIP + spectral
      - hybrid_forensic: concatenate CLIP + richer forensic features
    """

    def __init__(
        self,
        spec: EncoderSpec | None = None,
        device: str | None = None,
        feature_mode: str = "hybrid",
    ):
        self.spec = spec or EncoderSpec()
        self.device = device or best_device()
        self.feature_mode = feature_mode
        if feature_mode not in {"clip", "spectral", "forensic", "hybrid", "hybrid_forensic"}:
            raise ValueError(f"Unknown feature_mode: {feature_mode}")

        self.model = None
        self.preprocess = None
        if feature_mode in {"clip", "hybrid", "hybrid_forensic"}:
            try:
                import open_clip
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "open_clip_torch is required for CLIP/hybrid features. "
                    "Install requirements-ai.txt first, or use --feature-mode spectral/forensic."
                ) from exc

            model, _, preprocess = open_clip.create_model_and_transforms(
                self.spec.model_name,
                pretrained=self.spec.pretrained,
            )
            self.model = model.eval().to(self.device)
            self.preprocess = preprocess
            for p in self.model.parameters():
                p.requires_grad_(False)

    @torch.inference_mode()
    def clip_embeddings(self, images: Sequence[Image.Image]) -> np.ndarray:
        if self.model is None or self.preprocess is None:
            raise RuntimeError("CLIP encoder is not loaded in spectral-only mode.")
        if not images:
            return np.empty((0, 0), dtype=np.float32)
        batch = torch.stack([self.preprocess(im.convert("RGB")) for im in images]).to(self.device)
        feat = self.model.encode_image(batch)
        feat = feat / feat.norm(dim=-1, keepdim=True).clamp_min(1e-12)
        return feat.float().cpu().numpy().astype(np.float32)

    def spectral_features(self, image: Image.Image) -> np.ndarray:
        return spectral_features(
            image,
            bins=self.spec.spectral_bins,
            residual_bins=self.spec.residual_bins,
            size=self.spec.spectral_size,
        )

    def extract_batch(self, images: Sequence[Image.Image]) -> np.ndarray:
        if not images:
            return np.empty((0, 0), dtype=np.float32)
        local = None
        clip = None
        if self.feature_mode in {"spectral", "hybrid"}:
            local = np.stack([self.spectral_features(im) for im in images]).astype(np.float32)
        elif self.feature_mode in {"forensic", "hybrid_forensic"}:
            local = np.stack([forensic_features(im, size=self.spec.spectral_size) for im in images]).astype(np.float32)
        if self.feature_mode in {"clip", "hybrid", "hybrid_forensic"}:
            clip = self.clip_embeddings(images)
        if self.feature_mode in {"spectral", "forensic"}:
            return local
        if self.feature_mode == "clip":
            return clip
        return np.concatenate([clip, local], axis=1).astype(np.float32)

    def extract(self, image: Image.Image) -> np.ndarray:
        return self.extract_batch([image])[0]


def best_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _center_square(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    w, h = image.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return image.crop((left, top, left + side, top + side))


def _radial_profile(log_mag: np.ndarray, radius: np.ndarray, bins: int) -> np.ndarray:
    edges = np.linspace(0.0, 1.0, bins + 1)
    values = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (radius >= lo) & (radius < hi)
        values.append(float(log_mag[mask].mean()) if mask.any() else 0.0)
    out = np.asarray(values, dtype=np.float32)
    return (out - out.mean()) / (out.std() + 1e-6)


def _safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1).astype(np.float64)
    bb = b.reshape(-1).astype(np.float64)
    aa -= aa.mean()
    bb -= bb.mean()
    denom = math.sqrt(float(np.dot(aa, aa) * np.dot(bb, bb)))
    if denom < 1e-12:
        return 0.0
    return float(np.dot(aa, bb) / denom)


def spectral_features(
    image: Image.Image,
    bins: int = 32,
    residual_bins: int = 16,
    size: int = 256,
) -> np.ndarray:
    """Compact frequency + residual forensic fingerprint.

    Unlike the v1 branch, this includes a high-pass residual spectrum and
    channel-residual correlations. These are content-reduced signals intended
    to make it harder for the classifier to win using semantics alone.
    """
    img = _center_square(image).resize((size, size), Image.Resampling.LANCZOS)
    arr = np.asarray(img, dtype=np.float32) / 255.0

    gray = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    gray = gray - float(gray.mean())

    win = np.outer(np.hanning(size), np.hanning(size)).astype(np.float32)
    fft = np.fft.fftshift(np.fft.fft2(gray * win))
    mag = np.log1p(np.abs(fft)).astype(np.float32)

    yy, xx = np.indices((size, size))
    c = (size - 1) / 2.0
    radius = np.sqrt((xx - c) ** 2 + (yy - c) ** 2)
    radius = radius / radius.max()

    radial = _radial_profile(mag, radius, bins)

    # High-pass residual suppresses semantics and emphasizes local texture/noise.
    smooth = gaussian_filter(gray, sigma=1.0, mode="reflect")
    residual = gray - smooth
    rfft = np.fft.fftshift(np.fft.fft2(residual * win))
    rmag = np.log1p(np.abs(rfft)).astype(np.float32)
    residual_radial = _radial_profile(rmag, radius, residual_bins)

    power = np.square(np.abs(fft)).astype(np.float64)
    total = float(power.sum()) + 1e-12
    summaries = [float(power[radius >= cutoff].sum() / total) for cutoff in (0.25, 0.40, 0.55, 0.70)]

    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    edge_energy = float(np.mean(gx * gx) + np.mean(gy * gy))

    rstd = float(residual.std())
    rabs = float(np.abs(residual).mean())
    centered = residual - float(residual.mean())
    kurt = float(np.mean(centered**4) / (np.mean(centered**2) ** 2 + 1e-12))
    summaries.extend([math.log1p(max(edge_energy, 0.0)), rstd, rabs, math.log1p(max(kurt, 0.0))])

    # Correlation between high-pass RGB channel residuals.
    channel_res = []
    for k in range(3):
        ch = arr[..., k]
        channel_res.append(ch - gaussian_filter(ch, sigma=1.0, mode="reflect"))
    channel_corr = [
        _safe_corr(channel_res[0], channel_res[1]),
        _safe_corr(channel_res[0], channel_res[2]),
        _safe_corr(channel_res[1], channel_res[2]),
    ]

    out = np.concatenate(
        [
            radial,
            residual_radial,
            np.asarray(summaries, dtype=np.float32),
            np.asarray(channel_corr, dtype=np.float32),
        ]
    ).astype(np.float32)
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)



def _shift_corr(a: np.ndarray, dy: int, dx: int) -> float:
    h, w = a.shape
    y1 = slice(max(0, dy), min(h, h + dy))
    y2 = slice(max(0, -dy), min(h, h - dy))
    x1 = slice(max(0, dx), min(w, w + dx))
    x2 = slice(max(0, -dx), min(w, w - dx))
    return _safe_corr(a[y1, x1], a[y2, x2])


def forensic_features(image: Image.Image, size: int = 256) -> np.ndarray:
    """Richer local forensic fingerprint used by TrustLens v3.

    Extends the spectral branch with multi-scale residual statistics,
    residual autocorrelation, patch-noise dispersion, gradient/Laplacian
    distributions, a compact uniform-LBP histogram, and angular Fourier
    energy. The goal is to rely less on image semantics and more on local
    rendering/noise regularities.
    """
    img = _center_square(image).resize((size, size), Image.Resampling.LANCZOS)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    gray = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    feats: list[float] = spectral_features(img, size=size).astype(np.float64).tolist()

    for sigma in (0.5, 1.0, 2.0):
        residual = gray - gaussian_filter(gray, sigma=sigma, mode="reflect")
        centered = residual - float(residual.mean())
        var = float(np.mean(centered**2)) + 1e-12
        feats.extend([
            float(residual.std()),
            float(np.mean(np.abs(residual))),
            float(np.mean(centered**3) / (var**1.5)),
            float(np.mean(centered**4) / (var**2)),
        ])
        feats.extend(np.quantile(np.abs(residual), [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).tolist())
        for dy, dx in ((0,1),(1,0),(1,1),(1,-1),(0,2),(2,0),(0,4),(4,0),(0,8),(8,0)):
            feats.append(_shift_corr(residual, dy, dx))

        patch_std = []
        for py in range(4):
            for px in range(4):
                patch = residual[py*size//4:(py+1)*size//4, px*size//4:(px+1)*size//4]
                patch_std.append(float(patch.std()))
        feats.extend([float(np.mean(patch_std)), float(np.std(patch_std)), float(np.min(patch_std)), float(np.max(patch_std))])
        feats.extend(np.quantile(patch_std, [0.25, 0.5, 0.75]).tolist())

    # Gradient and Laplacian distributions.
    import cv2
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = np.sqrt(gx*gx + gy*gy)
    feats.extend(np.quantile(magnitude, [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).tolist())
    angle = (np.arctan2(gy, gx) + np.pi) % np.pi
    hist, _ = np.histogram(angle, bins=8, range=(0.0, np.pi), weights=magnitude)
    hist = hist.astype(np.float64) / (float(hist.sum()) + 1e-12)
    feats.extend(hist.tolist())
    lap = cv2.Laplacian(gray, cv2.CV_32F)
    feats.extend(np.quantile(np.abs(lap), [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).tolist())

    # Compact rotation-invariant-ish uniform local binary pattern histogram.
    center = gray[1:-1, 1:-1]
    neighbors = (
        gray[:-2,:-2], gray[:-2,1:-1], gray[:-2,2:], gray[1:-1,2:],
        gray[2:,2:], gray[2:,1:-1], gray[2:,:-2], gray[1:-1,:-2],
    )
    bits = np.stack([(n >= center) for n in neighbors], axis=0).astype(np.uint8)
    transitions = np.sum(bits != np.roll(bits, 1, axis=0), axis=0)
    ones = bits.sum(axis=0)
    code = np.where(transitions <= 2, ones, 9)
    lbp = np.bincount(code.ravel(), minlength=10).astype(np.float64)
    lbp /= float(lbp.sum()) + 1e-12
    feats.extend(lbp.tolist())

    # Directional Fourier energy can expose periodic/upsampling structure that
    # disappears from a radial spectrum.
    g0 = gray - float(gray.mean())
    window = np.outer(np.hanning(size), np.hanning(size)).astype(np.float32)
    fft = np.fft.fftshift(np.fft.fft2(g0 * window))
    power = np.square(np.abs(fft)).astype(np.float64)
    yy, xx = np.indices((size, size))
    c = (size - 1) / 2.0
    dx, dy = xx - c, yy - c
    radius = np.sqrt(dx*dx + dy*dy)
    radius /= radius.max()
    theta = (np.arctan2(dy, dx) + np.pi) % np.pi
    high = radius > 0.2
    angular, _ = np.histogram(theta[high], bins=12, range=(0.0, np.pi), weights=power[high])
    angular = angular.astype(np.float64) / (float(angular.sum()) + 1e-12)
    feats.extend(angular.tolist())

    # Multi-scale detail energies and basic color statistics.
    current = gray.copy()
    for _ in range(3):
        blurred = gaussian_filter(current, sigma=1.0, mode="reflect")
        detail = current - blurred
        feats.extend([float(detail.std()), float(np.mean(np.abs(detail)))])
        feats.extend(np.quantile(np.abs(detail), [0.9, 0.99]).tolist())
        current = cv2.resize(blurred, (current.shape[1]//2, current.shape[0]//2), interpolation=cv2.INTER_AREA)

    pixels = arr.reshape(-1, 3)
    feats.extend(pixels.mean(axis=0).tolist())
    feats.extend(pixels.std(axis=0).tolist())
    out = np.asarray(feats, dtype=np.float32)
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)

def jpeg_roundtrip(image: Image.Image, quality: int) -> Image.Image:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=int(quality), optimize=False)
    buf.seek(0)
    with Image.open(buf) as decoded:
        return decoded.convert("RGB")


def transformed_view(image: Image.Image, mode: str) -> Image.Image:
    """Deterministic robustness transforms used for train/evaluation."""
    img = image.convert("RGB")
    if mode == "clean":
        return img
    if mode == "jpeg85":
        return jpeg_roundtrip(img, 85)
    if mode == "jpeg60":
        return jpeg_roundtrip(img, 60)
    if mode == "jpeg40":
        return jpeg_roundtrip(img, 40)
    if mode == "blur05":
        return img.filter(ImageFilter.GaussianBlur(radius=0.5))
    if mode == "blur":
        return img.filter(ImageFilter.GaussianBlur(radius=1.0))
    if mode in {"resize75", "resize50"}:
        frac = 0.75 if mode == "resize75" else 0.50
        w, h = img.size
        small = img.resize((max(32, int(w * frac)), max(32, int(h * frac))), Image.Resampling.LANCZOS)
        return small.resize((w, h), Image.Resampling.LANCZOS)
    if mode in {"crop95", "crop90"}:
        frac = 0.95 if mode == "crop95" else 0.90
        w, h = img.size
        nw, nh = max(32, int(w * frac)), max(32, int(h * frac))
        left, top = (w - nw) // 2, (h - nh) // 2
        crop = img.crop((left, top, left + nw, top + nh))
        return crop.resize((w, h), Image.Resampling.LANCZOS)
    if mode == "screenshot_like":
        w, h = img.size
        scale = 0.82
        small = img.resize((max(32, int(w * scale)), max(32, int(h * scale))), Image.Resampling.BILINEAR)
        restored = small.resize((w, h), Image.Resampling.BILINEAR)
        restored = ImageEnhance.Contrast(restored).enhance(1.02)
        return jpeg_roundtrip(restored, 82)
    raise ValueError(f"Unknown transform mode: {mode}")


def load_image(path: str | Path) -> Image.Image:
    with Image.open(path) as im:
        return im.convert("RGB")
