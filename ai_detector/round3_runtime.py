"""Frozen original/adapted encoders with explicitly compatible classifier heads."""
import gc
from pathlib import Path

import joblib
import numpy as np
import torch

from ai_detector.adaptation import assert_feature_contract,load_visual,representation
from ai_detector.image_ensemble import digest

def verify_frozen(frozen,clip_cache,community_weights):
    files=list(Path(clip_cache).rglob('open_clip_model.safetensors'))
    if len(files)!=1: raise ValueError('Select exactly one original CLIP checkpoint')
    base={'clip':digest(files[0]),'community':digest(Path(community_weights))}
    for c in frozen['components']:
        d=c['descriptor']; bound=c['classifier_encoder_contract']
        assert_feature_contract(d['contract'],bound)
        if c['branch']!=d['branch'] or d['contract']['branch']!=c['branch']:
            raise ValueError('Classifier encoder branch mismatch')
        if d['contract']['base_weights_sha256']!=base[c['branch']]: raise ValueError('Original encoder integrity failure')
        checkpoint=d.get('checkpoint')
        expected=d['contract']['weights_sha256']
        if (digest(Path(checkpoint)) if checkpoint else base[c['branch']])!=expected:
            raise ValueError('Visual encoder checkpoint integrity failure')
        if digest(Path(c['classifier']))!=c['classifier_sha256']: raise ValueError('Classifier integrity failure')
    if frozen.get('combination') and digest(Path(frozen['combination']['path']))!=frozen['combination']['sha256']:
        raise ValueError('Combination classifier integrity failure')

class Round3Runtime:
    def __init__(self,frozen,clip_cache,community_weights,device):
        verify_frozen(frozen,clip_cache,community_weights)
        self.frozen=frozen; self.device=device; self.encoders={}; self.preprocess={}; self.classifiers={}
        for c in frozen['components']:
            key=c['branch']+':'+c['descriptor']['contract']['weights_sha256']
            if key not in self.encoders:
                self.encoders[key],self.preprocess[key]=load_visual(c['branch'],clip_cache,community_weights,
                                                                 c['descriptor'].get('checkpoint'),device)
            self.classifiers[c['name']]=joblib.load(c['classifier'])
        self.combination=joblib.load(frozen['combination']['path']) if frozen.get('combination') else None
    def score_details(self,image):
        representations={}; scores={}; branch={'clip':[],'community':[]}
        with torch.inference_mode():
            for c in self.frozen['components']:
                key=c['branch']+':'+c['descriptor']['contract']['weights_sha256']
                if key not in representations:
                    x=self.preprocess[key](image).unsqueeze(0).to(self.device)
                    representations[key]=representation(self.encoders[key],c['branch'],x).float().cpu().numpy()
                score=float(self.classifiers[c['name']].predict_proba(representations[key])[0,1])
                scores[c['name']]=score; branch[c['branch']].append(score)
        recipe=self.frozen['recipe']
        if recipe=='feature_fusion':
            values=np.concatenate([representations[c['branch']+':'+c['descriptor']['contract']['weights_sha256']]
                                   for c in self.frozen['components']],axis=1)
            combined=float(self.combination.predict_proba(values)[0,1])
        elif recipe=='score_fusion':
            p=np.clip([scores[c['name']] for c in self.frozen['components']],1e-6,1-1e-6)
            combined=float(self.combination.predict_proba(np.log(p/(1-p)).reshape(1,-1))[0,1])
        elif recipe=='mean': combined=float(np.mean(list(scores.values())))
        elif recipe in branch: combined=float(np.mean(branch[recipe]))
        else: raise ValueError('Unknown frozen combination recipe')
        return {'combined':combined,'clip_probe':float(np.mean(branch['clip'])),'community':float(np.mean(branch['community']))}

def installed_frozen(root,metadata):
    """Installed metadata names files inside models, never arbitrary outside paths."""
    import copy
    frozen=copy.deepcopy(metadata['frozen_model'])
    directory=(Path(root)/'models').resolve()
    def local(filename):
        path=(directory/filename).resolve()
        if path.parent!=directory: raise ValueError('Model artifact escaped the model directory')
        return str(path)
    for c in frozen['components']:
        c['classifier']=local(c['classifier'])
        if c['descriptor'].get('checkpoint'): c['descriptor']['checkpoint']=local(c['descriptor']['checkpoint'])
    if frozen.get('combination'): frozen['combination']['path']=local(frozen['combination']['path'])
    return frozen
