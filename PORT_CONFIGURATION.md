# GrowthPilot - Port Configuration

## 포트 설정

GrowthPilot은 다음 포트를 사용합니다:

### Backend API Server
- **포트**: `6000`
- **URL**: `http://localhost:6000`
- **API 문서**: `http://localhost:6000/docs`
- **ReDoc**: `http://localhost:6000/redoc`
- **헬스 체크**: `http://localhost:6000/health`

### Frontend Application
- **포트**: `9000`
- **URL**: `http://localhost:9000`

## 서버 시작 방법

### Backend (포트 6000)
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 6000
```

### Frontend (포트 9000)
```bash
cd frontend
python -m http.server 9000
```

## CORS 설정

Backend는 다음 프론트엔드 URL을 허용합니다:
- `http://localhost:9000`
- `http://127.0.0.1:9000`
- `http://localhost:6000`
- `http://127.0.0.1:6000`

추가 URL이 필요한 경우 `.env` 파일의 `ALLOWED_ORIGINS`를 수정하세요:

```env
ALLOWED_ORIGINS=http://localhost:9000,http://127.0.0.1:9000,http://localhost:6000,http://127.0.0.1:6000
```

## 포트 변경 방법

### Backend 포트 변경
백엔드 포트를 변경하려면 서버 시작 명령어의 `--port` 옵션을 수정하세요:

```bash
uvicorn app.main:app --reload --port YOUR_PORT
```

### Frontend API 연결 포트 변경
프론트엔드가 연결하는 백엔드 포트를 변경하려면:

1. `frontend/static/js/app.js` 파일을 엽니다
2. `API_BASE_URL` 상수를 수정합니다:

```javascript
const API_BASE_URL = 'http://localhost:YOUR_PORT';
```

### Frontend 서빙 포트 변경
프론트엔드 서빙 포트를 변경하려면:

```bash
python -m http.server YOUR_PORT
```

## 방화벽 설정

로컬 개발 환경에서 방화벽이 활성화된 경우:
- 포트 6000 (Backend)
- 포트 9000 (Frontend)

위 포트들을 허용해주세요.

## 프로덕션 배포

프로덕션 환경에서는:
- Backend: Railway/Heroku가 자동으로 `PORT` 환경 변수 제공
- Frontend: Vercel/Netlify에서 정적 파일 서빙
- 프로덕션 URL로 `API_BASE_URL` 업데이트 필요

## 트러블슈팅

### "Address already in use" 에러

**문제**: 포트가 이미 사용 중입니다.

**해결 방법**:

**macOS/Linux**:
```bash
# 포트 6000 사용 중인 프로세스 찾기
lsof -i :6000

# 프로세스 종료 (PID는 위 명령어 결과에서 확인)
kill -9 PID
```

**Windows**:
```powershell
# 포트 6000 사용 중인 프로세스 찾기
netstat -ano | findstr :6000

# 프로세스 종료 (PID는 위 명령어 결과에서 확인)
taskkill /PID PID /F
```

### CORS 에러

**문제**: 프론트엔드에서 백엔드로 요청 시 CORS 에러 발생

**해결 방법**:
1. `.env` 파일에서 `ALLOWED_ORIGINS`에 프론트엔드 URL 추가
2. 백엔드 서버 재시작
3. 브라우저 캐시 삭제

### 연결 거부 (Connection Refused)

**문제**: 프론트엔드가 백엔드에 연결할 수 없습니다.

**체크리스트**:
1. ✅ 백엔드 서버가 포트 6000에서 실행 중인지 확인
2. ✅ `frontend/static/js/app.js`의 `API_BASE_URL`이 올바른지 확인
3. ✅ 브라우저 콘솔에서 에러 메시지 확인
4. ✅ 백엔드 헬스 체크: `curl http://localhost:6000/health`

## 참고 자료

- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작 가이드
- [docs/SETUP.md](docs/SETUP.md) - 상세 설정 가이드
- [docs/API.md](docs/API.md) - API 문서
