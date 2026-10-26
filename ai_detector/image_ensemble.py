"""The exact CLIP + CommunityForensics pipeline frozen before external testing."""
import hashlib
import json
import os
from pathlib import Path


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source,'sha256').hexdigest()


class ImageEnsemble:
    def __init__(self,root,clip_cache,device):
        import joblib
        from ai_detector.frozen_vision import load_backbone
        from ai_detector.community import load_community
        self.metadata=json.loads((root/'models/image_pipeline.json').read_text())
        self.pipeline=self.metadata['pipeline']
        if self.pipeline=='clip_community_adapted_v4':
            from ai_detector.round3_runtime import Round3Runtime,installed_frozen
            from ai_detector.decision_policy import validate_policy
            validate_policy(self.metadata.get('decision_policy'))
            community=Path(os.environ.get('TRUSTLENS_COMMUNITY_WEIGHTS',
                str(root.parent.parent/'work/community-forensics/model.safetensors')))
            self._round3=Round3Runtime(installed_frozen(root,self.metadata),clip_cache,community,device)
            self.threshold=.5
            self.robustness={'metrics':self.metadata['jpeg60_evaluation']}
            return
        if self.pipeline not in {'clip_community_v1','clip_community_full_v2','clip_community_full_v3'}:
            raise ValueError('Unsupported image pipeline')
        from ai_detector.decision_policy import validate_policy
        validate_policy(self.metadata.get('decision_policy'))
        self.threshold=float(self.metadata['threshold'])
        self.clip_weight=float(self.metadata.get('clip_weight',.5))
        if not 0<self.threshold<1 or not 0<=self.clip_weight<=1:
            raise ValueError('Invalid image pipeline thresholds')
        if self.pipeline=='clip_community_v1':
            probe=root/'models/clip_external_probe.joblib'
            if digest(probe)!=self.metadata['classifier_sha256']:
                raise ValueError('Image classifier failed its integrity check')
        else:
            files=self.metadata['classifiers']
            for branch,item in files.items():
                path=root/'models'/item['filename']
                if path.resolve().parent!=(root/'models').resolve() or digest(path)!=item['sha256']:
                    raise ValueError('Image classifier failed its integrity check: '+branch)
            probe=root/'models'/files['clip']['filename']
            self.community_classifier=joblib.load(root/'models'/files['community']['filename'])
            self.fusion_classifier=joblib.load(root/'models'/files['fusion']['filename'])
            self.deployment_candidate=self.metadata['deployment_candidate']
            if self.deployment_candidate not in {'clip','community','fusion','feature_fusion'}:
                raise ValueError('Invalid image deployment candidate')
            if self.deployment_candidate=='feature_fusion':
                self.feature_fusion_classifier=joblib.load(root/'models'/files['feature_fusion']['filename'])
        clip_weights=list(Path(clip_cache).rglob('open_clip_model.safetensors'))
        if len(clip_weights)!=1 or digest(clip_weights[0])!=self.metadata['clip_weights_sha256']:
            raise ValueError('CLIP weights are missing or failed their integrity check')
        community=Path(os.environ.get('TRUSTLENS_COMMUNITY_WEIGHTS',
            str(root.parent.parent/'work/community-forensics/model.safetensors')))
        if not community.is_file():
            raise ValueError('CommunityForensics weights are not installed. See README.md.')
        if digest(community)!=self.metadata['community_weights_sha256']:
            raise ValueError('CommunityForensics weights failed their integrity check')
        self.encoder,self.preprocess,_=load_backbone('clip_l14',clip_cache,device)
        self.community,self.community_preprocess=load_community(community)
        self.community.to(device)
        self.classifier=joblib.load(probe)
        self.device=device
        robustness=root/Path(self.metadata['evaluation_report']).parent/'robustness_jpeg60.json'
        self.robustness=({'metrics':self.metadata['jpeg60_evaluation']} if self.pipeline!='clip_community_v1'
            else json.loads(robustness.read_text()) if robustness.is_file() else None)

    def score_details(self,image):
        if hasattr(self,'_round3'): return self._round3.score_details(image)
        import torch
        with torch.inference_mode():
            features=self.encoder(self.preprocess(image).unsqueeze(0).to(self.device)).float().cpu().numpy()
            clip_score=float(self.classifier.predict_proba(features)[0,1])
            community_input=self.community_preprocess(image).unsqueeze(0).to(self.device)
            if getattr(self,'pipeline','clip_community_v1') in {'clip_community_full_v2','clip_community_full_v3'}:
                cf_features=self.community.forward_head(self.community.forward_features(community_input),pre_logits=True)
                cf_features=cf_features.float().cpu().numpy()
                community_score=float(self.community_classifier.predict_proba(cf_features)[0,1])
            else:
                logit=self.community(community_input).reshape(-1)
                community_score=float(torch.sigmoid(logit)[0])
        if getattr(self,'pipeline','clip_community_v1') in {'clip_community_full_v2','clip_community_full_v3'}:
            if self.deployment_candidate=='feature_fusion':
                import numpy as np
                combined=float(self.feature_fusion_classifier.predict_proba(np.concatenate([features,cf_features],axis=1))[0,1])
            else:
                combined=self.combine_retrained_scores(clip_score,community_score)
        else:
            combined=self.clip_weight*clip_score+(1-self.clip_weight)*community_score
        return {'combined':combined,
                'clip_probe':clip_score,'community':community_score}

    def combine_retrained_scores(self,clip_score,community_score):
        import numpy as np
        if self.deployment_candidate=='clip': return clip_score
        if self.deployment_candidate=='community': return community_score
        scores=np.clip([clip_score,community_score],1e-6,1-1e-6)
        log_odds=np.log(scores/(1-scores)).reshape(1,2)
        return float(self.fusion_classifier.predict_proba(log_odds)[0,1])

    def score(self,image):
        return self.score_details(image)['combined']
