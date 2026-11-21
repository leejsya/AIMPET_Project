from pathlib import Path
from PIL import Image
from django.conf import settings

import torch
import torch.nn as nn
from torchvision.transforms import v2
from torchvision.models import resnet18


# 모델 파라미터 경로
MODEL_PATH = Path(settings.BASE_DIR) / 'model.pt'
# 이미지 크기
IMG_SIZE = 224
# normalization을 위한 mean 값
MEAN = [0.485, 0.456, 0.406]
# normalization을 위핞 std 값
STD = [0.229, 0.224, 0.225]

# Device 설정
device = torch.device(
    'cuda' if torch.cuda.is_available()
    else 'mps' if torch.backends.mps.is_available()
    else 'cpu'
)

# 베이스 모델 불러오기 및 classifier 교체
model = resnet18()
model.fc = nn.Linear(model.fc.in_features, 1)
# 모델 파라미터 적용
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

# preprocessing
preprocess = v2.Compose(
    [
        # 텐서로 변환
        v2.ToImage(),
        # grayscale 이미지로 변환하고 3채널로 복제
        v2.Grayscale(num_output_channels=3),
        # 이미지 크기 조정
        v2.Resize((IMG_SIZE, IMG_SIZE)),
        # float32로 데이터 타입을 변경하고 0~1 사이의 값으로 scaling
        v2.ToDtype(dtype=torch.float32, scale=True),
        # standardization
        v2.Normalize(mean=MEAN, std=STD),
    ]
)

''' inference가 수행되는 부분 '''
def predict(image_file):
    # 이미지를 grayscale 1채널로 불러오기
    image = Image.open(image_file).convert('L')
    # preprocessing 적용
    # unzqueeze(0) : (3, 224, 224) -> (1, 3, 224, 224) 배치 차원 추가
    x = preprocess(image).unsqueeze(0).to(device)

    # gradienet 계산 X
    with torch.no_grad():
        # 입력이미지를 모델에 넣어주어 logit을 받음
        logit = model(x)
        # probability 계산
        prob = torch.sigmoid(logit).item()
        
    return prob