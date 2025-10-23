# Railway PostgreSQL Setup Guide

## 🚀 Railway PostgreSQL 연결 가이드

### 1. Railway에서 PostgreSQL 블록 확인

1. [Railway Dashboard](https://railway.app/dashboard) 접속
2. 프로젝트 선택
3. PostgreSQL 블록 클릭
4. **Variables** 탭에서 다음 정보 확인:
   - `DATABASE_URL` (전체 연결 문자열)
   - `PGDATABASE` (데이터베이스 이름)
   - `PGHOST` (호스트 주소)
   - `PGPASSWORD` (비밀번호)
   - `PGPORT` (포트 번호)
   - `PGUSER` (사용자명)

### 2. GrowthPilot 서비스에 환경 변수 추가

#### Railway Dashboard에서:

1. **GrowthPilot 서비스** 클릭 (PostgreSQL 블록이 아닌 앱 서비스)
2. **Variables** 탭으로 이동
3. **Add Variable** 클릭
4. 다음 변수 추가:

```bash
# PostgreSQL 연결 (Railway PostgreSQL 블록에서 복사)
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/railway

# 기존 API 키들도 유지
GEMINI_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
# ... 기타 환경 변수들
```

#### 또는 Railway CLI 사용:

```bash
# Railway CLI 설치 (아직 없다면)
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 연결
railway link

# 환경 변수 설정
railway variables set DATABASE_URL="postgresql://..."
```

### 3. 로컬에서 PostgreSQL 연결 테스트

```bash
# 1. .env 파일 생성 (backend 폴더에서)
cd backend
cp .env.railway.example .env

# 2. .env 파일 편집하여 Railway PostgreSQL URL 입력
# DATABASE_URL=postgresql://postgres:xxxxx@containers-us-west-xxx.railway.app:xxxx/railway

# 3. 마이그레이션 실행
python migrate_to_postgresql.py

# 4. 서버 실행 테스트
uvicorn app.main:app --reload --port 6000
```

### 4. Railway 배포

```bash
# Git에 변경사항 커밋
git add .
git commit -m "Configure PostgreSQL database connection"
git push

# Railway가 자동으로 재배포됨
```

### 5. 확인 사항

#### ✅ 체크리스트:
- [ ] Railway PostgreSQL 블록이 생성됨
- [ ] DATABASE_URL을 Railway 서비스 변수에 추가함
- [ ] 로컬에서 PostgreSQL 연결 테스트 성공
- [ ] Railway에 배포 완료

#### 🔍 문제 해결:

**"connection refused" 에러:**
- DATABASE_URL이 올바른지 확인
- Railway PostgreSQL 블록이 활성화되어 있는지 확인
- 네트워크 연결 확인

**"relation does not exist" 에러:**
- 테이블이 생성되지 않음
- `python migrate_to_postgresql.py` 실행
- 또는 앱 시작 시 자동으로 테이블 생성됨

**"password authentication failed" 에러:**
- DATABASE_URL의 비밀번호 확인
- Railway Variables에서 최신 정보 확인

### 6. PostgreSQL 장점

SQLite → PostgreSQL 전환 시 장점:
- ✅ **동시성**: 여러 사용자 동시 접속 처리
- ✅ **확장성**: 대용량 데이터 처리
- ✅ **신뢰성**: ACID 트랜잭션 완벽 지원
- ✅ **Railway 통합**: 자동 백업, 모니터링
- ✅ **프로덕션 준비**: 실제 서비스 운영 가능

### 7. 데이터 마이그레이션 (선택사항)

기존 SQLite 데이터를 PostgreSQL로 이전하려면:

```python
# 별도 스크립트 작성 필요
# 1. SQLite에서 데이터 읽기
# 2. PostgreSQL로 데이터 삽입
```

### 8. 모니터링

Railway Dashboard에서:
- PostgreSQL 블록 → Metrics 탭
- CPU, Memory, Storage 사용량 확인
- Query 성능 모니터링

## 🎯 완료!

이제 GrowthPilot이 Railway PostgreSQL을 사용합니다.
프로덕션 환경에서 안정적인 데이터베이스 운영이 가능합니다.