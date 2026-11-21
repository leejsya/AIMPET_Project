from .inference import model, preprocess, device, IMG_SIZE
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F
import torch.nn as nn

from matplotlib import colormaps
from io import BytesIO
from django.core.files.base import ContentFile

COLORMAP = colormaps['jet']

def render_heatmap(cam):
    # 모든 음수 값을 0으로
    cam = torch.relu(cam)
    # normalization(0~1 사이의 값으로 조정)
    cam = cam / (cam.max() + 1e-10) # zero-division 방지
    # interpolate - 4차원을 입력으로 받음
    cam = F.interpolate(
        cam.reshape(1, 1, 7, 7), size=(IMG_SIZE, IMG_SIZE), mode='bilinear'
    ).reshape(IMG_SIZE, IMG_SIZE).cpu().numpy()

    # 값을 색으로 변경 (224, 224) -> (224, 224, 4)
    heatmap = COLORMAP(cam)
    # 투명도를 cam값으로
    heatmap[:, :, 3] = cam
    
    return Image.fromarray((heatmap * 255).astype(np.uint8), mode='RGBA')

def generate_cam(image_file):
    image = Image.open(image_file).convert('L')
    # (3, 224, 224) -> (1, 3, 224, 224)
    x = preprocess(image).unsqueeze(0).to(device)

    # avg pool + fc layer만 제외(layer4의 feature map을 얻기 위함)
    backbone = nn.Sequential(*list(model.children())[:-2])

    with torch.no_grad():
        # (1, 512, ,7 ,7) -> (512, 7, 7)
        feature = backbone(x).squeeze(0)
        # (1, 512) -> (512, 1, 1)
        weight = model.fc.weight.reshape(-1, 1, 1)
        # 채널별로 가중치를 곱하고 채널방향으로 모두 더함. (512, 7, 7) -> (7, 7)
        cam = (weight * feature).sum(dim=0)

    # cam을 PIL 이미지로 렌더링
    heatmap_PIL = render_heatmap(cam)

    # heatmap PIL 이미지를 PNG 바이트로 변환
    buffer = BytesIO()
    heatmap_PIL.save(buffer, format='PNG')

    # Django가 저장할 수 있도록 파일 객체로 만듦
    return ContentFile(buffer.getvalue(), name='heatmap.png')