import numpy as np
from PIL import Image

from ai_detector.features import HybridFeatureExtractor, spectral_features, transformed_view


def test_spectral_shape_and_finite():
    img = Image.new("RGB", (320, 240), (128, 128, 128))
    x = spectral_features(img, bins=32, residual_bins=16, size=128)
    assert x.shape == (59,)
    assert np.isfinite(x).all()


def test_spectral_only_extractor_needs_no_clip_dependency():
    img = Image.new("RGB", (128, 128), (100, 120, 140))
    extractor = HybridFeatureExtractor(feature_mode="spectral")
    x = extractor.extract(img)
    assert x.shape == (59,)
    assert np.isfinite(x).all()


def test_transforms_keep_valid_images():
    img = Image.new("RGB", (320, 240), (120, 130, 140))
    for mode in [
        "clean", "jpeg85", "jpeg60", "jpeg40", "blur05", "blur",
        "resize75", "resize50", "crop95", "crop90", "screenshot_like",
    ]:
        out = transformed_view(img, mode)
        assert isinstance(out, Image.Image)
        assert out.size == img.size


def test_forensic_features_are_finite_and_richer():
    from ai_detector.features import forensic_features, spectral_features
    img = Image.new("RGB", (96, 80), (120, 80, 40))
    f = forensic_features(img, size=128)
    s = spectral_features(img, size=128)
    assert f.ndim == 1
    assert len(f) > len(s)
    assert np.isfinite(f).all()


def test_forensic_extractor_mode():
    extractor = HybridFeatureExtractor(feature_mode="forensic")
    img = Image.new("RGB", (64, 64), (10, 30, 80))
    f = extractor.extract(img)
    assert f.ndim == 1
    assert np.isfinite(f).all()
