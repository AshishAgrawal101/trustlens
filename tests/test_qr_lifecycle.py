"""QR pixel lifetime; constructed image and fake worker, no native decode."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from PIL import Image
from app.analyzers import qr


@pytest.mark.parametrize('failure',[False,True])
def test_qr_explicitly_closes_pixels_and_temp_on_worker_exit(monkeypatch,failure):
    image=Image.new('RGB',(2,2));paths=[]
    monkeypatch.setattr(qr,'decode_image',lambda content:image)
    def run(args,**kwargs):
        paths.append(Path(args[-2]));assert paths[0].exists()
        return SimpleNamespace(returncode=int(failure),stdout=json.dumps({'codes':['Read only']}).encode())
    monkeypatch.setattr(qr.subprocess,'run',run)
    try:
        if failure:
            with pytest.raises(qr.QrUnavailable):qr.extract_qr(b'image')
        else:assert qr.extract_qr(b'image')['codes']==['Read only']
        with pytest.raises(ValueError,match='closed'):image.getpixel((0,0))
        assert not paths[0].exists() and not qr._lock.locked()
    finally:image.close()
