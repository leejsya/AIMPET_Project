from rest_framework import serializers
from .models import ResultModel

# 이미지 업로드를 위한 시리얼라이저
class UploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

# 추론 결과와 히트맵 이미지를 저장하기 위한 시리얼라이저
class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultModel
        fields = [
            'id',
            'image',
            'malignant_prob',
            'created_time',
            'heatmap'
        ]
        # 읽기만 수행 가능
        read_only_fields = [
            'id',
            'malignant_prob',
            'created_time',
            'heatmap',
        ]