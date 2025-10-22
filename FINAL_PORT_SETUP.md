# GrowthPilot - 최종 포트 설정

## 🎯 포트 구성

### Backend (FastAPI)
- **포트**: `6000`
- **URL**: `http://localhost:6000`
- **API 문서**: `http://localhost:6000/docs`
- **ReDoc**: `http://localhost:6000/redoc`

### Frontend (Static HTML/CSS/JS)
- **포트**: `9000`
- **URL**: `http://localhost:9000`

## 🚀 서버 실행 방법

### 1. Backend 시작
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 6000
```

### 2. Frontend 시작 (새 터미널)
```bash
cd frontend
python -m http.server 9000
```

## 🌐 접속 URL

- **웹 애플리케이션**: http://localhost:9000
- **API 엔드포인트**: http://localhost:6000
- **API 문서 (Swagger)**: http://localhost:6000/docs
- **헬스 체크**: http://localhost:6000/health

## ✅ 빠른 테스트

```bash
# 1. Backend 헬스 체크
curl http://localhost:6000/health

# 2. 웹브라우저에서 접속
open http://localhost:9000  # macOS
start http://localhost:9000  # Windows
```

## 📝 설정 파일

### Backend CORS 설정 (.env)
```env
ALLOWED_ORIGINS=http://localhost:9000,http://127.0.0.1:9000,http://localhost:6000,http://127.0.0.1:6000
```

### Frontend API 연결 (frontend/static/js/app.js)
```javascript
const API_BASE_URL = 'http://localhost:6000';
```

## 🔧 트러블슈팅

### "Address already in use" 에러

**포트 6000이 사용 중인 경우:**
```bash
# macOS/Linux
lsof -i :6000
kill -9 <PID>

# Windows
netstat -ano | findstr :6000
taskkill /PID <PID> /F
```

**포트 9000이 사용 중인 경우:**
```bash
# macOS/Linux
lsof -i :9000
kill -9 <PID>

# Windows
netstat -ano | findstr :9000
taskkill /PID <PID> /F
```

### CORS 에러

1. `.env` 파일에 프론트엔드 URL 추가 확인
2. Backend 서버 재시작
3. 브라우저 캐시 삭제 (Cmd+Shift+R / Ctrl+Shift+R)

### 연결 실패

**체크리스트:**
- ✅ Backend가 포트 6000에서 실행 중인가?
- ✅ Frontend가 포트 9000에서 실행 중인가?
- ✅ 방화벽이 포트를 차단하고 있지 않은가?
- ✅ .env 파일이 올바르게 설정되었는가?

## 📚 추가 문서

- 상세 설정: [docs/SETUP.md](docs/SETUP.md)
- API 문서: [docs/API.md](docs/API.md)
- 빠른 시작: [QUICKSTART.md](QUICKSTART.md)
- 포트 설정: [PORT_CONFIGURATION.md](PORT_CONFIGURATION.md)

---

**모든 설정 완료! 🎉**

이제 http://localhost:9000 으로 접속하여 GrowthPilot을 사용하실 수 있습니다!
