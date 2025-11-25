"""Investment insight model for AI-generated stock analysis"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from datetime import datetime
from app.database import Base


class InvestmentInsight(Base):
    """AI-generated investment insights for stocks"""
    __tablename__ = "investment_insights"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)

    # Analysis content
    buffett_analysis = Column(Text, nullable=True)  # Warren Buffett style analysis
    lynch_analysis = Column(Text, nullable=True)    # Peter Lynch style analysis
    graham_analysis = Column(Text, nullable=True)   # Benjamin Graham style analysis

    # Stock fundamentals used for analysis
    current_price = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)
    profit_margin = Column(Float, nullable=True)

    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Cache expiration
    is_valid = Column(Boolean, default=True, nullable=False)
    ai_model_used = Column(String, nullable=True)  # e.g., "groq-llama3"

    # Analysis summary
    overall_rating = Column(String, nullable=True)  # BUY, HOLD, SELL
    confidence_score = Column(Float, nullable=True)  # 0-100
    key_strengths = Column(Text, nullable=True)  # JSON array of strengths
    key_risks = Column(Text, nullable=True)  # JSON array of risks

    def __repr__(self):
        return f"<InvestmentInsight(ticker={self.ticker}, rating={self.overall_rating}, generated={self.generated_at})>"
