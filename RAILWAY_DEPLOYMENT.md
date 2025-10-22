# 🚂 Railway 배포 가이드

GrowthPilot을 Railway에 배포하는 완벽한 가이드입니다.

## 📋 사전 준비

### 1. 필수 계정

- ✅ Railway 계정: https://railway.app (GitHub로 로그인 가능)
- ✅ GitHub 계정 (코드 푸시용)

### 2. 로컬 준비사항 확인

```bash
# Git 저장소 확인
git remote -v
# origin  https://github.com/Noah1206/growpilot.git

# 변경사항 커밋
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

---

## 🚀 Step 1: Railway 프로젝트 생성

### 1-1. Railway 대시보드 접속

1. https://railway.app 접속
2. **"Start a New Project"** 클릭
3. **"Deploy from GitHub repo"** 선택

### 1-2. GitHub 저장소 연결

1. **"Configure GitHub App"** 클릭 (처음인 경우)
2. `Noah1206/growpilot` 저장소 선택
3. **"Deploy Now"** 클릭

### 1-3. 배포 설정

- **Root Directory**: `backend` 선택 (중요!)
- **Start Command**: 자동 감지됨 (Procfile 사용)
- Railway가 자동으로 Python 환경 설정

---

## 🗄️ Step 2: PostgreSQL 데이터베이스 추가

### 2-1. 데이터베이스 플러그인 추가

1. Railway 프로젝트 대시보드에서 **"+ New"** 클릭
2. **"Database"** → **"Add PostgreSQL"** 선택
3. PostgreSQL 인스턴스 생성 완료 대기 (1-2분)

### 2-2. 데이터베이스 연결 확인

1. PostgreSQL 플러그인 클릭
2. **"Variables"** 탭에서 `DATABASE_URL` 확인
3. Railway가 자동으로 백엔드 서비스와 연결함

---

## ⚙️ Step 3: 환경변수 설정

### 3-1. 백엔드 서비스 환경변수 설정

Railway 대시보드에서 백엔드 서비스 클릭 → **"Variables"** 탭

#### 필수 환경변수

```env
# Google Gemini API (필수)
GEMINI_API_KEY=your_gemini_api_key_here

# 데이터베이스 (자동 설정됨)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# 애플리케이션 보안
SECRET_KEY=LYMulnGTuauYeK3BJ1w9F5AI3UZtbLRZ7fsvLJfskRU
ENVIRONMENT=production
DEBUG=False

# CORS 설정 (Railway 도메인으로 변경)
ALLOWED_ORIGINS=https://your-app.up.railway.app

# Rate Limiting
MAX_DAILY_SENDS_LINKEDIN=200
MAX_DAILY_SENDS_REDDIT=30
MAX_DAILY_SENDS_FACEBOOK=50
```

#### SECRET_KEY 생성 방법

```bash
# Python으로 랜덤 키 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3-2. Railway 도메인 확인

1. 백엔드 서비스 → **"Settings"** 탭
2. **"Domains"** 섹션에서 자동 생성된 도메인 확인
   - 예: `growthpilot-production-xxxx.up.railway.app`
3. **ALLOWED_ORIGINS** 환경변수에 이 도메인 추가

---

## 🔧 Step 4: 데이터베이스 마이그레이션

### 4-1. Railway CLI 설치 (옵션)

```bash
# macOS
brew install railway

# Linux/Windows WSL
curl -fsSL https://railway.app/install.sh | sh
```

### 4-2. Railway CLI 로그인

```bash
railway login
```

### 4-3. 프로젝트 연결

```bash
cd /Users/johyeon-ung/Desktop/GrowthPilot/backend
railway link
# 프로젝트 선택
```

### 4-4. 마이그레이션 실행

```bash
# Railway 환경에서 마이그레이션 실행
railway run alembic upgrade head
```

### 대안: Railway 대시보드에서 실행

1. 백엔드 서비스 → **"Deployments"** 탭
2. 최근 배포 클릭 → **"View Logs"**
3. 로그에서 마이그레이션 자동 실행 확인

---

## ✅ Step 5: 배포 확인

### 5-1. 헬스체크 확인

```bash
# Railway 도메인으로 헬스체크
curl https://your-app.up.railway.app/health
```

**예상 응답:**

```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

### 5-2. API 문서 확인

브라우저에서 접속:

- **Swagger UI**: https://your-app.up.railway.app/docs
- **ReDoc**: https://your-app.up.railway.app/redoc

### 5-3. 프론트엔드 확인

- **메인 페이지**: https://your-app.up.railway.app/
- 정적 파일이 정상적으로 로드되는지 확인

---

## 🔄 Step 6: 자동 배포 설정

### 6-1. GitHub 연동 확인

1. Railway 프로젝트 → **"Settings"** 탭
2. **"Source"** 섹션에서 GitHub 연결 확인
3. **"Deploy Trigger"**: `main` 브랜치 자동 배포 활성화

### 6-2. 배포 테스트

```bash
# 코드 변경 후 푸시
git add .
git commit -m "Test Railway auto-deployment"
git push origin main

# Railway 대시보드에서 자동 배포 확인
```

---

## 🎯 Step 7: 커스텀 도메인 연결 (선택사항)

### 7-1. 도메인 설정

1. Railway 프로젝트 → 백엔드 서비스 → **"Settings"** 탭
2. **"Domains"** → **"Custom Domain"** 클릭
3. 본인 도메인 입력 (예: `api.growthpilot.com`)

### 7-2. DNS 설정

Railway가 제공하는 CNAME 레코드를 도메인 DNS에 추가:

```
Type: CNAME
Name: api (또는 원하는 서브도메인)
Value: your-app.up.railway.app
```

### 7-3. ALLOWED_ORIGINS 업데이트

환경변수에 커스텀 도메인 추가:

```env
ALLOWED_ORIGINS=https://your-app.up.railway.app,https://api.growthpilot.com
```

---

## 🐛 문제 해결

### 배포 실패 시

1. **Railway Logs 확인**:

   - 백엔드 서비스 → **"Deployments"** → 최근 배포 → **"View Logs"**

2. **빌드 오류**:

   ```bash
   # requirements.txt 문제
   - Python 버전 확인 (runtime.txt)
   - psycopg2-binary 설치 확인
   ```

3. **데이터베이스 연결 오류**:

   ```bash
   # DATABASE_URL 확인
   - PostgreSQL 플러그인 정상 작동 확인
   - 환경변수에 DATABASE_URL 설정 확인
   ```

4. **CORS 오류**:
   ```env
   # ALLOWED_ORIGINS 확인
   ALLOWED_ORIGINS=https://your-exact-railway-domain.up.railway.app
   ```

### 헬스체크 실패

```bash
# Railway 대시보드 → 백엔드 서비스 → Settings → Health Check
Path: /health
Timeout: 100
```

### 마이그레이션 실패

```bash
# Railway CLI로 수동 실행
railway run alembic upgrade head

# 또는 로컬에서 Railway DB에 직접 연결
railway run bash
alembic upgrade head
```

---

## 📊 모니터링 및 로그

### 로그 확인

```bash
# Railway CLI로 실시간 로그 보기
railway logs

# 또는 대시보드에서
# 백엔드 서비스 → Deployments → View Logs
```

### 메트릭 확인

Railway 대시보드에서:

- CPU 사용량
- 메모리 사용량
- 네트워크 트래픽
- 응답 시간

---

## 💰 비용 최적화

### Railway 무료 티어

- **시간**: 월 500시간 (약 $5 크레딧)
- **PostgreSQL**: 1GB 스토리지
- **대역폭**: 100GB/월

### 비용 절감 팁

1. **개발/테스트 환경 분리**: 별도 프로젝트 사용
2. **Sleep Mode**: 사용하지 않을 때 서비스 중지
3. **로그 관리**: 불필요한 로그 최소화

---

## 🔐 보안 체크리스트

- ✅ `.env` 파일이 Git에 커밋되지 않았는지 확인
- ✅ `SECRET_KEY`가 강력한 랜덤 값인지 확인
- ✅ `DEBUG=False`로 설정
- ✅ `ALLOWED_ORIGINS`에 정확한 도메인만 포함
- ✅ Gemini API 키가 안전하게 저장됨
- ✅ PostgreSQL 비밀번호 자동 관리 확인

---

## 🎉 배포 완료!

축하합니다! GrowthPilot이 Railway에 성공적으로 배포되었습니다.

**다음 단계:**

1. 프론트엔드에서 API 연결 테스트
2. 캠페인 생성 기능 테스트
3. 사용자 등록 및 로그인 테스트
4. Analytics 대시보드 확인

**유용한 링크:**

- Railway 대시보드: https://railway.app/dashboard
- Railway 문서: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

---

## 📞 도움이 필요하신가요?

- Railway 커뮤니티: https://discord.gg/railway
- GitHub Issues: https://github.com/Noah1206/growpilot/issues
- Railway 문서: https://docs.railway.app

Happy deploying! 🚀
