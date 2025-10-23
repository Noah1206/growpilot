# Railway Variable Reference 설정 가이드

## 🔗 PostgreSQL과 GrowthPilot 서비스 연결하기

### 방법 1: Variable Reference 사용 (권장) ✨

1. **GrowthPilot 서비스**의 Variables 탭에서
2. 상단의 보라색 **"Add a Variable Reference"** 링크 클릭
3. **Postgres** 서비스 선택
4. **DATABASE_URL** 선택
5. 자동으로 PostgreSQL의 DATABASE_URL이 연결됨

### 방법 2: 수동으로 DATABASE_URL 복사

1. **Postgres 블록** 클릭
2. **Variables** 탭에서 DATABASE_URL 값 복사 (눈 아이콘 클릭하여 값 보기)
3. **growpilot 서비스**로 돌아가기
4. **Variables** 탭에서 DATABASE_URL이 이미 있다면:
   - 값이 `sqlite:///./growthpilot.db`인지 확인
   - PostgreSQL URL로 교체 필요
5. DATABASE_URL 값 업데이트

### 현재 상태 체크리스트:

✅ **완료된 것들:**
- PostgreSQL 블록 생성 완료
- GrowthPilot 서비스 실행 중
- DATABASE_URL 변수 존재

⚠️ **확인 필요:**
- DATABASE_URL이 SQLite URL이 아닌 PostgreSQL URL인지 확인
- Format: `postgresql://postgres:xxxxx@xxxxx.railway.app:xxxx/railway`

### 연결 확인 방법:

1. **Deployments** 탭에서 최신 배포 로그 확인
2. 다음 메시지 찾기:
   - "📊 Creating database tables..."
   - "✅ Database tables created successfully!"

3. 에러가 있다면:
   - "sqlite" 관련 에러 → DATABASE_URL이 여전히 SQLite를 가리킴
   - "connection refused" → PostgreSQL URL이 잘못됨

### 재배포 트리거:

변수 업데이트 후:
```bash
# 로컬에서 작은 변경 후 푸시
git add .
git commit -m "Trigger Railway redeploy with PostgreSQL"
git push
```

또는 Railway Dashboard에서:
- Deployments 탭 → 최신 배포 → 우측 ⋮ 메뉴 → Redeploy