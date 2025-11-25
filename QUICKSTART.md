# 🚀 Finance-Hub 빠른 시작 가이드

API 개발이 완료되었습니다! 이제 바로 실행해볼 수 있습니다.

## 📋 완성된 기능

### ✅ Backend API
1. **Portfolio CRUD** - 포트폴리오 생성/조회/수정/삭제
2. **Holding CRUD** - 보유 종목 관리
3. **Stock API** - 실시간 주가 조회, 종목 정보, 과거 데이터

### ✅ Frontend UI
1. **대시보드** - 포트폴리오 요약 및 목록
2. **포트폴리오 상세** - 보유 종목 및 수익률 확인

---

## 🏃‍♂️ 3단계로 시작하기

### Step 1: 데이터베이스 설정 (5분)

```bash
# PostgreSQL 설치 (이미 설치되어 있다면 스킵)
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15

# 데이터베이스 생성
createdb finance_hub
```

### Step 2: 백엔드 실행 (3분)

```bash
# 터미널 1: 백엔드
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치 (처음 한 번만)
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 DATABASE_URL 확인/수정

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

**백엔드 실행 확인**: http://localhost:8000/docs

### Step 3: 프론트엔드 실행 (2분)

```bash
# 터미널 2: 프론트엔드
cd frontend

# 의존성 설치 (처음 한 번만)
npm install

# 환경 변수 설정
cp .env.example .env.local

# 서버 실행
npm run dev
```

**프론트엔드 실행 확인**: http://localhost:3000

---

## 🎯 API 테스트하기

### 1. Swagger UI 사용
http://localhost:8000/docs에서 모든 API를 테스트할 수 있습니다.

### 2. curl 명령어로 테스트

```bash
# Health Check
curl http://localhost:8000/health

# 포트폴리오 생성
curl -X POST http://localhost:8000/api/v1/portfolios \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Portfolio", "description": "Test portfolio"}'

# 포트폴리오 목록 조회
curl http://localhost:8000/api/v1/portfolios

# 주식 정보 조회 (Apple)
curl http://localhost:8000/api/v1/stocks/AAPL/info

# 실시간 시세 조회
curl http://localhost:8000/api/v1/stocks/AAPL/quote

# 한국 주식 (삼성전자)
curl http://localhost:8000/api/v1/stocks/005930.KS/quote
```

### 3. 프론트엔드에서 테스트

1. http://localhost:3000 접속
2. "대시보드 시작하기" 클릭
3. "+ 새 포트폴리오" 버튼으로 포트폴리오 생성 (현재는 API만 완성)

---

## 📊 샘플 데이터 추가하기

### Python으로 샘플 데이터 생성

```python
# backend/scripts/seed_data.py
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding, MarketType
from datetime import date

db = SessionLocal()

# 사용자 생성
user = User(email="test@example.com", hashed_password="dummy")
db.add(user)
db.commit()
db.refresh(user)

# 포트폴리오 생성
portfolio = Portfolio(
    user_id=user.id,
    name="테스트 포트폴리오",
    description="미국 + 한국 주식 포트폴리오"
)
db.add(portfolio)
db.commit()
db.refresh(portfolio)

# 보유 종목 추가
holdings = [
    # 미국 주식
    Holding(
        portfolio_id=portfolio.id,
        ticker="AAPL",
        company_name="Apple Inc.",
        market=MarketType.NASDAQ,
        quantity=10,
        avg_price=150.00,
        purchase_date=date(2024, 1, 15)
    ),
    Holding(
        portfolio_id=portfolio.id,
        ticker="GOOGL",
        company_name="Alphabet Inc.",
        market=MarketType.NASDAQ,
        quantity=5,
        avg_price=140.00,
        purchase_date=date(2024, 2, 1)
    ),
    # 한국 주식
    Holding(
        portfolio_id=portfolio.id,
        ticker="005930.KS",
        company_name="삼성전자",
        market=MarketType.KRX,
        quantity=20,
        avg_price=70000,
        purchase_date=date(2024, 3, 10)
    ),
]

for holding in holdings:
    db.add(holding)

db.commit()
print("✅ 샘플 데이터 생성 완료!")
print(f"Portfolio ID: {portfolio.id}")
db.close()
```

```bash
# 실행
cd backend
python scripts/seed_data.py
```

---

## 🔍 주요 엔드포인트

### Portfolios
- `POST /api/v1/portfolios` - 포트폴리오 생성
- `GET /api/v1/portfolios` - 목록 조회
- `GET /api/v1/portfolios/{id}` - 상세 조회 (보유 종목 포함)
- `PUT /api/v1/portfolios/{id}` - 수정
- `DELETE /api/v1/portfolios/{id}` - 삭제

### Holdings
- `POST /api/v1/holdings` - 종목 추가
- `GET /api/v1/holdings/portfolio/{portfolio_id}` - 포트폴리오별 종목 목록
- `GET /api/v1/holdings/{id}` - 종목 상세
- `GET /api/v1/holdings/{id}/with-price` - 현재가 포함 조회
- `PUT /api/v1/holdings/{id}` - 수정
- `DELETE /api/v1/holdings/{id}` - 삭제

### Stocks
- `GET /api/v1/stocks/{ticker}/info` - 종목 정보
- `GET /api/v1/stocks/{ticker}/quote` - 실시간 시세
- `GET /api/v1/stocks/{ticker}/history?period=1mo` - 과거 데이터

---

## 🐛 문제 해결

### 문제: 데이터베이스 연결 실패
**해결**:
```bash
# PostgreSQL이 실행 중인지 확인
pg_ctl status

# 실행되지 않았다면
brew services start postgresql@15  # macOS
sudo service postgresql start       # Linux
```

### 문제: 포트 충돌
**해결**:
```bash
# 백엔드를 다른 포트로 실행
uvicorn app.main:app --reload --port 8001

# 프론트엔드를 다른 포트로 실행
npm run dev -- -p 3001
```

### 문제: yfinance 데이터 조회 실패
**원인**: Yahoo Finance API 일시적 장애 또는 잘못된 티커 심볼

**해결**:
- 미국 주식: `AAPL`, `GOOGL`, `MSFT`
- 한국 주식: `005930.KS` (삼성전자), `000660.KS` (SK하이닉스)

### 문제: CORS 에러
**해결**: backend/.env에서 CORS_ORIGINS 확인
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 📚 다음 단계

### 현재 완성된 것 ✅
1. ✅ Backend API (Portfolio, Holding, Stock)
2. ✅ Frontend 기본 UI (대시보드, 포트폴리오 상세)
3. ✅ 실시간 주가 조회
4. ✅ 수익률 계산

### 다음에 구현할 것 🔜
1. 포트폴리오/종목 추가 모달/폼
2. 주가 데이터 자동 수집 스케줄러
3. 차트 컴포넌트 (Recharts)
4. LSTM 주가 예측 모델
5. 매매 신호 생성

---

## 🎉 성공!

이제 다음 명령어를 실행하면 됩니다:

```bash
# 터미널 1
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# 터미널 2
cd frontend && npm run dev
```

- **API 문서**: http://localhost:8000/docs
- **웹 앱**: http://localhost:3000
- **대시보드**: http://localhost:3000/dashboard

**문제가 생기면 SETUP.md를 참고하세요!** 🚀
