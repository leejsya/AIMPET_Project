# AIMPET_Project
- 과목: [클라우드 네이티브] / 이름 : [이준서] / 학번 : [202335314]

> (**A**uto **I**mage **M**odel **P**erformance **E**valuation **T**oolkit)

유방 초음파 이미지를 업로드하면 딥러닝 모델(ResNet18)이 악성(malignant) 점수를 예측하고, 
CAM(Class Activation Mapping) 히트맵을 통해 모델이 주목한 영역을 보여주는 웹 서비스입니다.

AIMPET 프로젝트명이 의미하는 것과 같이, 기존에는 모델의 이미지 딥러닝 모델의 성능을 평가하고
그 내용을 바탕으로 시각적으로 보여주는 서비스를 구축할 계획이었으나,
Database와 Redis 세션, 그리고 서버의 역할에 무게를 더 주기 위해서 다음과 같이 수정하였습니다.
1. 로그인/로그아웃/회원가입 기능을 수행하는 user server 구축
2. inference server에 CAM 기능 추가 구현
3. 서버 간 세션 공유 기능과 사용자 세션에 따른 Database 관리
> 프론트엔드는 Claude Code의 도움을 받아 구현되었으며, 해당 내용을 토대로 필요한 부분은 기능에 맞도록 직접 수정하였습니다.  


## 1. 개발 환경
- 컨테이너와 프로그램 실행에 있어서 모든 비밀번호는 '2323'으로 통일.
- MacOS의 UTM을 통한 Ubuntu VM 환경에서 개발됨.
- 모든 이미지는 amd64로 빌드됨.

## 2. 소스코드 GitHub 주소
[leejsya](https://github.com/leejsya/AIMPET_Project)

## 3. 도커 허브 주소
[leejsya0102](https://hub.docker.com/repositories/leejsya0102)
- leejsya0102/aimpet-mysql:latest
- leejsya0102/aimpet-redis:latest
- leejsya0102/aimpet-user:latest
- leejsya0102/aimpet-inf:latest
- leejsya0102/aimpet-frontend:latest
- leejsya0102/aimpet-proxy:latest

## 4. 구글 드라이브 주소
[drive](https://drive.google.com/drive/folders/1YBRKL_okqTu1wueOwEjbVoyGSH1C-PMP?usp=drive_link)
- 구현 시연 영상
- 도커 환경 캡처 이미지
- 테스트를 위한 테스트 이미지 폴더
- 시스템 구성도

## 5. 딥러닝 모델링
- 데이터셋 : MedMNIST의 BreastMNIST 데이터셋
- 사전학습 모델 : ResNet18
- 학습도구 : PyTorch
> 학습 데이터셋이 작은 모델이라 추론 성능이 뛰어나진 않기에, 테스트할 때 여러번 다른 샘플을 입력하여 확인해야 함.

## 6. 컨테이너 구조
모든 컨테이너는 'AIMPET-net' 네트워크로 연결됨.
1) inf_server(port:8000) - 모델 추론을 수행하는 서버
2) user_server(port:8000) - 서비스의 사용자를 관리하는 서버
3) frontend(port:80) - 서비스 웹 화면을 렌더링하는 서버
4) myproxy(port:80,81) - reverse proxy 기능을 수행하는 서버
5) myredis(port:6379) - 세션 공유 저장소 기능을 수행하는 서버
6) mysql(port:3306) - 데이터베이스 기능을 수행하는 서버

## 7. Request Flow
- ```/``` -> frontend:80
- ```/api/users/``` -> user_server:8000
- ```/api/inf/``` -> inf_server:8000

## 8. 기술 스택
- 프론트엔드 : HTML, CSS, JavaScript
- 백엔드 : Django, Django REST Framework, gunicorn
- 모델 : PyTorch, ResNet18, CAM
- DB : MySQL
- 세션 : Redis
- 인프라 : Docker
- Proxy : Nginx Proxy Manager

## 9. 폴더 구조
```
AIMPET_Project
├── Backends
│   ├── inf_server     # 추론 서버 (model.pt 포함)
│   └── user_server    # 사용자 서버
├── Frontends          # HTML, JS, CSS
├── nginx-proxy-manager  # 프록시 호스트 설정
├── mysql              # DB 초기 계정 설정 및 DB 생성
├── redis              # 세션 저장소 이미지
```
> 각 폴더에 Dockerfile로 실행에 필요한 비밀번호, DB 초기화, 프록시 등의 설정을 작성함.

## 10. 세션 공유 방식
1. 사용자가 로그인 시 user_server가 세션을 생성하고 user_id를 Redis 서버에 저장하며, 브라우저에서 세션 쿠기가 전달됨.
2. 같은 쿠키를 프록시를 통해 inf_server에서도 사용.
3. inf_server는 쿠키로 같은 Redis에서 세션을 읽어 로그인한 사용자(user_id)를 인식
4. 로그인된 상태라면 분석 결과를 inf_db에 user_id와 함께 저장하고, 조회할 때는 로그인한 사용자의 결과만 보여줌.

## 11. Proxy 설정
Reverse Proxy 설정은 이미지에 포함되어 있으므로 따로 진행할 필요가 없음. \
브라우저에서 http://localhost:81 에 접속 시 프록시 설정을 직접 확인할 수 있음.
> Nginx Proxy Manager 아이디 : leejsya@gachon.ac.kr | 비밀번호 : 12345678
- Domain Names : ```192.168.64.11```, ```localhost```
- Forward Hostname : frontend
- Forward Port : 80
- Custom Locations : ```/api/users/``` -> user_server:8000, ```/api/inf/``` -> inf_server:8000
- Custom Nginx Configuration : client_max_body_size 20M; proxy_read_timeout 120s;
> 20MB까지의 이미지를 업로드할 수 있도록 설정하고, 추론에 시간이 조금 걸릴 수 있기 때문에 timeout을 120초로 확장했음

## 12. 데이터 영속성
- mysql_data(mysql:/var/lib/mysql) - 회원 정보, 분석 결과 기록
- inf_media(inf_server:/app/media) - 저장된 결과 이미지와 히트맵
> 컨테이너를 삭제하고 같은 볼륨 이름으로 실행 시 데이터가 유지됨.

## 13. API
- user_server | POST | `'/api/users/signup/'` | 회원가입
- user_server | POST | `'/api/users/login/'` | 로그인
- user_server | POST | `'/api/users/logout/'` | 로그아웃
- user_server | GET | `'/api/users/me/'` | 현재 로그인 상태
- inf_server | POST | `'/api/inf/results/'` | 이미지 업로드 및 추론
- inf_server | GET | `'/api/inf/results/'` | 저장 결과 목록 조회
- inf_server | DELETE | `'/api/inf/results/<id>/'` | 결과 삭제

## 14. 실행 순서
> Host의 80, 81번 포트가 비어있어야 함.
1. docker 네트워크 생성
```bash
docker network create AIMPET-net
```

2. 이미지 다운로드 및 컨테이너 실행
```bash
docker run -d --name mysql --network AIMPET-net --restart unless-stopped -v mysql_data:/var/lib/mysql leejsya0102/aimpet-mysql:latest
docker run -d --name myredis --network AIMPET-net --restart unless-stopped leejsya0102/aimpet-redis:latest
docker run -d --name user_server --network AIMPET-net --restart unless-stopped leejsya0102/aimpet-user:latest
docker run -d --name inf_server --network AIMPET-net --restart unless-stopped -v inf_media:/app/media leejsya0102/aimpet-inf:latest
docker run -d --name frontend --network AIMPET-net --restart unless-stopped leejsya0102/aimpet-frontend:latest
docker run -d --name myproxy --network AIMPET-net --restart unless-stopped -p 80:80 -p 81:81 leejsya0102/aimpet-proxy:latest
```
> inf_server의 이미지가 조금 무거운 편이라 실행에 시간이 좀 걸림

3. 웹 브라우저에서 접근
> mysql에서 DB를 준비하는데 시간이 좀 걸리기 때문에 최소 1~2분 후에 실행하기
```bash
http://localhost
```

4. 로그인 화면에서 회원가입 또는 기존 아이디로 로그인 및 동작 확인
- 초기 실행 시 DB에 저장된 user 정보가 없기 때문에 회원가입을 통해 user 생성.(```index.html```)
- 회원가입 시 바로 그 계정으로 로그인 됨.
- 로그인에 성공하면 inference를 위한 이미지 업로드 화면과 저장된 결과 기록이 나타남.(```infer.html```)
- drag & drop 또는 파일선택을 통해 이미지를 업로드하고 '분석하기' 버튼을 클릭.
- 그 후 분석 결과가 화면에 렌더링되고 결과를 저장할지 여부를 물어봄.
- 저장하기 버튼을 클릭하면 DB에 업로드 이미지와 함께 결과가 저장됨.
- 저장하지 않는다면, DB와 media 폴더에서 이미지와 결과가 모두 삭제됨.
- 추가로, 결과화면에서 heatmap의 alpha값을 조정하며 CAM 기능을 확인할 수 있음.

