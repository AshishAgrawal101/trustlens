import json
from pathlib import Path
import sys

import numpy as np
import pytest

from ai_detector.decision_policy import is_inconclusive, validate_policy



def scores(combined, clip=.8, community=.02):
    return {'combined': combined, 'clip_probe': clip, 'community': community}


def test_disagreement_can_be_resolved_only_by_explicit_validated_policy():
    policy = {'kind': 'fusion_margin_v1', 'lower': .4, 'upper': .6}
    assert is_inconclusive(scores(.02))
    assert not is_inconclusive(scores(.02), policy)
    assert is_inconclusive(scores(.52), policy)
    assert not is_inconclusive(scores(.4), policy)
    assert not is_inconclusive(scores(.6), policy)
    with pytest.raises(ValueError):
        validate_policy({**policy, 'lower': float('nan')})
    with pytest.raises(ValueError):
        is_inconclusive(scores(float('nan')), policy)

