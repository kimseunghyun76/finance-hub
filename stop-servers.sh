#!/bin/bash

# Finance Hub - 서버 중지 스크립트
# 백엔드(FastAPI)와 프론트엔드(Next.js) 서버를 중지합니다

echo "=================================================="
echo "🛑 Finance Hub 서버 중지 중..."
echo "=================================================="

# 백엔드 서버 중지 (포트 8001)
echo ""
echo "🔧 백엔드 서버 중지 중..."
if lsof -ti:8001 > /dev/null 2>&1; then
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    echo "✅ 백엔드 서버 중지됨 (포트 8001)"
else
    echo "✓  백엔드 서버가 실행 중이지 않습니다"
fi

# 프론트엔드 서버 중지 (포트 3000)
echo ""
echo "🎨 프론트엔드 서버 중지 중..."
if lsof -ti:3000 > /dev/null 2>&1; then
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    echo "✅ 프론트엔드 서버 중지됨 (포트 3000)"
else
    echo "✓  프론트엔드 서버가 실행 중이지 않습니다"
fi

echo ""
echo "=================================================="
echo "✅ 모든 서버가 중지되었습니다"
echo "=================================================="
echo ""
echo "다시 시작하려면: ./start-servers.sh"
echo ""
