#!/bin/bash

# API 전체 테스트 스크립트
echo "=========================================="
echo "Finance Hub API 전체 테스트"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8001"
PORTFOLIO_ID=3

# 색상 코드
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=${4:-200}

    echo -n "Testing $name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL$endpoint")
    fi

    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_status)"
    fi
}

echo "1. Health Check"
echo "----------------------------------------"
test_endpoint "Health Check" GET "/health"
echo ""

echo "2. Stock APIs"
echo "----------------------------------------"
test_endpoint "Stock Search" GET "/api/v1/stocks/search?query=apple"
test_endpoint "Stock Info - AAPL" GET "/api/v1/stocks/AAPL/info"
test_endpoint "Stock Quote - AAPL" GET "/api/v1/stocks/AAPL/quote"
test_endpoint "Stock Info - Samsung" GET "/api/v1/stocks/005930.KS/info"
test_endpoint "Stock Quote - Samsung" GET "/api/v1/stocks/005930.KS/quote"
echo ""

echo "3. Portfolio Basic APIs"
echo "----------------------------------------"
test_endpoint "List Portfolios" GET "/api/v1/portfolios/"
test_endpoint "Get Portfolio Detail" GET "/api/v1/portfolios/$PORTFOLIO_ID"
echo ""

echo "4. Portfolio Performance APIs"
echo "----------------------------------------"
test_endpoint "Portfolio Performance" GET "/api/v1/portfolios/$PORTFOLIO_ID/performance"
test_endpoint "Asset Allocation" GET "/api/v1/portfolios/$PORTFOLIO_ID/allocation"
test_endpoint "Dividend Income" GET "/api/v1/portfolios/$PORTFOLIO_ID/dividends"
test_endpoint "Risk Metrics" GET "/api/v1/portfolios/$PORTFOLIO_ID/risk"
test_endpoint "Portfolio Summary" GET "/api/v1/portfolios/$PORTFOLIO_ID/summary"
echo ""

echo "5. Portfolio Advanced APIs"
echo "----------------------------------------"
test_endpoint "Create Snapshot" POST "/api/v1/portfolios/$PORTFOLIO_ID/snapshot"
test_endpoint "Portfolio History" GET "/api/v1/portfolios/$PORTFOLIO_ID/history?days=30"
test_endpoint "Rebalancing Recommendations" GET "/api/v1/portfolios/$PORTFOLIO_ID/rebalancing"
test_endpoint "Target Comparison" GET "/api/v1/portfolios/$PORTFOLIO_ID/target-comparison"
test_endpoint "Tax Calculation" GET "/api/v1/portfolios/$PORTFOLIO_ID/tax"
echo ""

echo "6. Education APIs"
echo "----------------------------------------"
test_endpoint "List Education Content" GET "/api/v1/education/articles"
test_endpoint "Get Education Detail" GET "/api/v1/education/articles/68"
echo ""

echo "7. Investment Insights APIs"
echo "----------------------------------------"
test_endpoint "Get Investment Insight - AAPL" GET "/api/v1/insights/AAPL"
echo ""

echo "=========================================="
echo "테스트 완료!"
echo "=========================================="
