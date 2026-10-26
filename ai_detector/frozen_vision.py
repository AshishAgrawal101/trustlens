"""Shared frozen backbone loading for experiments and local image inference."""
def load_backbone(name, cache,device='cpu'):
    import torch
    from torchvision import models
    if name == 'resnet50':
        torch.hub.set_dir(str(cache))
        weights = models.ResNet50_Weights.IMAGENET1K_V2
        model = models.resnet50(weights=weights)
        model.fc = torch.nn.Identity()
        return model.to(device).eval(), weights.transforms(), 'torchvision:IMAGENET1K_V2'
    if name != 'clip_l14':
        raise ValueError(f'Unknown backbone: {name}')
    import open_clip
    from pathlib import Path
    local_weights = list(Path(cache).rglob('open_clip_model.safetensors'))
    if len(local_weights) > 1:
        raise ValueError('Multiple CLIP checkpoints found; select a cache containing one checkpoint')
    config = open_clip.get_pretrained_cfg('ViT-L-14', 'openai')
    pretrained = str(local_weights[0]) if local_weights else 'openai'
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-L-14', pretrained=pretrained, device=device, cache_dir=str(cache), force_quick_gelu=True,
        image_mean=config['mean'], image_std=config['std'],
        image_interpolation=config['interpolation'], image_resize_mode=config['resize_mode'])
    model.requires_grad_(False)
    return model.visual.eval(), preprocess, 'open_clip:ViT-L-14:openai'
