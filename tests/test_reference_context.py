"""Finite-template development controls; no population-accuracy claim."""
import pytest

from app.analyzers.text import analyze_text
from app.guidance import add_guidance
from app.models import Evidence

ANTECEDENTS = [
    f'A {kind} code should arrive by text{suffix}'
    for kind in ('login', 'verification', 'security') for suffix in ('', ' in a moment')
] + [
    f'Your {app} has {just}sent {code}'
    for app in ('banking app', 'app') for just in ('', 'just ')
    for code in ('a login code', 'a verification code', 'a security code', 'a one-time passcode')
]
REQUESTS = [
    f'Tell me those six numbers{when}{why}'
    for when in ('', ' when you see them') for why in ('', ' so I can complete the sign-in')
] + ['Reply here with those characters', 'Reply here with those characters so I can cancel the attempted login']
CODE_ACTION = 'Keep security codes and passwords private'
PAIR = ANTECEDENTS[0] + '. ' + REQUESTS[0] + '.'


@pytest.mark.parametrize('antecedent', ANTECEDENTS)
@pytest.mark.parametrize('disclosure', REQUESTS)
def test_finite_templates_produce_only_precautionary_unknown(antecedent, disclosure):
    text = antecedent + '. ' + disclosure + '.'
    report = add_guidance(analyze_text(text))
    assert len(report.evidence) == 1
    item = report.evidence[0]
    assert (item.id, item.evidence_class, item.severity, item.weight) == ('reference:code', 'unknown', 'info', 0)
    assert item.title == 'Possible security-code reference'
    assert 'unknown' in item.detail and antecedent not in item.detail and disclosure not in item.detail
    assert report.risk_index is None and report.risk_level == 'low' and report.confidence == 'low'
    assert CODE_ACTION in {action.title for action in report.actions}
    assert 'Verify through a separate route' in {action.title for action in report.actions}
    assert '0 wording or address warning sign(s)' in report.share_summary
    assert text not in report.share_summary and antecedent not in report.share_summary


@pytest.mark.parametrize('text', [
    'Your seat reservation reference should arrive by text in a moment. Tell the staffed box office those six numbers when you collect the tickets.',
    'The classroom poster has a six-character puzzle answer. Reply on the class worksheet with those characters after you solve it. No account sign-in is involved.',
    'A login code should arrive by text. Do not tell me those six numbers.',
    'Your banking app has sent a one-time passcode. Never reply here with those characters.',
    'No one-time passcode was sent. Reply here with those characters.',
    'A login code should not arrive by text. Tell me those six numbers.',
    'A login code should arrive by text. Your ticket reference is also six numbers. Tell me those six numbers.',
    'A login code should arrive by text and a ticket reference should arrive too. Tell me those six numbers.',
    'Your banking app has sent a one-time passcode. Reply here with those characters from the puzzle.',
    'A login code should arrive by text. If someone asks you to tell them those six numbers, hang up.',
    "Our completed poster includes the fake example 'A login code should arrive by text. Tell me those six numbers.'",
    'A login code should arrive by text.\nTell me those six numbers.',
    'A login code should arrive by text.\n\nTell me those six numbers.',
    'A login code should arrive by text! Tell me those six numbers.',
    'A login code should arrive by text? Tell me those six numbers.',
    'A login code should arrive by text.Tell me those six numbers.',
    'A login code should arrive by text; tell me those six numbers.',
    'A login code should arrive by text. Something else. Tell me those six numbers.',
    'A login code should arrive by text' + ' ' * 161 + 'extra. Tell me those six numbers.',
    'A login code should arrive by text. Tell me those six numbers' + ' ' * 161 + 'extra.',
    'A login code should arrive by text. Tell me those six numbers, please.',
    'A login code should arrive by text. Reply with those characters.',
])
def test_negated_conflicting_ordinary_and_out_of_scope_references_are_not_guessed(text):
    report = add_guidance(analyze_text(text))
    assert not any(item.id == 'reference:code' for item in report.evidence)
    assert CODE_ACTION not in {action.title for action in report.actions}


def test_later_live_request_and_call_guidance_survive():
    report = add_guidance(analyze_text(PAIR + ' Send me your verification code.', 'call'))
    assert {'reference:code', 'request:code'} <= {item.id for item in report.evidence}
    assert report.risk_level == 'high'
    assert next(item for item in report.evidence if item.id == 'request:code').weight > 0
    titles = [action.title for action in report.actions]
    assert titles.count(CODE_ACTION) == 1
    assert 'End the call and call back independently' in titles


def test_reference_never_displaces_payment_or_remote_actions_and_share_stays_input_free():
    live = 'Send $700 to PRIVATE-ACCOUNT. Install TeamViewer.'
    baseline = add_guidance(analyze_text(live))
    report = add_guidance(analyze_text(PAIR + ' ' + live))
    assert {'request:payment', 'request:remote', 'reference:code'} <= {item.id for item in report.evidence}
    assert report.risk_level == 'high'
    titles = [action.title for action in report.actions]
    assert titles == [action.title for action in baseline.actions]
    assert titles[:2] == ['Pause the payment', 'Keep control of your device']
    assert CODE_ACTION not in titles
    assert 'PRIVATE-ACCOUNT' not in report.share_summary
    assert 'PRIVATE-ACCOUNT' not in next(item for item in report.evidence if item.id == 'reference:code').detail


@pytest.mark.parametrize('live,first', [
    ('Send $700 to this account.', 'Pause the payment'),
    ('Install TeamViewer.', 'Keep control of your device'),
])
def test_reference_uses_only_spare_action_slot(live, first):
    report = add_guidance(analyze_text(live + ' ' + PAIR))
    assert [action.title for action in report.actions] == [first, CODE_ACTION, 'Verify through a separate route']


def test_existing_payment_and_code_actions_keep_order_without_duplicate():
    live = 'Send $700 to this account. Send me your verification code.'
    baseline = add_guidance(analyze_text(live))
    report = add_guidance(analyze_text(live + ' ' + PAIR))
    assert [action.title for action in report.actions] == [action.title for action in baseline.actions]
    assert [action.title for action in report.actions][:2] == ['Pause the payment', CODE_ACTION]


@pytest.mark.parametrize('evidence_id,second', [
    ('email:incomplete', 'Review the original email'),
    ('url:userinfo:0', 'Use a known address instead of this link'),
])
def test_reference_preserves_existing_address_and_incomplete_email_slots(evidence_id, second):
    original = analyze_text('Send $700 to this account.')
    original.evidence.append(Evidence(id=evidence_id, evidence_class='unknown', severity='info',
                                      title='Synthetic', detail='Synthetic', source='Synthetic'))
    baseline = add_guidance(original.model_copy(deep=True))
    original.evidence.extend(analyze_text(PAIR).evidence)
    report = add_guidance(original)
    assert [action.title for action in report.actions] == [action.title for action in baseline.actions]
    assert [action.title for action in report.actions][:2] == ['Pause the payment', second]
    assert CODE_ACTION not in {action.title for action in report.actions}


@pytest.mark.parametrize('text', [
    "Our completed poster includes the fake example 'Reply with your password.'",
    'If someone asks you to read a verification code, stop.',
])
def test_existing_context_does_not_receive_reference_action(text):
    report = add_guidance(analyze_text(text))
    assert 'context:code' in {item.id for item in report.evidence}
    assert CODE_ACTION not in {action.title for action in report.actions}


@pytest.mark.parametrize('classification,weight', [('inferred', 0), ('unknown', .8)])
def test_routing_requires_exact_unknown_zero_contract(classification, weight):
    report = analyze_text('Ordinary message.')
    report.evidence = [Evidence(id='reference:code', evidence_class=classification, severity='info',
                                weight=weight, title='Synthetic', detail='Synthetic', source='Synthetic')]
    assert CODE_ACTION not in {action.title for action in add_guidance(report).actions}


def test_deduplicates_repeated_pairs():
    report = add_guidance(analyze_text(PAIR + ' ' + PAIR))
    assert sum(item.id == 'reference:code' for item in report.evidence) == 1


def test_case_and_horizontal_separator():
    report = add_guidance(analyze_text(PAIR.upper().replace('. ', '.\t')))
    assert 'reference:code' in {item.id for item in report.evidence}
