"""Portfolio schemas"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.holding import HoldingResponse


class PortfolioBase(BaseModel):
    """Base portfolio schema"""

    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio"""

    pass


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio"""

    name: Optional[str] = None
    description: Optional[str] = None


class PortfolioResponse(PortfolioBase):
    """Schema for portfolio response"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PortfolioWithHoldings(PortfolioResponse):
    """Portfolio with holdings included"""

    holdings: List["HoldingResponse"] = []

    model_config = ConfigDict(from_attributes=True)
