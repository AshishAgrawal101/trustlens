"""Fake-runtime pixel cleanup: never imports a scientific model runtime."""
import ast
import hashlib
from pathlib import Path
from types import SimpleNamespace
import pytest
from PIL import Image
from app.analyzers import image as module

ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/'tests/fixtures/frozen_v14_image.py.txt'


def old_source():
    source=FROZEN.read_bytes()
    assert hashlib.sha256(source).hexdigest()=='414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6'
    return source


def runtime(mode):
    def score(image):
        assert image.getpixel((0,0))==(11,22,33)
        if mode=='score':raise RuntimeError('fake failure')
        return .2
    result=SimpleNamespace(score=score,threshold=.35,metadata={'evaluation':{'accuracy':.5,'n':2,'accuracy_wilson_95_interval':[.1,.9]}},robustness=None)
    if mode=='components':result.score_details=lambda image: {'combined':None}
    return result


@pytest.mark.parametrize('mode',['load','score','components','success'])
def test_explicit_close_even_with_retained_exception(mode,monkeypatch):
    image=Image.new('RGB',(2,2),(11,22,33))
    monkeypatch.setattr(module,'decode_image',lambda content:image)
    def load():
        if mode=='load':raise RuntimeError('fake load')
        return runtime(mode)
    monkeypatch.setattr(module,'load_runtime',load)
    retained=None
    try:
        if mode=='success':assert module.analyze_image(b'fake').summary=='Photograph patterns detected (experimental)'
        else:
            with pytest.raises(module.ImageModelUnavailable) as error:module.analyze_image(b'fake')
            retained=error.value
        with pytest.raises(ValueError,match='closed'):image.getpixel((0,0))
        assert not module._lock.locked()
    finally:image.close()


def test_body_ast_unchanged_from_frozen_v14_except_closing_wrapper():
    old=ast.parse(old_source());new=ast.parse(Path(module.__file__).read_text())
    old_fn=next(node for node in old.body if isinstance(node,ast.FunctionDef) and node.name=='_analyze_image')
    new_fn=next(node for node in new.body if isinstance(node,ast.FunctionDef) and node.name=='_analyze_image')
    wrapper=new_fn.body[0]
    assert len(new_fn.body)==1 and isinstance(wrapper,ast.With)
    assert ast.dump(wrapper.items[0].context_expr)=="Call(func=Name(id='closing', ctx=Load()), args=[Call(func=Name(id='decode_image', ctx=Load()), args=[Name(id='content', ctx=Load())], keywords=[])], keywords=[])"
    assert ast.dump(wrapper.items[0].optional_vars)=="Name(id='image', ctx=Store())"
    assert [ast.dump(node) for node in old_fn.body[1:]]==[ast.dump(node) for node in wrapper.body]
    # Entire module equals the original after reversing the authorized wrapper/import.
    new_fn.body=old_fn.body
    new.body=[node for node in new.body if not (isinstance(node,ast.ImportFrom) and node.module=='contextlib')]
    assert ast.dump(new)==ast.dump(old)


def test_success_report_identical_to_frozen_body(monkeypatch):
    namespace={'__name__':module.__name__}
    tree=ast.parse(old_source())
    old_fn=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='_analyze_image')
    namespace.update(vars(module))
    exec(compile(ast.Module(body=[old_fn],type_ignores=[]),'<frozen-v14-function>','exec'),namespace)
    images=[]
    def decode(content):
        image=Image.new('RGB',(2,2),(11,22,33));images.append(image);return image
    monkeypatch.setattr(module,'decode_image',decode);monkeypatch.setattr(module,'load_runtime',lambda:runtime('success'))
    namespace.update(decode_image=decode,load_runtime=lambda:runtime('success'))
    try:
        old=namespace['_analyze_image'](b'fake').model_dump()
        new=module._analyze_image(b'fake').model_dump()
        assert old==new
    finally:
        for image in images:image.close()
