"""Holding schemas"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional
from app.models.holding import MarketType


class HoldingBase(BaseModel):
    """Base holding schema"""

    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: Optional[str] = None
    market: MarketType
    quantity: float = Field(..., gt=0, description="Number of shares")
    avg_price: float = Field(..., gt=0, description="Average purchase price")
    purchase_date: date


class HoldingCreate(HoldingBase):
    """Schema for creating a holding"""

    portfolio_id: int


class HoldingUpdate(BaseModel):
    """Schema for updating a holding"""

    quantity: Optional[float] = Field(None, gt=0)
    avg_price: Optional[float] = Field(None, gt=0)
    purchase_date: Optional[date] = None


class HoldingResponse(HoldingBase):
    """Schema for holding response"""

    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HoldingWithPrice(HoldingResponse):
    """Holding with current price and P&L"""

    current_price: Optional[float] = None
    total_value: Optional[float] = None
    total_cost: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
