from django.urls import path
from .views import SignupView, LoginView, LogoutView, MeView

urlpatterns = [
    # 회원가입
    path('signup/', SignupView.as_view()),
    # 로그인
    path('login/', LoginView.as_view()),
    # 로그아웃
    path('logout/', LogoutView.as_view()),
    # 현재 로그인 정보
    path('me/', MeView.as_view()),
]