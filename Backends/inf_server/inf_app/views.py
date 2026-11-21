import base64

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import ResultSerializer, UploadSerializer
from .models import ResultModel
from .ML.inference import predict
from .ML.cam import generate_cam

# userid 세션 공유
def get_user_id(request):
    return request.session.get('user_id')

# 결과 목록 조회(GET) + 이미지 업로드 및 추론(POST) view
class ResultListCreateView(generics.ListCreateAPIView):
    serializer_class = ResultSerializer

    # user 세션에 저장되어 있는 결과 조회
    def get_queryset(self):
        # user_id 가져오기
        user_id = get_user_id(self.request)
        # user_id 검증
        if user_id is None:
            return ResultModel.objects.none()
        # user_id의 세션에 저장된 결과만을 조회
        return ResultModel.objects.filter(user_id=user_id).order_by('-created_time')

    # 이미지를 추론 모델에 업로드
    def create(self, request, *args, **kwargs):
        # 입력 이미지 검증 후 업로드
        upload = UploadSerializer(data=request.data)
        upload.is_valid(raise_exception=True)
        image = upload.validated_data['image']

        # 추론 모델 predict에서 이미지를 입력받아 추론 결과를 반환
        malignant_prob = predict(image)
        image.seek(0)
        # 히트맵 렌더링 generate_cam에서 이미지를 입력받아 히트맵 결과 이미지를 받환
        heatmap_img = generate_cam(image)
        image.seek(0)

        # 추론 결과 + 히트맵 조회
        user_id = get_user_id(request)
        if user_id is None:
            heatmap_b64 = base64.b64encode(heatmap_img.read()).decode()
            return Response(
                {
                    'malignant_prob': malignant_prob,
                    'heatmap': 'data:image/png;base64,' + heatmap_b64,
                    'saved': False,
                },
                status=status.HTTP_200_OK,
            )

        # 일단 결과를 DB에 저장
        result = ResultModel.objects.create(
            user_id=user_id,
            image=image,
            malignant_prob=malignant_prob,
            heatmap=heatmap_img,
        )
        data = dict(ResultSerializer(result, context={'request': request}).data)
        data['saved'] = True
        return Response(data, status=status.HTTP_201_CREATED)


# 개별 결과 조회(GET) + 결과삭제(DELETE) view
class ResultDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ResultSerializer

    # user 세션에 저장되어 있는 결과 조회
    def get_queryset(self):
        user_id = get_user_id(self.request)
        if user_id is None:
            return ResultModel.objects.none()
        return ResultModel.objects.filter(user_id=user_id)

    # 사용자가 DB에 결과 저장을 거부할 시 모든 내용 삭제
    def perform_destroy(self, instance):
        # media image 파일 삭제
        instance.image.delete(save=False)
        # heatmap image 삭제
        if instance.heatmap:
            instance.heatmap.delete(save=False)
        # DB 레코드 삭제
        instance.delete()
