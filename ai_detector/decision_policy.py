"""One decision rule shared by validation, acceptance checks and the app."""
import math


def validate_policy(policy):
    if policy is None:
        return
    if policy.get('kind') != 'fusion_margin_v1':
        raise ValueError('Unsupported image decision policy')
    lower, upper = policy['lower'], policy['upper']
    if not (math.isfinite(lower) and math.isfinite(upper) and 0 <= lower < .5 < upper <= 1):
        raise ValueError('Invalid image uncertainty bounds')


def is_inconclusive(scores, policy=None):
    validate_policy(policy)
    if not all(math.isfinite(scores[k]) and 0 <= scores[k] <= 1
               for k in ('combined', 'clip_probe', 'community')):
        raise ValueError('Invalid image model score')
    if policy is None:
        return (scores['clip_probe'] >= .5) != (scores['community'] >= .5)
    return policy['lower'] < scores['combined'] < policy['upper']
