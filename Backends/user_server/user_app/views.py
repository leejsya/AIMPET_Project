
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

# 회원가입(POST) view
class SignupView(APIView):
    authentication_classes = []

    # username과 password를 입력받아 user정보를 DB에 추가
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        # 입력 정보 검증
        if not username or not password:
            return Response({'detail': 'username, password 필요'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'detail': '이미 존재하는 사용자'}, status=409)
        # 새로운 user 생성
        user = User.objects.create_user(username=username, password=password)
        return Response({'id': user.id, 'username': user.username}, status=201)

# 로그인(POST) view
class LoginView(APIView):
    authentication_classes = []

    # username과 password를 입력받아 검증 후 user_id의 세션을 생성
    def post(self, request):
        # 입력 정보 검증 
        user = authenticate(request,
                            username=request.data.get('username'),
                            password=request.data.get('password'))
        if user is None:
            return Response({'detail': '아이디 또는 비밀번호 오류'}, status=401)
        # 로그인
        login(request, user)
        # 세션 생성
        request.session['user_id'] = user.id   # inf_server가 읽는 값
        return Response({'id': user.id, 'username': user.username})

# 로그아웃(POST) view
class LogoutView(APIView):
    authentication_classes = []

    def post(self, request):
        # 로그아웃
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

# 현재 로그인 정보 조회(GET) view
class MeView(APIView):
    authentication_classes = []

    # 로그인 상태 조회
    def get(self, request):
        # 세션 정보
        user_id = request.session.get('user_id')
        # 저장된 결과 정보
        user = User.objects.filter(id=user_id).first() if user_id else None
        # user 검증
        if user is None:
            return Response({'detail': '로그인 필요'}, status=401)
        return Response({'id': user.id, 'username': user.username})