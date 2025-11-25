"""Portfolio CRUD service"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate


class PortfolioService:
    """Service for portfolio CRUD operations"""

    @staticmethod
    def create_portfolio(db: Session, portfolio: PortfolioCreate, user_id: int) -> Portfolio:
        """Create a new portfolio"""
        db_portfolio = Portfolio(
            name=portfolio.name,
            description=portfolio.description,
            user_id=user_id,
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio

    @staticmethod
    def get_portfolio(db: Session, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    @staticmethod
    def get_portfolios_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Portfolio]:
        """Get all portfolios for a user"""
        return (
            db.query(Portfolio)
            .filter(Portfolio.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_portfolio(
        db: Session, portfolio_id: int, portfolio_update: PortfolioUpdate
    ) -> Optional[Portfolio]:
        """Update portfolio"""
        db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

        if not db_portfolio:
            return None

        update_data = portfolio_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_portfolio, field, value)

        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio

    @staticmethod
    def delete_portfolio(db: Session, portfolio_id: int) -> bool:
        """Delete portfolio"""
        db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

        if not db_portfolio:
            return False

        db.delete(db_portfolio)
        db.commit()
        return True
