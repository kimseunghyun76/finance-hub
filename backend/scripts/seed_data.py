"""Seed database with sample data"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding, MarketType
from datetime import date

def seed_database():
    """Create sample data for testing"""
    db = SessionLocal()

    try:
        print("🌱 시작: 샘플 데이터 생성...")

        # 사용자 생성
        user = User(
            email="demo@finance-hub.com",
            hashed_password="dummy_hash_for_demo"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ 사용자 생성: {user.email}")

        # 포트폴리오 1: 미국 기술주
        portfolio1 = Portfolio(
            user_id=user.id,
            name="🇺🇸 미국 기술주 포트폴리오",
            description="FAANG + Microsoft 포트폴리오"
        )
        db.add(portfolio1)
        db.commit()
        db.refresh(portfolio1)
        print(f"✅ 포트폴리오 생성: {portfolio1.name}")

        # 미국 주식 종목 추가
        us_holdings = [
            Holding(
                portfolio_id=portfolio1.id,
                ticker="AAPL",
                company_name="Apple Inc.",
                market=MarketType.NASDAQ,
                quantity=10,
                avg_price=150.00,
                purchase_date=date(2024, 1, 15)
            ),
            Holding(
                portfolio_id=portfolio1.id,
                ticker="GOOGL",
                company_name="Alphabet Inc.",
                market=MarketType.NASDAQ,
                quantity=5,
                avg_price=140.00,
                purchase_date=date(2024, 2, 1)
            ),
            Holding(
                portfolio_id=portfolio1.id,
                ticker="MSFT",
                company_name="Microsoft Corporation",
                market=MarketType.NASDAQ,
                quantity=8,
                avg_price=380.00,
                purchase_date=date(2024, 1, 20)
            ),
            Holding(
                portfolio_id=portfolio1.id,
                ticker="AMZN",
                company_name="Amazon.com Inc.",
                market=MarketType.NASDAQ,
                quantity=6,
                avg_price=170.00,
                purchase_date=date(2024, 3, 5)
            ),
        ]

        for holding in us_holdings:
            db.add(holding)
            print(f"  📊 종목 추가: {holding.ticker} ({holding.quantity}주)")

        db.commit()

        # 포트폴리오 2: 한국 반도체 포트폴리오
        portfolio2 = Portfolio(
            user_id=user.id,
            name="🇰🇷 한국 반도체 포트폴리오",
            description="삼성전자, SK하이닉스 중심"
        )
        db.add(portfolio2)
        db.commit()
        db.refresh(portfolio2)
        print(f"✅ 포트폴리오 생성: {portfolio2.name}")

        # 한국 주식 종목 추가
        kr_holdings = [
            Holding(
                portfolio_id=portfolio2.id,
                ticker="005930.KS",
                company_name="삼성전자",
                market=MarketType.KRX,
                quantity=20,
                avg_price=72000,
                purchase_date=date(2024, 3, 10)
            ),
            Holding(
                portfolio_id=portfolio2.id,
                ticker="000660.KS",
                company_name="SK하이닉스",
                market=MarketType.KRX,
                quantity=15,
                avg_price=135000,
                purchase_date=date(2024, 2, 15)
            ),
        ]

        for holding in kr_holdings:
            db.add(holding)
            print(f"  📊 종목 추가: {holding.ticker} ({holding.quantity}주)")

        db.commit()

        print("\n" + "="*50)
        print("🎉 샘플 데이터 생성 완료!")
        print("="*50)
        print(f"\n사용자 ID: {user.id}")
        print(f"포트폴리오 1 ID: {portfolio1.id} ({len(us_holdings)}개 종목)")
        print(f"포트폴리오 2 ID: {portfolio2.id} ({len(kr_holdings)}개 종목)")
        print("\n📍 대시보드에서 확인: http://localhost:3000/dashboard")
        print(f"📍 포트폴리오 1: http://localhost:3000/portfolios/{portfolio1.id}")
        print(f"📍 포트폴리오 2: http://localhost:3000/portfolios/{portfolio2.id}")
        print()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
