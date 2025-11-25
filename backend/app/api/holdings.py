"""Holding API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.holding import (
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse,
    HoldingWithPrice,
)
from app.services.holding_service import HoldingService

router = APIRouter()


@router.post("/", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(holding: HoldingCreate, db: Session = Depends(get_db)):
    """Create a new holding"""
    return HoldingService.create_holding(db, holding)


@router.get("/portfolio/{portfolio_id}", response_model=List[HoldingResponse])
def get_holdings_by_portfolio(
    portfolio_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all holdings for a portfolio"""
    return HoldingService.get_holdings_by_portfolio(db, portfolio_id, skip, limit)


@router.get("/{holding_id}", response_model=HoldingResponse)
def get_holding(holding_id: int, db: Session = Depends(get_db)):
    """Get holding by ID"""
    holding = HoldingService.get_holding(db, holding_id)
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with id {holding_id} not found",
        )
    return holding


@router.get("/{holding_id}/with-price", response_model=HoldingWithPrice)
def get_holding_with_price(holding_id: int, db: Session = Depends(get_db)):
    """Get holding with current price and P&L"""
    holding = HoldingService.get_holding_with_current_price(db, holding_id)
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with id {holding_id} not found",
        )
    return holding


@router.put("/{holding_id}", response_model=HoldingResponse)
def update_holding(
    holding_id: int,
    holding_update: HoldingUpdate,
    db: Session = Depends(get_db),
):
    """Update holding"""
    holding = HoldingService.update_holding(db, holding_id, holding_update)
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with id {holding_id} not found",
        )
    return holding


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    """Delete holding"""
    success = HoldingService.delete_holding(db, holding_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with id {holding_id} not found",
        )
    return None
