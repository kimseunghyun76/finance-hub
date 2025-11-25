import requests
import sys
import json

BASE_URL = "http://localhost:8001/api/v1"
ENDPOINTS = [
    # Stocks
    ("GET", "/stocks/AAPL/quote"),
    ("GET", "/stocks/AAPL/info"),
    ("GET", "/stocks/AAPL/history?period=1mo"),
    ("GET", "/stocks/AAPL/analyst-targets"),
    ("GET", "/stocks/AAPL/fundamentals"),
    ("GET", "/stocks/search?query=Apple"),
    ("GET", "/stocks/fear-greed"),
    
    # Predictions
    ("GET", "/predictions/AAPL"),
    ("GET", "/predictions/summary"),
    ("GET", "/predictions/models/details"),
    
    # Portfolios (might fail if no auth/data, but checking 500s)
    ("GET", "/portfolios"),
    
    # Holdings
    # ("GET", "/holdings/portfolio/1"), # Needs valid ID
]

def test_endpoints():
    print(f"🚀 Starting API Diagnosis on {BASE_URL}...\n")
    
    success_count = 0
    fail_count = 0
    
    for method, endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        print(f"Testing {method} {endpoint}...", end=" ", flush=True)
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✅ OK")
                success_count += 1
            else:
                print(f"❌ FAILED ({response.status_code})")
                print(f"   Response: {response.text[:200]}")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            fail_count += 1
            
    print(f"\n{'-'*50}")
    print(f"📊 Diagnosis Complete")
    print(f"✅ Passed: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"{'-'*50}")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    test_endpoints()
