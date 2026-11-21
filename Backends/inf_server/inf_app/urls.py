from django.urls import path
from .views import ResultListCreateView, ResultDetailView

urlpatterns = [
    # 저장된 결과 리스트 조회
    path("results/", ResultListCreateView.as_view(), name='result_list'),
    # 저장된 개별 결과 조회
    path("results/<int:pk>/", ResultDetailView.as_view(), name='result_detail'),
]