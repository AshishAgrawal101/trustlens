"""Local inference for the published Community Forensics ViT-S/16 detector."""
from pathlib import Path

MODEL_REVISION = '6076002bf0d9dd37537f965ee2f06f826c333b61'
MODEL_URL = f'https://huggingface.co/OwensLab/commfor-model-384/resolve/{MODEL_REVISION}/model.safetensors'


def load_community(weights):
    import timm
    from safetensors.torch import load_file
    from torchvision import transforms
    model = timm.create_model('vit_small_patch16_384.augreg_in21k_ft_in1k',
                              pretrained=False, num_classes=1)
    state = load_file(str(Path(weights)))
    model.load_state_dict({k.removeprefix('vit.'):v for k,v in state.items()}, strict=True)
    model.requires_grad_(False)
    model.eval()
    # Authors' test-time pipeline: shortest-edge resize 440, center crop 384,
    # float pixels in [0,1], and ImageNet normalization.
    preprocess = transforms.Compose([transforms.Resize(440), transforms.CenterCrop(384),
        transforms.ToTensor(), transforms.Normalize((.485,.456,.406),(.229,.224,.225))])
    return model, preprocess
