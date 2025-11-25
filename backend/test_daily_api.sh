#!/bin/bash

# Test save daily prediction
echo "=== Test 1: Save Daily Prediction ==="
curl -s -X POST "http://localhost:8001/api/v1/predictions/daily/save" \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","prediction_date":"2025-11-18","target_date":"2025-11-19","predicted_price":150.50,"current_price":148.00,"predicted_change":2.50,"predicted_change_percent":1.69,"confidence":0.85,"action":"BUY","model_type":"LSTM"}' | python3 -m json.tool

echo -e "\n\n=== Test 2: Get Daily Predictions ==="
curl -s "http://localhost:8001/api/v1/predictions/daily" | python3 -m json.tool

echo -e "\n\n=== Test 3: Get Daily Predictions for AAPL ==="
curl -s "http://localhost:8001/api/v1/predictions/daily?ticker=AAPL" | python3 -m json.tool

echo -e "\n\n=== Test 4: Get Accuracy Stats ==="
curl -s "http://localhost:8001/api/v1/predictions/daily/accuracy" | python3 -m json.tool
