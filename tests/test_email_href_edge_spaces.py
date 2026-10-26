"""Frozen additional href boundary expectations, before implementation."""
from email.message import EmailMessage
import pytest
from app.analyzers.email import analyze_email,analyze_email_bytes,VisibleText,href_target

@pytest.mark.parametrize('space',['\u00a0','\u2003','\u3000','\u2028'])
@pytest.mark.parametrize('value',['//bank.example/','https://bank.example/','#section',''])
@pytest.mark.parametrize('side',['leading','trailing'])
def test_nonascii_whitespace_unsupported_before_normalization(space,value,side):
    raw=space+value if side=='leading' else value+space
    assert href_target(raw)==('unsupported',None)
    p=VisibleText();p.feed('<a href="'+raw+'">Open</a>');p.finish_anchor()
    assert p.uninspected_targets==1 and p.links==[] and p.anchors==[]

@pytest.mark.parametrize('as_bytes',[False,True])
@pytest.mark.parametrize('value',['\u00a0//bank.example/','https://bank.example/\u2003','\u3000https://-invalid.example/','\u2028#section'])
def test_paste_and_bytes_count_without_invented_host_or_transport(value,as_bytes):
    m=EmailMessage();m.set_content('<a href="'+value+'">Open</a>',subtype='html',charset='utf-8')
    r=analyze_email_bytes(m.as_bytes()) if as_bytes else analyze_email(m.as_string())
    partial=[e for e in r.evidence if e.id=='email:links_incomplete']
    assert len(partial)==1 and partial[0].weight==0
    assert not any(e.id.startswith(('url:host','url:http','email:link_mismatch')) for e in r.evidence)

@pytest.mark.parametrize('value,kind,host',[(' //bank.example/ ','relative_host','bank.example'),(' https://bank.example/ ','web','bank.example'),(' //straße.example/😀 ','relative_host','xn--strae-oqa.example'),(' https://例え.テスト/😀 ','web','xn--r8jz45g.xn--zckzah'),('   ','none',None),(' #section ','none',None)])
def test_ascii_edge_space_unicode_host_and_astral_controls(value,kind,host):
    assert href_target(value)==(kind,host)

@pytest.mark.parametrize('value',['\t//bank.example/','//bank.\u200bexample/','https://bank.example/\u202e','https://bank.example/\ud800'])
def test_existing_hidden_control_rejection_remains(value):assert href_target(value)==('unsupported',None)
