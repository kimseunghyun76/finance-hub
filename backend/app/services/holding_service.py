"""Holding CRUD service"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.holding import Holding
from app.schemas.holding import HoldingCreate, HoldingUpdate
from app.services.data_fetcher import StockDataFetcher


class HoldingService:
    """Service for holding CRUD operations"""

    @staticmethod
    def create_holding(db: Session, holding: HoldingCreate) -> Holding:
        """Create a new holding"""
        # Fetch company name if not provided
        company_name = holding.company_name
        if not company_name:
            stock_info = StockDataFetcher.get_stock_info(holding.ticker)
            if stock_info:
                company_name = stock_info.get("name", "Unknown")

        db_holding = Holding(
            portfolio_id=holding.portfolio_id,
            ticker=holding.ticker,
            company_name=company_name,
            market=holding.market,
            quantity=holding.quantity,
            avg_price=holding.avg_price,
            purchase_date=holding.purchase_date,
        )
        db.add(db_holding)
        db.commit()
        db.refresh(db_holding)
        return db_holding

    @staticmethod
    def get_holding(db: Session, holding_id: int) -> Optional[Holding]:
        """Get holding by ID"""
        return db.query(Holding).filter(Holding.id == holding_id).first()

    @staticmethod
    def get_holdings_by_portfolio(
        db: Session, portfolio_id: int, skip: int = 0, limit: int = 100
    ) -> List[Holding]:
        """Get all holdings for a portfolio"""
        return (
            db.query(Holding)
            .filter(Holding.portfolio_id == portfolio_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_holding(
        db: Session, holding_id: int, holding_update: HoldingUpdate
    ) -> Optional[Holding]:
        """Update holding"""
        db_holding = db.query(Holding).filter(Holding.id == holding_id).first()

        if not db_holding:
            return None

        update_data = holding_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_holding, field, value)

        db.commit()
        db.refresh(db_holding)
        return db_holding

    @staticmethod
    def delete_holding(db: Session, holding_id: int) -> bool:
        """Delete holding"""
        db_holding = db.query(Holding).filter(Holding.id == holding_id).first()

        if not db_holding:
            return False

        db.delete(db_holding)
        db.commit()
        return True

    @staticmethod
    def get_holding_with_current_price(db: Session, holding_id: int) -> Optional[dict]:
        """Get holding with current price and P&L calculation"""
        db_holding = db.query(Holding).filter(Holding.id == holding_id).first()

        if not db_holding:
            return None

        # Get current price
        current_price = StockDataFetcher.get_current_price(db_holding.ticker)

        # Calculate P&L
        result = {
            "id": db_holding.id,
            "portfolio_id": db_holding.portfolio_id,
            "ticker": db_holding.ticker,
            "company_name": db_holding.company_name,
            "market": db_holding.market,
            "quantity": db_holding.quantity,
            "avg_price": db_holding.avg_price,
            "purchase_date": db_holding.purchase_date,
            "created_at": db_holding.created_at,
            "updated_at": db_holding.updated_at,
            "current_price": current_price,
        }

        if current_price:
            total_cost = db_holding.quantity * db_holding.avg_price
            total_value = db_holding.quantity * current_price
            profit_loss = total_value - total_cost
            profit_loss_percent = (profit_loss / total_cost) * 100

            result.update(
                {
                    "total_cost": total_cost,
                    "total_value": total_value,
                    "profit_loss": profit_loss,
                    "profit_loss_percent": profit_loss_percent,
                }
            )

        return result
