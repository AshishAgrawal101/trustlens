import io
import pytest
from PIL import Image
from app.analyzers.image import analyze_image


@pytest.mark.parametrize('clip,community,level', [
    (.8578,.00000037,'guarded'),
    (.6858,.1234,'guarded'),
    (.8,.9,'high'),
    (.1,.2,'low'),
])
def test_disagreement_is_inconclusive_without_changing_combined_score(monkeypatch,clip,community,level):
    class Pipeline:
        threshold=.35
        robustness=None
        metadata={'evaluation':{'accuracy':.9507462687,'n':670,'accuracy_wilson_95_interval':[.9316,.9647]}}
        def score_details(self,image):
            return {'clip_probe':clip,'community':community,'combined':(clip+community)/2}
        def score(self,image):
            raise AssertionError('Must compute the component scores only once')
    monkeypatch.setattr('app.analyzers.image.load_runtime',lambda:Pipeline())
    buffer=io.BytesIO()
    Image.new('RGB',(20,24)).save(buffer,format='PNG')
    report=analyze_image(buffer.getvalue())
    assert report.risk_index==round(50*(clip+community))
    assert report.risk_level==level
    assert {'image:clip','image:community'}<={q.id for q in report.evidence}
    assert any('cutoff 35.0' in q.detail for q in report.evidence)
    if level=='guarded':
        assert 'inconclusive' in report.summary
        assert any(q.id=='image:disagreement' for q in report.evidence)
        assert any('not counted as correct' in item for item in report.limitations)
