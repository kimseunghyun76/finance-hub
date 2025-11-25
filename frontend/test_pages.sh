#!/bin/bash

# 프론트엔드 페이지 전체 테스트 스크립트
echo "=========================================="
echo "Finance Hub Frontend 페이지 테스트"
echo "=========================================="
echo ""

BASE_URL="http://localhost:3000"

# 색상 코드
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_page() {
    local name=$1
    local path=$2
    local expected_status=${3:-200}

    echo -n "Testing $name... "

    # Follow redirects and get final status code
    response=$(curl -s -o /dev/null -w "%{http_code}" -L "$BASE_URL$path" 2>&1)

    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_status)"
        return 1
    fi
}

# Test counters
total=0
passed=0
failed=0

run_test() {
    if test_page "$1" "$2" "$3"; then
        ((passed++))
    else
        ((failed++))
    fi
    ((total++))
}

echo "1. Core Pages"
echo "----------------------------------------"
run_test "Home Page" "/"
run_test "Education Page" "/education"
run_test "Explore Page" "/explore"
run_test "Discovery Page" "/discovery"
run_test "Compare Page" "/compare"
run_test "Backtest Page" "/backtest"
run_test "Guide Page" "/guide"
run_test "Settings Page" "/settings"
echo ""

echo "2. Portfolio Pages"
echo "----------------------------------------"
run_test "Portfolio Detail (ID 3)" "/portfolios/3"
run_test "Portfolio Analytics (ID 3)" "/portfolios/3/analytics"
run_test "Portfolio Rebalance (ID 3)" "/portfolios/3/rebalance"
echo ""

echo "3. Stock Pages"
echo "----------------------------------------"
run_test "Stock Detail - AAPL" "/stocks/AAPL"
run_test "Stock Detail - Samsung" "/stocks/005930.KS"
run_test "Stocks List Page" "/stocks-list"
run_test "Sectors Page" "/sectors"
echo ""

echo "4. Model & Analytics Pages"
echo "----------------------------------------"
run_test "Models Page" "/models"
run_test "Accuracy Page" "/accuracy"
run_test "Prediction Map" "/prediction-map"
run_test "Scheduler Page" "/scheduler"
echo ""

echo "=========================================="
echo "테스트 완료!"
echo "----------------------------------------"
echo -e "Total: $total | ${GREEN}Passed: $passed${NC} | ${RED}Failed: $failed${NC}"
echo "=========================================="

# Exit with error if any tests failed
if [ $failed -gt 0 ]; then
    exit 1
fi
