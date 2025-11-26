#!/bin/bash

# Finance Hub - 서버 재기동 스크립트
# 백엔드(FastAPI)와 프론트엔드(Next.js) 서버를 동시에 실행합니다

set -e  # 에러 발생시 스크립트 중단

echo "=================================================="
echo "🚀 Finance Hub 서버 재기동 중..."
echo "=================================================="

# 현재 실행 중인 서버 확인 및 종료
echo ""
echo "📋 1단계: 기존 서버 프로세스 확인 및 종료"
echo "--------------------------------------------------"

# 백엔드 포트 8001 확인
if lsof -ti:8001 > /dev/null 2>&1; then
    echo "⚠️  포트 8001에서 실행 중인 프로세스 발견. 종료 중..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    echo "✅ 백엔드 서버 종료 완료"
else
    echo "✓  포트 8001 사용 가능"
fi

# 프론트엔드 포트 3000 확인
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "⚠️  포트 3000에서 실행 중인 프로세스 발견. 종료 중..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo "✅ 프론트엔드 서버 종료 완료"
else
    echo "✓  포트 3000 사용 가능"
fi

sleep 1

# 백엔드 서버 시작
echo ""
echo "🔧 2단계: 백엔드 서버 시작 (FastAPI)"
echo "--------------------------------------------------"
cd /Users/dennis/finance-hub/backend

if [ ! -d "venv" ]; then
    echo "❌ 에러: Python 가상환경(venv)을 찾을 수 없습니다"
    echo "   다음 명령어로 가상환경을 생성하세요:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

echo "▶️  백엔드 서버 시작 중... (http://localhost:8001)"
nohup bash -c "source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001" > /tmp/finance-hub-backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 백엔드 서버 시작됨 (PID: $BACKEND_PID)"
echo "   로그: /tmp/finance-hub-backend.log"

sleep 2

# 백엔드 서버 상태 확인
if lsof -ti:8001 > /dev/null 2>&1; then
    echo "✓  백엔드 서버 정상 실행 중"
else
    echo "❌ 백엔드 서버 시작 실패. 로그를 확인하세요:"
    echo "   tail -f /tmp/finance-hub-backend.log"
    exit 1
fi

# 프론트엔드 서버 시작
echo ""
echo "🎨 3단계: 프론트엔드 서버 시작 (Next.js)"
echo "--------------------------------------------------"
cd /Users/dennis/finance-hub/frontend

if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules를 찾을 수 없습니다. npm install 실행 중..."
    npm install
fi

echo "▶️  프론트엔드 서버 시작 중... (http://localhost:3000)"
nohup npm run dev > /tmp/finance-hub-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 프론트엔드 서버 시작됨 (PID: $FRONTEND_PID)"
echo "   로그: /tmp/finance-hub-frontend.log"

sleep 3

# 프론트엔드 서버 상태 확인
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "✓  프론트엔드 서버 정상 실행 중"
else
    echo "❌ 프론트엔드 서버 시작 실패. 로그를 확인하세요:"
    echo "   tail -f /tmp/finance-hub-frontend.log"
    exit 1
fi

# 최종 상태 출력
echo ""
echo "=================================================="
echo "✅ 서버 재기동 완료!"
echo "=================================================="
echo ""
echo "📍 서버 정보:"
echo "   백엔드 (FastAPI):  http://localhost:8001"
echo "   프론트엔드 (Next.js): http://localhost:3000"
echo "   API 문서:          http://localhost:8001/docs"
echo ""
echo "📊 프로세스 ID:"
echo "   백엔드 PID:  $BACKEND_PID"
echo "   프론트엔드 PID: $FRONTEND_PID"
echo ""
echo "📝 로그 확인:"
echo "   백엔드:  tail -f /tmp/finance-hub-backend.log"
echo "   프론트엔드: tail -f /tmp/finance-hub-frontend.log"
echo ""
echo "🛑 서버 중지:"
echo "   ./stop-servers.sh (또는 아래 명령어)"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "=================================================="
