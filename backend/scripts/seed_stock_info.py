"""Seed stock information database with popular stocks and ETFs"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.sector import StockInfo, SectorType, AssetType

# Stock and ETF data
STOCK_DATA = [
    # US Technology - AI/Cloud
    {"ticker": "AAPL", "name": "Apple Inc.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Consumer Electronics", "country": "US", "description": "iPhone, Mac, Services"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Cloud & AI", "country": "US", "description": "Azure, Office, AI (Copilot, OpenAI)"},
    {"ticker": "GOOGL", "name": "Alphabet (Google)", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Search & AI", "country": "US", "description": "Search, Cloud, AI (Gemini, DeepMind)"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "AI Chips", "country": "US", "description": "GPU, AI Training/Inference Chips"},
    {"ticker": "META", "name": "Meta Platforms", "asset_type": AssetType.STOCK, "sector": SectorType.COMMUNICATION,
     "industry": "Social Media", "country": "US", "description": "Facebook, Instagram, WhatsApp, AI"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "asset_type": AssetType.STOCK, "sector": SectorType.CONSUMER,
     "industry": "E-commerce & Cloud", "country": "US", "description": "Online Retail, AWS Cloud"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "asset_type": AssetType.STOCK, "sector": SectorType.CONSUMER,
     "industry": "Electric Vehicles", "country": "US", "description": "EVs, Energy Storage, AI (FSD)"},

    # US Technology - Semiconductor & Software
    {"ticker": "AMD", "name": "AMD", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Semiconductors", "country": "US", "description": "CPU, GPU, Data Center Chips"},
    {"ticker": "INTC", "name": "Intel Corp.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Semiconductors", "country": "US", "description": "CPU, Foundry, AI Chips"},
    {"ticker": "QCOM", "name": "Qualcomm Inc.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Mobile Chips", "country": "US", "description": "Mobile SoC, 5G, IoT"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Semiconductors", "country": "US", "description": "Networking, Broadband, Storage"},
    {"ticker": "ORCL", "name": "Oracle Corp.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Enterprise Software", "country": "US", "description": "Database, Cloud, ERP"},
    {"ticker": "CRM", "name": "Salesforce", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Cloud CRM", "country": "US", "description": "CRM, Sales, Service Cloud"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Creative Software", "country": "US", "description": "Photoshop, AI Creative Tools"},
    {"ticker": "CSCO", "name": "Cisco Systems", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Networking", "country": "US", "description": "Enterprise Networking, Security"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "asset_type": AssetType.STOCK, "sector": SectorType.COMMUNICATION,
     "industry": "Streaming", "country": "US", "description": "Streaming Entertainment"},

    # Korean Stocks - Technology
    {"ticker": "005930.KS", "name": "삼성전자", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Semiconductors", "country": "KR", "description": "Memory Chips, Smartphones, Displays"},
    {"ticker": "000660.KS", "name": "SK하이닉스", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Memory Chips", "country": "KR", "description": "DRAM, NAND Flash, HBM"},
    {"ticker": "035420.KS", "name": "NAVER", "asset_type": AssetType.STOCK, "sector": SectorType.COMMUNICATION,
     "industry": "Internet Platform", "country": "KR", "description": "Search, E-commerce, Cloud"},
    {"ticker": "035720.KS", "name": "카카오", "asset_type": AssetType.STOCK, "sector": SectorType.COMMUNICATION,
     "industry": "Messaging & Platform", "country": "KR", "description": "KakaoTalk, Payment, Mobility"},

    # Korean Stocks - Other Sectors
    {"ticker": "051910.KS", "name": "LG화학", "asset_type": AssetType.STOCK, "sector": SectorType.MATERIALS,
     "industry": "Chemicals & Battery", "country": "KR", "description": "EV Batteries, Petrochemicals"},
    {"ticker": "006400.KS", "name": "삼성SDI", "asset_type": AssetType.STOCK, "sector": SectorType.TECHNOLOGY,
     "industry": "Battery", "country": "KR", "description": "EV Batteries, Energy Storage"},
    {"ticker": "207940.KS", "name": "삼성바이오로직스", "asset_type": AssetType.STOCK, "sector": SectorType.HEALTHCARE,
     "industry": "Biopharmaceutical", "country": "KR", "description": "Bio CDMO Services"},
    {"ticker": "068270.KS", "name": "셀트리온", "asset_type": AssetType.STOCK, "sector": SectorType.HEALTHCARE,
     "industry": "Biopharmaceutical", "country": "KR", "description": "Biosimilars, Antibody Drugs"},
    {"ticker": "105560.KS", "name": "KB금융", "asset_type": AssetType.STOCK, "sector": SectorType.FINANCE,
     "industry": "Banking", "country": "KR", "description": "Commercial Banking, Investment"},
    {"ticker": "055550.KS", "name": "신한지주", "asset_type": AssetType.STOCK, "sector": SectorType.FINANCE,
     "industry": "Banking", "country": "KR", "description": "Commercial Banking, Cards"},

    # US ETFs - Market Index
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF", "asset_type": AssetType.ETF, "sector": None,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Market Index",
     "expense_ratio": 0.0945, "description": "S&P 500 Index Tracker"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust", "asset_type": AssetType.ETF, "sector": SectorType.TECHNOLOGY,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Tech Index",
     "expense_ratio": 0.20, "description": "NASDAQ-100 Tracker (Tech Heavy)"},
    {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "asset_type": AssetType.ETF, "sector": None,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Market Index",
     "expense_ratio": 0.03, "description": "Total US Stock Market"},
    {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "asset_type": AssetType.ETF, "sector": None,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Market Index",
     "expense_ratio": 0.03, "description": "S&P 500 Low-Cost Tracker"},

    # US ETFs - Sector Specific
    {"ticker": "XLK", "name": "Technology Select Sector SPDR", "asset_type": AssetType.ETF, "sector": SectorType.TECHNOLOGY,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Sector - Technology",
     "expense_ratio": 0.10, "description": "US Technology Stocks"},
    {"ticker": "XLF", "name": "Financial Select Sector SPDR", "asset_type": AssetType.ETF, "sector": SectorType.FINANCE,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Sector - Finance",
     "expense_ratio": 0.10, "description": "US Financial Stocks"},
    {"ticker": "XLE", "name": "Energy Select Sector SPDR", "asset_type": AssetType.ETF, "sector": SectorType.ENERGY,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Sector - Energy",
     "expense_ratio": 0.10, "description": "US Energy Stocks"},
    {"ticker": "XLV", "name": "Health Care Select Sector SPDR", "asset_type": AssetType.ETF, "sector": SectorType.HEALTHCARE,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Sector - Healthcare",
     "expense_ratio": 0.10, "description": "US Healthcare Stocks"},

    # US ETFs - Thematic
    {"ticker": "ARKK", "name": "ARK Innovation ETF", "asset_type": AssetType.ETF, "sector": SectorType.TECHNOLOGY,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Thematic - Innovation",
     "expense_ratio": 0.75, "description": "Disruptive Innovation (AI, Genomics, Fintech)"},
    {"ticker": "BOTZ", "name": "Global X Robotics & AI ETF", "asset_type": AssetType.ETF, "sector": SectorType.TECHNOLOGY,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Thematic - AI/Robotics",
     "expense_ratio": 0.68, "description": "AI & Robotics Companies"},
    {"ticker": "SOXX", "name": "iShares Semiconductor ETF", "asset_type": AssetType.ETF, "sector": SectorType.TECHNOLOGY,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Thematic - Semiconductors",
     "expense_ratio": 0.35, "description": "Semiconductor Industry"},
    {"ticker": "FINX", "name": "Global X FinTech ETF", "asset_type": AssetType.ETF, "sector": SectorType.FINANCE,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Thematic - FinTech",
     "expense_ratio": 0.68, "description": "Financial Technology"},

    # US ETFs - International & Bond
    {"ticker": "EWY", "name": "iShares MSCI South Korea ETF", "asset_type": AssetType.ETF, "sector": None,
     "industry": None, "country": "KR", "is_etf": 1, "etf_category": "Country - Korea",
     "expense_ratio": 0.59, "description": "South Korean Stocks"},
    {"ticker": "EEM", "name": "iShares MSCI Emerging Markets ETF", "asset_type": AssetType.ETF, "sector": None,
     "industry": None, "country": "GLOBAL", "is_etf": 1, "etf_category": "Emerging Markets",
     "expense_ratio": 0.68, "description": "Emerging Market Stocks"},
    {"ticker": "AGG", "name": "iShares Core US Aggregate Bond ETF", "asset_type": AssetType.ETF, "sector": None,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Bonds",
     "expense_ratio": 0.03, "description": "US Investment Grade Bonds"},
    {"ticker": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "asset_type": AssetType.ETF, "sector": None,
     "industry": None, "country": "US", "is_etf": 1, "etf_category": "Bonds - Treasury",
     "expense_ratio": 0.15, "description": "Long-term US Treasury Bonds"},
]


def seed_stock_info():
    """Seed stock information database"""
    db = SessionLocal()

    try:
        print("🌱 Seeding stock information...")

        added = 0
        updated = 0

        for stock_data in STOCK_DATA:
            # Check if exists
            existing = db.query(StockInfo).filter(StockInfo.ticker == stock_data["ticker"]).first()

            if existing:
                # Update existing
                for key, value in stock_data.items():
                    setattr(existing, key, value)
                updated += 1
                print(f"  ✏️  Updated: {stock_data['ticker']} - {stock_data['name']}")
            else:
                # Add new
                stock_info = StockInfo(**stock_data)
                db.add(stock_info)
                added += 1
                print(f"  ✅ Added: {stock_data['ticker']} - {stock_data['name']}")

        db.commit()

        print(f"\n📊 Summary:")
        print(f"  ✅ Added: {added} stocks/ETFs")
        print(f"  ✏️  Updated: {updated} stocks/ETFs")
        print(f"  📈 Total: {len(STOCK_DATA)} entries")

        # Print statistics
        total = db.query(StockInfo).count()
        stocks = db.query(StockInfo).filter(StockInfo.is_etf == 0).count()
        etfs = db.query(StockInfo).filter(StockInfo.is_etf == 1).count()

        print(f"\n📈 Database Statistics:")
        print(f"  Total Entries: {total}")
        print(f"  Stocks: {stocks}")
        print(f"  ETFs: {etfs}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_stock_info()
