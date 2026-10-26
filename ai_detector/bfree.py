"""B-Free inference adapter. Published weights are for nonprofit research use.

Reference: https://github.com/grip-unina/B-Free
The authors' five-crop averaging is preserved. Identical crop positions are
evaluated once with their original multiplicity, to save CPU work on small inputs.
"""
import math


def crop_positions(height, width, size):
    if height<size or width<size:
        height=width=size
    return [((height-size)//2,(width-size)//2), (0,0),
            (height-size,0), (height-size,width-size), (0,width-size)]


def load_bfree(weights,device='cpu'):
    import torch
    import timm
    from torchvision import transforms
    model = timm.create_model('vit_base_patch14_reg4_dinov2.lvd142m',
                             pretrained=False, num_classes=1)
    model.set_input_size(img_size=504)
    state = torch.load(weights,map_location='cpu',weights_only=True)
    if set(state) != {'model'}:
        raise ValueError('Unexpected B-Free checkpoint')
    model.load_state_dict(state['model'],strict=True)
    model.to(device)
    patch = model.patch_embed
    model.patch_embed = torch.nn.Identity()
    model.eval().requires_grad_(False)
    preprocess = transforms.Compose([transforms.ToTensor(),
        transforms.Normalize((.485,.456,.406),(.229,.224,.225))])
    return model, patch, preprocess


def bfree_logit(runtime, image, deduplicate=True):
    import torch
    model, patch, preprocess = runtime
    with torch.inference_mode():
        device=next(model.parameters()).device
        embedding = patch.proj(preprocess(image).unsqueeze(0).to(device))
        size = patch.grid_size[0]
        h,w = embedding.shape[-2:]
        if h<size or w<size:
            embedding = embedding.repeat(1,1,max(math.ceil(size/h),1),max(math.ceil(size/w),1))
            # The published wrapper truncates BOTH axes to its patch grid when
            # either axis needs replication, including narrow/tall inputs.
            embedding = embedding[:,:,:size,:size]
        h,w=embedding.shape[-2:]
        positions = crop_positions(h,w,size)
        unique = list(dict.fromkeys(positions)) if deduplicate else positions
        # Small crops can all coincide. Preserve the five-crop weighting.
        embeddings = torch.cat([embedding[:,:,y:y+size,x:x+size] for y,x in unique])
        if patch.flatten:
            embeddings = embeddings.flatten(2).transpose(1,2)
        embeddings = patch.norm(embeddings)
        logits = model(embeddings).reshape(-1)
        if deduplicate:
            logits = torch.stack([logits[unique.index(q)] for q in positions])
        return float(logits.mean())
