"""HTML comparison display limits disclose omitted distinct differences, not uninspected targets."""
import pytest
from app.analyzers.email import link_label_evidence,analyze_email,analyze_email_bytes
from app.guidance import add_guidance
NOTICE='Only the first 8 distinct HTML address differences were displayed; additional differences were omitted.'

def anchors(n,kind='mailto'):
    return [(('mailto:office@destination'+str(i)+'.example') if kind=='mailto' else ('//' if kind=='relative' else 'https://')+'destination'+str(i)+'.example/PRIVATE?token=SECRET',('office@shown'+str(i)+'.example') if kind=='mailto' else 'https://shown'+str(i)+'.example') for i in range(n)]

def raw(items):return 'Content-Type: text/html; charset=ascii\n\n'+''.join('<a href="'+h+'">'+l+'</a> ' for h,l in items)
def weighted(rows):return [e.model_dump() for e in rows if e.weight>0]

@pytest.mark.parametrize('kind',['mailto','web','relative'])
def test_eight_vs_nine_preserves_original_rows_and_adds_count_only_notice(kind):
    eight=link_label_evidence(anchors(8,kind));nine=link_label_evidence(anchors(9,kind))
    assert isinstance(nine,list) and weighted(nine)==weighted(eight)
    assert len(eight)==8 and not any(e.id=='email:label_limit' for e in eight)
    notice=[e for e in nine if e.id=='email:label_limit'];assert len(notice)==1
    e=notice[0];assert (e.evidence_class,e.severity,e.weight)==('unknown','info',0)
    assert '1' in e.detail and 'not displayed' in e.detail
    assert not any(x in e.detail for x in ['destination8.example','shown8.example','office@','PRIVATE','SECRET','uninspected','not inspected'])

def test_duplicate_ninth_and_equal_first_eight_do_not_consume_unique_difference_budget():
    rows=anchors(8);assert link_label_evidence(rows+[rows[0]])==link_label_evidence(rows)
    equal=[('mailto:office@same'+str(i)+'.example','office@same'+str(i)+'.example') for i in range(8)]
    assert len(link_label_evidence(equal+anchors(1)))==1

@pytest.mark.parametrize('mode',['paste','eml'])
def test_report_exports_fixed_display_reason_without_scoring_actions_or_private_echo(mode):
    run=lambda items:add_guidance(analyze_email(raw(items)) if mode=='paste' else analyze_email_bytes(raw(items).encode()))
    before=run(anchors(8));after=run(anchors(10))
    assert after.risk_level==before.risk_level=='guarded' and after.actions==before.actions
    assert weighted(after.evidence)==weighted(before.evidence)
    assert NOTICE in after.share_summary and NOTICE not in before.share_summary
    assert any('not displayed' in x for x in after.limitations)
    assert not any(e.id=='email:links_incomplete' for e in after.evidence)
    assert not any(x in after.share_summary for x in ['destination0.example','shown0.example','office@','PRIVATE','SECRET'])

def test_multipart_dedup_is_global_and_independent_coverage_high_request_survives():
    first=raw(anchors(8));second=raw(anchors(8)+anchors(10)[8:])+'<a href="relative-path">Account</a><p>Send me your verification code.</p>'
    message='Content-Type: multipart/alternative; boundary=p\n\n--p\n'+first+'\n--p\n'+second+'\n--p--\n'
    r=add_guidance(analyze_email(message));notice=next(e for e in r.evidence if e.id=='email:label_limit')
    assert '2' in notice.detail
    assert {'email:links_incomplete','request:code'} <= {e.id for e in r.evidence}
    assert r.risk_level=='high' and NOTICE in r.share_summary
    assert 'targets were not inspected' in r.share_summary
    assert sum(e.id.startswith('email:link_mismatch:') for e in r.evidence)==8

@pytest.mark.parametrize('mode',['paste','eml'])
def test_display_limit_is_independent_of_all_existing_link_coverage_reasons(mode):
    content=raw(anchors(9))+'<a href="relative-path">Account</a><p>https://example.org:BAD '+ ' '.join('https://valid'+str(i)+'.example/' for i in range(8))+'</p>'
    r=add_guidance(analyze_email(content) if mode=='paste' else analyze_email_bytes(content.encode()))
    ids={e.id for e in r.evidence}
    assert {'email:label_limit','email:links_incomplete','analysis:links_incomplete','url:malformed:0'} <= ids
    assert NOTICE in r.share_summary and 'could not be parsed' in r.share_summary
    assert 'Only the first 8 unique literal links were inspected.' in r.share_summary
    assert 'targets were not inspected' in r.share_summary
