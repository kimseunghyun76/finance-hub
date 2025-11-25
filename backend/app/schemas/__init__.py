"""Pydantic schemas for request/response validation"""
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioWithHoldings,
)
from app.schemas.holding import (
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse,
    HoldingWithPrice,
)
from app.schemas.stock import StockInfo, StockPrice

# Rebuild models to resolve forward references
PortfolioWithHoldings.model_rebuild()

__all__ = [
    "PortfolioCreate",
    "PortfolioUpdate",
    "PortfolioResponse",
    "PortfolioWithHoldings",
    "HoldingCreate",
    "HoldingUpdate",
    "HoldingResponse",
    "HoldingWithPrice",
    "StockInfo",
    "StockPrice",
]
