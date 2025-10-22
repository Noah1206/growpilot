# Frontend Deployment Guide - Railway

Railway에 프론트엔드를 별도 서비스로 배포하는 가이드입니다.

## 배포 방법

### 1단계: Railway에 새 서비스 추가

1. **Railway 대시보드** 접속: https://railway.app/
2. **GrowthPilot 프로젝트** 클릭
3. **"+ New Service"** 버튼 클릭
4. **"GitHub Repo"** 선택
5. **`Noah1206/growpilot`** 리포지토리 선택

### 2단계: 서비스 설정

새로 생성된 서비스를 클릭하고 **Settings** 탭으로 이동:

#### General Settings
- **Service Name**: `frontend` (또는 원하는 이름)

#### Source Settings
- **Root Directory**: `/frontend`
- **Branch**: `main`
- **Wait for CI**: OFF (선택사항)

#### Build Settings
Railway가 자동으로 `frontend/railway.json`을 읽어서 Docker 빌드를 설정합니다.

만약 자동 감지가 안 되면:
- **Builder**: DOCKERFILE
- **Dockerfile Path**: `Dockerfile`

#### Deploy Settings
Railway가 자동으로 설정하지만, 수동 확인:
- **Start Command**: `nginx -g 'daemon off;'`
- **Health Check Path**: `/`

### 3단계: 도메인 설정

1. **Settings → Networking** 탭으로 이동
2. **Public Networking** 섹션에서 Railway 도메인 자동 생성 확인
3. 도메인 예시: `growpilot-frontend-production.up.railway.app`

### 4단계: 배포 및 확인

1. Railway가 자동으로 배포 시작
2. **Deploy** 탭에서 빌드 로그 확인
3. 배포 완료 후 도메인 접속 테스트

```bash
curl https://growpilot-frontend-production.up.railway.app
```

## 아키텍처

```
┌─────────────────────────────────────────┐
│          Railway Project                │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Backend Service                   │ │
│  │  - Root: /backend                  │ │
│  │  - Python 3.11.9 + FastAPI         │ │
│  │  - Domain: growpilot-production... │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Frontend Service                  │ │
│  │  - Root: /frontend                 │ │
│  │  - Nginx + Static Files            │ │
│  │  - Domain: growpilot-frontend...   │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 프론트엔드 구성

### Nginx 설정 (`nginx.conf`)
- **포트**: 80
- **루트**: `/usr/share/nginx/html`
- **Gzip 압축**: 활성화
- **정적 파일 캐싱**: 1년
- **보안 헤더**: X-Frame-Options, X-Content-Type-Options 등

### API 연결 (`app.js`)
프론트엔드는 자동으로 환경을 감지하여 API URL을 설정합니다:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? "http://localhost:8001"
    : "https://growpilot-production.up.railway.app";
```

- **개발 환경** (localhost): `http://localhost:8001`
- **프로덕션** (Railway): `https://growpilot-production.up.railway.app`

## 배포 확인

### 1. 헬스체크
```bash
curl https://growpilot-frontend-production.up.railway.app
```

응답이 HTML이면 성공!

### 2. 정적 파일 확인
```bash
curl https://growpilot-frontend-production.up.railway.app/static/js/app.js
```

### 3. 브라우저 접속
프론트엔드 도메인으로 브라우저 접속하여 UI 확인

## 문제 해결

### 빌드 실패
**문제**: "No Dockerfile found"
**해결**: Settings → Source에서 Root Directory가 `/frontend`로 설정되어 있는지 확인

### 404 에러
**문제**: 모든 페이지에서 404
**해결**:
1. Deploy 탭에서 빌드 로그 확인
2. nginx가 제대로 시작되었는지 확인
3. Dockerfile이 올바른지 확인

### CORS 에러
**문제**: 백엔드 API 호출 시 CORS 에러
**해결**: 백엔드 `config.py`의 `allowed_origins`에 프론트엔드 도메인 추가

```python
allowed_origins: str = Field(
    default="http://localhost:9000,https://growpilot-production.up.railway.app,https://growpilot-frontend-production.up.railway.app",
    env="ALLOWED_ORIGINS"
)
```

## 환경 변수 (필요시)

현재 프론트엔드는 환경 변수가 필요 없지만, 필요한 경우:

1. **Settings → Variables** 탭
2. **Raw Editor** 클릭
3. 환경 변수 추가

```env
API_URL=https://growpilot-production.up.railway.app
```

## 비용 최적화

Railway 무료 플랜:
- **월 500시간** 실행 시간
- **100GB** 네트워크 대역폭

Frontend (Nginx)는 매우 가볍기 때문에 리소스를 거의 사용하지 않습니다.

## 대안: Vercel 또는 Netlify

정적 파일 호스팅에 특화된 플랫폼을 사용할 수도 있습니다:

### Vercel 배포
```bash
npm install -g vercel
cd frontend
vercel --prod
```

### Netlify 배포
```bash
npm install -g netlify-cli
cd frontend
netlify deploy --prod --dir=.
```

## 참고 자료

- Railway 문서: https://docs.railway.app/
- Nginx 문서: https://nginx.org/en/docs/
- Docker 문서: https://docs.docker.com/
