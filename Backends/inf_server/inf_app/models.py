from django.db import models

# Create your models here.

# 결과 저장 형태
class ResultModel(models.Model):
    # 저장을 수행하는 user의 id
    user_id = models.PositiveIntegerField(db_index=True)
    # 입력된 이미지 저장
    image = models.ImageField(upload_to='results/%Y/%m/%d', max_length=255)
    # 추론 결과 저장
    malignant_prob = models.FloatField()
    # 생성 시각(자동 생성)
    created_time = models.DateTimeField(auto_now_add=True)
    # 히트맵 이미지 저장
    heatmap = models.ImageField(upload_to="heatmap/%Y/%m/%d", max_length=255, null=True, blank=True)
    # 생성시각을 기준으로 정렬
    class Meta:
        ordering = ['-created_time']

    # id를 통해 접근 가능
    def __str__(self):
        return f"{self.id}"