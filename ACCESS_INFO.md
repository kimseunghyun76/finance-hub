# 🌐 Finance-Hub 접속 정보

**생성일시**: 2025-11-21
**상태**: 서버 실행 중

---

## ✅ 서버 상태

### 백엔드 API ✅
```
URL: http://localhost:8001
Status: ✅ Running (PID: 26266)
Health: http://localhost:8001/health
Docs: http://localhost:8001/docs
```

### 프론트엔드 ✅
```
URL: http://localhost:3000
Status: ✅ Running (PID: 74694, 34967)
Port: 3000 LISTEN
```

---

## 🔍 접속 문제 해결

### 1. 브라우저에서 직접 접속
다음 URL을 **브라우저 주소창**에 입력하세요:

```
http://localhost:3000
```

또는

```
http://127.0.0.1:3000
```

### 2. 백엔드 API 확인
먼저 백엔드가 작동하는지 확인:

```
http://localhost:8001/docs
```

### 3. 프론트엔드 재시작 (필요 시)
터미널에서 실행:

```bash
cd /Users/dennis/finance-hub/frontend
npm run dev
```

### 4. 캐시 문제 해결
브라우저에서:
- **Chrome/Edge**: `Ctrl + Shift + R` (Hard Refresh)
- **Safari**: `Cmd + Option + R`
- **Firefox**: `Ctrl + F5`

---

## 🎯 접속 가능한 페이지

### 메인 페이지
```
http://localhost:3000/
→ 대시보드 (AI 추천, 시장 지수, 포트폴리오)
```

### 주요 기능
```
http://localhost:3000/stocks-list
→ 인기 종목 목록

http://localhost:3000/stocks/AAPL
→ Apple 종목 상세

http://localhost:3000/portfolio
→ 포트폴리오 관리

http://localhost:3000/watchlist
→ 관심 종목

http://localhost:3000/prediction-map
→ AI 예측 맵

http://localhost:3000/discovery
→ 신규 발굴
```

---

## 🐛 문제 진단

### 증상별 해결 방법

#### "사이트에 연결할 수 없음"
1. 서버 상태 확인:
   ```bash
   lsof -ti:3000
   ```
2. 재시작:
   ```bash
   cd /Users/dennis/finance-hub/frontend
   npm run dev
   ```

#### "데이터가 표시되지 않음"
1. 백엔드 확인:
   ```bash
   curl http://localhost:8001/health
   ```
2. 환경변수 확인:
   ```bash
   cat /Users/dennis/finance-hub/frontend/.env.local
   ```
   → `NEXT_PUBLIC_API_URL=http://localhost:8001` 확인

#### "로딩이 계속됨"
1. 브라우저 콘솔 확인 (F12)
2. Network 탭에서 실패한 요청 확인
3. CORS 에러 시 백엔드 재시작

---

## 🔧 서버 관리 명령어

### 서버 상태 확인
```bash
# 백엔드
lsof -ti:8001

# 프론트엔드
lsof -ti:3000
```

### 서버 중지
```bash
# 백엔드 중지
kill $(lsof -ti:8001)

# 프론트엔드 중지
kill $(lsof -ti:3000)
```

### 서버 시작
```bash
# 백엔드 시작
cd /Users/dennis/finance-hub/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001

# 프론트엔드 시작 (새 터미널)
cd /Users/dennis/finance-hub/frontend
npm run dev
```

---

## 📱 모바일/태블릿 접속

같은 WiFi 네트워크에서:

1. 컴퓨터의 IP 주소 확인:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. 모바일에서 접속:
   ```
   http://[컴퓨터IP]:3000
   예: http://192.168.1.100:3000
   ```

---

## ✅ 정상 작동 확인 방법

### 1. 백엔드 Health Check
```bash
curl http://localhost:8001/health
```
**기대 결과**:
```json
{"status":"healthy"}
```

### 2. 예측 데이터 확인
```bash
curl http://localhost:8001/api/v1/predictions/summary | head -20
```
**기대 결과**: 28개 종목 예측 JSON

### 3. 프론트엔드 HTML 확인
브라우저에서 `http://localhost:3000` 접속 후:
- 페이지 소스 보기 (`Ctrl+U`)
- `<title>` 태그 확인
- JavaScript 에러 없는지 콘솔 확인 (F12)

---

## 💡 자주 묻는 질문

### Q: 포트를 변경하고 싶어요
**A**:
```bash
# 백엔드
uvicorn app.main:app --reload --port 8002

# 프론트엔드 (package.json 수정)
"scripts": {
  "dev": "next dev -p 3001"
}
```

### Q: 외부 네트워크에서 접속하고 싶어요
**A**:
```bash
# 백엔드
uvicorn app.main:app --host 0.0.0.0 --port 8001

# 프론트엔드
next dev -H 0.0.0.0
```

### Q: 로그를 보고 싶어요
**A**:
```bash
# 백엔드 로그
cd backend
# uvicorn 실행 터미널에서 확인

# 프론트엔드 로그
cd frontend
# npm run dev 실행 터미널에서 확인
```

---

## 🎯 최종 체크리스트

접속 전 확인사항:

- [ ] 백엔드 서버 실행 중 (`lsof -ti:8001`)
- [ ] 프론트엔드 서버 실행 중 (`lsof -ti:3000`)
- [ ] 백엔드 Health Check 통과
- [ ] 브라우저 캐시 삭제
- [ ] JavaScript 활성화
- [ ] 방화벽/안티바이러스 확인

---

**작성일**: 2025-11-21
**서버 상태**: 실행 중
**예상 해결 시간**: 1-5분
