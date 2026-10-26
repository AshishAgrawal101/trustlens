"""CLIP attention LoRA and architecture-compatible visual checkpoint exports."""
import hashlib
import json
from pathlib import Path

import torch
from torch import nn
from torch.nn.utils import parametrize

class LowRankDelta(nn.Module):
    def __init__(self,weight,rank=8):
        super().__init__()
        self.rank=rank
        self.a=nn.Parameter(torch.empty(rank,weight.shape[1],device=weight.device,dtype=weight.dtype))
        self.b=nn.Parameter(torch.zeros(weight.shape[0],rank,device=weight.device,dtype=weight.dtype))
        nn.init.kaiming_uniform_(self.a,a=5**.5)
    def forward(self,weight): return weight+(self.b@self.a)  # alpha/rank=1

def attach_clip_lora(visual,rank=8,last_blocks=6):
    visual.requires_grad_(False)
    blocks=list(visual.transformer.resblocks)
    if last_blocks>len(blocks): raise ValueError('Not enough CLIP attention blocks')
    targets=[]
    for i,block in enumerate(blocks[-last_blocks:],start=len(blocks)-last_blocks):
        attention=block.attn
        if not isinstance(attention,nn.MultiheadAttention) or attention.in_proj_weight is None:
            raise ValueError('Unsupported CLIP attention architecture')
        parametrize.register_parametrization(attention,'in_proj_weight',LowRankDelta(attention.in_proj_weight,rank))
        parametrize.register_parametrization(attention.out_proj,'weight',LowRankDelta(attention.out_proj.weight,rank))
        targets.extend([f'transformer.resblocks.{i}.attn.in_proj_weight',f'transformer.resblocks.{i}.attn.out_proj.weight'])
    return targets

def merged_state(model):
    """Merge LoRA without removing parametrizations from the live trainer."""
    state={k:v.detach().cpu().contiguous().clone() for k,v in model.state_dict().items() if '.parametrizations.' not in k}
    for name,module in model.named_modules():
        if not parametrize.is_parametrized(module): continue
        for key in module.parametrizations:
            state[(name+'.' if name else '')+key]=getattr(module,key).detach().cpu().contiguous().clone()
    return state

def export_visual(model,path):
    from safetensors.torch import save_file
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.safetensors.tmp')
    save_file(merged_state(model),str(temporary),metadata={'format':'trustlens-merged-visual-v1'})
    temporary.replace(path)

def assert_feature_contract(actual,expected):
    if actual!=expected:
        raise ValueError('Incompatible encoder/checkpoint or preprocessing in cached embeddings')

def contract(branch,weights_sha256,base_sha256):
    preprocessing={'clip':'clip_l14_quickgelu_openai224_v1',
                   'community':'community_vit_s16_resize440_crop384_imagenet_v1'}[branch]
    return {'branch':branch,'weights_sha256':weights_sha256,'base_weights_sha256':base_sha256,
            'preprocessing':preprocessing,'dimensions':768 if branch=='clip' else 384,
            'pixel_decode':'exif_transpose_rgb_v1','representation':'unnormalized_penultimate_fp32_v1'}

def load_visual(branch,cache,community_weights,checkpoint=None,device='cpu'):
    from ai_detector.frozen_vision import load_backbone
    from ai_detector.community import load_community
    if branch=='clip': model,preprocess,_=load_backbone('clip_l14',cache,device)
    elif branch=='community': model,preprocess=load_community(community_weights); model.to(device)
    else: raise ValueError('Unknown visual branch')
    if checkpoint is not None:
        from safetensors.torch import load_file
        model.load_state_dict(load_file(str(checkpoint)),strict=True)
    return model.eval().requires_grad_(False),preprocess

def representation(model,branch,inputs):
    return model(inputs) if branch=='clip' else model.forward_head(model.forward_features(inputs),pre_logits=True)
