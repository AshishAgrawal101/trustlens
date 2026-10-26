import numpy as np

from ai_detector.train import collapse_worst_case, pick_ai_threshold, pick_real_threshold, selective_summary


def test_ai_threshold_can_reject_everything_to_meet_fpr():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.99, 0.98, 0.60, 0.55])
    t, stats = pick_ai_threshold(y, p, target_fpr=0.0)
    assert stats["fpr"] == 0.0
    assert t > 0.99


def test_real_threshold_limits_fake_certification():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.05, 0.10, 0.40, 0.90])
    t, stats = pick_real_threshold(y, p, target_fake_as_real=0.0)
    assert stats["fake_as_real"] == 0.0
    assert t < 0.40


def test_selective_summary_has_unresolved_region():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.01, 0.45, 0.55, 0.99])
    m = selective_summary(y, p, real_threshold=0.10, ai_threshold=0.90)
    assert m["coverage"] == 0.5
    assert m["unresolved_rate"] == 0.5
    assert m["selective_accuracy"] == 1.0


def test_worst_case_collapse_uses_max_for_real_min_for_fake():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.7, 0.9, 0.4])
    paths = ["real.png", "real.png#aug=jpeg", "fake.png", "fake.png#aug=jpeg"]
    yy, pp = collapse_worst_case(y, p, paths)
    assert yy.tolist() == [0, 1]
    assert np.allclose(pp, [0.7, 0.4])
