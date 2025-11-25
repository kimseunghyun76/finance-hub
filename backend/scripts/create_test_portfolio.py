"""Create test portfolio with holdings for testing"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, SessionLocal
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.user import User

def create_test_portfolio():
    """테스트용 포트폴리오 생성"""
    db = SessionLocal()

    try:
        # Check if user exists
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            print("❌ User with id=1 not found. Please create a user first.")
            return

        # Check if test portfolio exists
        existing = db.query(Portfolio).filter(Portfolio.name == "테스트 포트폴리오").first()
        if existing:
            print(f"✅ Test portfolio already exists (ID: {existing.id})")
            portfolio_id = existing.id
        else:
            # Create test portfolio
            portfolio = Portfolio(
                user_id=1,
                name="테스트 포트폴리오",
                description="성과 분석 테스트용 포트폴리오",
                initial_value=10000000.0,  # 1천만원
                target_return=15.0,  # 목표 수익률 15%
                risk_tolerance="medium"
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            portfolio_id = portfolio.id
            print(f"✅ Created test portfolio (ID: {portfolio_id})")

        # Check if holdings exist
        existing_holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        if existing_holdings:
            print(f"✅ Portfolio already has {len(existing_holdings)} holdings")
            return portfolio_id

        # Create test holdings
        from datetime import date
        from app.models.holding import MarketType

        test_holdings = [
            {"ticker": "AAPL", "quantity": 50, "avg_price": 150.0, "market": MarketType.NASDAQ},
            {"ticker": "GOOGL", "quantity": 20, "avg_price": 140.0, "market": MarketType.NASDAQ},
            {"ticker": "MSFT", "quantity": 30, "avg_price": 350.0, "market": MarketType.NASDAQ},
            {"ticker": "005930.KS", "quantity": 100, "avg_price": 70000.0, "market": MarketType.KRX},  # 삼성전자
            {"ticker": "TSLA", "quantity": 15, "avg_price": 250.0, "market": MarketType.NASDAQ},
        ]

        for h in test_holdings:
            holding = Holding(
                portfolio_id=portfolio_id,
                ticker=h["ticker"],
                quantity=h["quantity"],
                avg_price=h["avg_price"],
                market=h["market"],
                purchase_date=date.today()
            )
            db.add(holding)
            print(f"  Added: {h['ticker']} x {h['quantity']} @ {h['avg_price']}")

        db.commit()
        print(f"\n✅ Successfully created test portfolio with {len(test_holdings)} holdings!")
        print(f"\n🔗 Test portfolio ID: {portfolio_id}")
        print(f"\n📊 Try these APIs:")
        print(f"  - http://localhost:8001/api/v1/portfolios/{portfolio_id}/summary")
        print(f"  - http://localhost:8001/api/v1/portfolios/{portfolio_id}/performance")
        print(f"  - http://localhost:8001/api/v1/portfolios/{portfolio_id}/allocation")
        print(f"  - http://localhost:8001/api/v1/portfolios/{portfolio_id}/dividends")
        print(f"  - http://localhost:8001/api/v1/portfolios/{portfolio_id}/risk")

        return portfolio_id

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_portfolio()
