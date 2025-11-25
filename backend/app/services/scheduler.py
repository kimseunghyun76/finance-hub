"""Background scheduler for automatic data collection and model training"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.holding import Holding
from app.models.stock_price import StockPrice
from app.models.scheduler_log import SchedulerLog
from app.services.data_fetcher import StockDataFetcher
import logging
import os
import sys

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()

# Add scripts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def log_job_start(job_id: str, job_name: str) -> int:
    """Log job start to database, returns log id"""
    db = SessionLocal()
    try:
        log_entry = SchedulerLog(
            job_id=job_id,
            job_name=job_name,
            status="started",
            message=f"Job {job_name} started",
            started_at=datetime.utcnow(),
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry.id
    except Exception as e:
        logger.error(f"Failed to log job start: {e}")
        return None
    finally:
        db.close()


def log_job_complete(log_id: int, success_count: int = 0, failed_count: int = 0, message: str = None):
    """Log job completion to database"""
    if log_id is None:
        return
    db = SessionLocal()
    try:
        log_entry = db.query(SchedulerLog).filter(SchedulerLog.id == log_id).first()
        if log_entry:
            log_entry.status = "completed"
            log_entry.success_count = success_count
            log_entry.failed_count = failed_count
            log_entry.message = message or f"Completed: {success_count} success, {failed_count} failed"
            log_entry.completed_at = datetime.utcnow()
            log_entry.duration_seconds = int((log_entry.completed_at - log_entry.started_at).total_seconds())
            db.commit()
    except Exception as e:
        logger.error(f"Failed to log job completion: {e}")
    finally:
        db.close()


def log_job_failed(log_id: int, error_message: str):
    """Log job failure to database"""
    if log_id is None:
        return
    db = SessionLocal()
    try:
        log_entry = db.query(SchedulerLog).filter(SchedulerLog.id == log_id).first()
        if log_entry:
            log_entry.status = "failed"
            log_entry.message = error_message
            log_entry.completed_at = datetime.utcnow()
            log_entry.duration_seconds = int((log_entry.completed_at - log_entry.started_at).total_seconds())
            db.commit()
    except Exception as e:
        logger.error(f"Failed to log job failure: {e}")
    finally:
        db.close()


def collect_stock_prices():
    """Collect and cache stock prices for all holdings"""
    log_id = log_job_start("collect_prices", "가격 수집")
    db = SessionLocal()
    success_count = 0
    failed_count = 0
    try:
        # Get all unique tickers from holdings
        holdings = db.query(Holding).all()
        unique_tickers = list(set([h.ticker for h in holdings]))

        logger.info(f"Starting price collection for {len(unique_tickers)} tickers")

        for ticker in unique_tickers:
            try:
                # Fetch historical data (last 7 days)
                df = StockDataFetcher.fetch_yahoo_finance(ticker, period="7d")

                if df is None or df.empty:
                    logger.warning(f"No data for {ticker}")
                    continue

                # Save to database
                for _, row in df.iterrows():
                    price_date = row['date'].date() if hasattr(row['date'], 'date') else row['date']

                    # Check if already exists
                    existing = (
                        db.query(StockPrice)
                        .filter(
                            StockPrice.ticker == ticker,
                            StockPrice.date == price_date
                        )
                        .first()
                    )

                    if existing:
                        # Update existing
                        existing.open = row['open']
                        existing.high = row['high']
                        existing.low = row['low']
                        existing.close = row['close']
                        existing.volume = int(row['volume'])
                        existing.adj_close = row.get('adj close')
                    else:
                        # Insert new
                        price = StockPrice(
                            ticker=ticker,
                            date=price_date,
                            open=row['open'],
                            high=row['high'],
                            low=row['low'],
                            close=row['close'],
                            volume=int(row['volume']),
                            adj_close=row.get('adj close')
                        )
                        db.add(price)

                db.commit()
                logger.info(f"Updated prices for {ticker}")
                success_count += 1

            except Exception as e:
                logger.error(f"Error collecting prices for {ticker}: {e}")
                db.rollback()
                failed_count += 1
                continue

        logger.info("Price collection completed")

        # Check for price alerts after collection
        try:
            from app.services.notification_service import NotificationService
            NotificationService.check_price_alerts(db)
        except Exception as e:
            logger.error(f"Error checking price alerts: {e}")

        log_job_complete(log_id, success_count, failed_count)

    except Exception as e:
        logger.error(f"Error in collect_stock_prices: {e}")
        db.rollback()
        log_job_failed(log_id, str(e))
    finally:
        db.close()


def cleanup_old_data():
    """Remove stock price data older than 2 years"""
    log_id = log_job_start("cleanup_data", "데이터 정리")
    db = SessionLocal()
    try:
        cutoff_date = datetime.now().date() - timedelta(days=730)  # 2 years

        deleted = (
            db.query(StockPrice)
            .filter(StockPrice.date < cutoff_date)
            .delete()
        )

        db.commit()
        logger.info(f"Cleaned up {deleted} old stock price records")
        log_job_complete(log_id, deleted, 0, f"Deleted {deleted} old records")

    except Exception as e:
        logger.error(f"Error in cleanup_old_data: {e}")
        db.rollback()
        log_job_failed(log_id, str(e))
    finally:
        db.close()


def update_prediction_actuals():
    """Update actual prices for predictions (daily)"""
    log_id = log_job_start("update_actuals", "예측 실제가 업데이트")
    try:
        from scripts.update_actual_prices import update_actual_prices

        logger.info("🔄 Starting automatic actual price update...")
        update_actual_prices(days_back=7)
        logger.info("✅ Actual price update completed")
        log_job_complete(log_id, 1, 0, "Actual price update completed")

    except Exception as e:
        logger.error(f"❌ Error in update_prediction_actuals: {e}")
        log_job_failed(log_id, str(e))


def refresh_prediction_cache():
    """Refresh prediction cache for all trained models (every 30 minutes)"""
    log_id = log_job_start("refresh_cache", "예측 캐시 갱신")
    try:
        from app.api.predictions import predict_stock_price
        import os

        db = SessionLocal()
        model_dir = "models"

        if not os.path.exists(model_dir):
            logger.warning(f"Model directory {model_dir} does not exist")
            log_job_complete(log_id, 0, 0, "Model directory does not exist")
            db.close()
            return

        # Get all trained models
        trained_tickers = []
        for file in os.listdir(model_dir):
            if file.endswith("_model.h5"):
                ticker = file.replace("_model.h5", "").replace("_", ".")
                trained_tickers.append(ticker)

        logger.info(f"🔄 Refreshing prediction cache for {len(trained_tickers)} trained models...")

        success_count = 0
        failed_count = 0

        for ticker in trained_tickers:
            try:
                # Generate fresh prediction (will cache automatically)
                predict_stock_price(ticker, db)
                success_count += 1
                logger.info(f"✅ Refreshed cache for {ticker}")
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Failed to refresh cache for {ticker}: {str(e)}")

        logger.info(f"Cache refresh completed: {success_count} success, {failed_count} failed")
        log_job_complete(log_id, success_count, failed_count)
        db.close()

    except Exception as e:
        logger.error(f"Error in refresh_prediction_cache: {e}")
        log_job_failed(log_id, str(e))


def start_scheduler():
    """Start the background scheduler"""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return

    # Schedule price collection for Korean stocks
    # Run every weekday at 3:35 PM KST (after Korean market close)
    scheduler.add_job(
        collect_stock_prices,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour=15,
            minute=35
        ),
        id='collect_prices_kr',
        name='Collect Korean stock prices (KR market close)',
        replace_existing=True
    )

    # Schedule price collection for US stocks
    # Run every weekday at 6:05 AM KST (after US market close, EST 4PM = KST 6AM)
    scheduler.add_job(
        collect_stock_prices,
        trigger=CronTrigger(
            day_of_week='tue-sat',  # US Mon-Fri = KR Tue-Sat morning
            hour=6,
            minute=5
        ),
        id='collect_prices_us',
        name='Collect US stock prices (US market close)',
        replace_existing=True
    )

    # Schedule actual price updates for predictions
    # Run after both market collections (evening)
    scheduler.add_job(
        update_prediction_actuals,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour=16,
            minute=0
        ),
        id='update_actuals',
        name='Update prediction actual prices',
        replace_existing=True
    )

    # Schedule data cleanup
    # Run every Sunday at 2 AM
    scheduler.add_job(
        cleanup_old_data,
        trigger=CronTrigger(
            day_of_week='sun',
            hour=2,
            minute=0
        ),
        id='cleanup_data',
        name='Cleanup old data',
        replace_existing=True
    )

    # Schedule portfolio holdings training (daily at 8 AM)
    scheduler.add_job(
        train_portfolio_holdings,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour=8,
            minute=0
        ),
        id='train_portfolio',
        name='Train portfolio holdings (daily)',
        replace_existing=True
    )

    # Schedule untrained recommended stocks training (daily at 8:30 AM)
    scheduler.add_job(
        train_untrained_recommended,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour=8,
            minute=30
        ),
        id='train_untrained',
        name='Train untrained recommended stocks (daily)',
        replace_existing=True
    )

    # Schedule all recommended stocks training (weekly on Monday at 9 AM)
    scheduler.add_job(
        train_all_recommended_weekly,
        trigger=CronTrigger(
            day_of_week='mon',
            hour=9,
            minute=0
        ),
        id='train_weekly',
        name='Train all recommended stocks (weekly)',
        replace_existing=True
    )

    # Schedule prediction cache refresh (every 30 minutes during market hours)
    # Run at :00 and :30 of every hour from 9 AM to 5 PM on weekdays
    scheduler.add_job(
        refresh_prediction_cache,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour='9-17',
            minute='0,30'
        ),
        id='refresh_cache',
        name='Refresh prediction cache (every 30 min)',
        replace_existing=True
    )

    # Schedule portfolio rebalancing check (daily at 5 PM after market close)
    scheduler.add_job(
        check_portfolio_rebalancing,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour=17,
            minute=0
        ),
        id='check_rebalancing',
        name='Check portfolio rebalancing needs (daily)',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started successfully")
    logger.info("Scheduled jobs:")
    logger.info("  - collect_prices_kr: Mon-Fri 15:35 (한국 장 종료 후 가격 수집)")
    logger.info("  - collect_prices_us: Tue-Sat 06:05 (미국 장 종료 후 가격 수집)")
    logger.info("  - update_actuals: Mon-Fri 16:00 (예측 실제 가격 업데이트)")
    logger.info("  - cleanup_data: Sun 02:00 (데이터 정리)")
    logger.info("  - train_portfolio: Mon-Fri 08:00 (포트폴리오 매일 훈련)")
    logger.info("  - train_untrained: Mon-Fri 08:30 (미훈련 추천주 매일 훈련)")
    logger.info("  - train_weekly: Mon 09:00 (전체 추천주 주간 훈련)")
    logger.info("  - refresh_cache: Mon-Fri 09:00-17:00 every 30min (예측 캐시 갱신)")
    logger.info("  - check_rebalancing: Mon-Fri 17:00 (포트폴리오 리밸런싱 체크)")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def train_portfolio_holdings():
    """Train models for portfolio holdings (daily)"""
    log_id = log_job_start("train_portfolio", "포트폴리오 훈련")
    try:
        from scripts.train_model import train_model_for_ticker

        db = SessionLocal()

        # Get unique tickers from holdings (포트폴리오에 담긴 주식)
        holdings = db.query(Holding).all()
        holding_tickers = list(set([h.ticker for h in holdings]))

        logger.info(f"📊 Daily training for {len(holding_tickers)} portfolio holdings")

        success_count = 0
        failed_count = 0

        for ticker in holding_tickers:
            try:
                logger.info(f"Training portfolio stock: {ticker}...")
                train_model_for_ticker(ticker, save_dir="models")
                success_count += 1
                logger.info(f"✅ Successfully trained {ticker}")
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Failed to train {ticker}: {str(e)}")

        logger.info(f"Portfolio training completed: {success_count} success, {failed_count} failed")
        log_job_complete(log_id, success_count, failed_count)
        db.close()

    except Exception as e:
        logger.error(f"Error in train_portfolio_holdings: {e}")
        log_job_failed(log_id, str(e))


def train_untrained_recommended():
    """Train untrained recommended stocks (daily)"""
    log_id = log_job_start("train_untrained", "미훈련 추천주 훈련")
    try:
        from scripts.train_model import train_model_for_ticker
        import os

        # Recommended stocks list
        recommended_tickers = [
            # US Stocks - Popular
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            # US Stocks - Recommended
            'AVGO', 'ORCL', 'NFLX', 'AMD', 'INTC', 'QCOM', 'CSCO', 'CRM', 'ADBE',
            # Korean Stocks - Popular
            '005930.KS', '000660.KS', '035420.KS', '035720.KS',
            # Korean Stocks - Recommended
            '051910.KS', '006400.KS', '207940.KS', '068270.KS', '105560.KS', '055550.KS'
        ]

        # Check which models are already trained
        model_dir = "models"
        trained_models = set()
        if os.path.exists(model_dir):
            for file in os.listdir(model_dir):
                if file.endswith("_model.h5"):
                    ticker = file.replace("_model.h5", "").replace("_", ".")
                    trained_models.add(ticker)

        # Filter untrained stocks
        untrained_tickers = [t for t in recommended_tickers if t not in trained_models]

        if not untrained_tickers:
            logger.info("🎯 All recommended stocks are already trained")
            log_job_complete(log_id, 0, 0, "All recommended stocks already trained")
            return

        logger.info(f"🆕 Daily training for {len(untrained_tickers)} untrained recommended stocks")

        success_count = 0
        failed_count = 0

        for ticker in untrained_tickers:
            try:
                logger.info(f"Training new recommended stock: {ticker}...")
                train_model_for_ticker(ticker, save_dir="models")
                success_count += 1
                logger.info(f"✅ Successfully trained {ticker}")
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Failed to train {ticker}: {str(e)}")

        logger.info(f"Untrained recommended training completed: {success_count} success, {failed_count} failed")
        log_job_complete(log_id, success_count, failed_count)

    except Exception as e:
        logger.error(f"Error in train_untrained_recommended: {e}")
        log_job_failed(log_id, str(e))


def train_all_recommended_weekly():
    """Train all recommended stocks (weekly)"""
    log_id = log_job_start("train_weekly", "전체 추천주 주간 훈련")
    try:
        from scripts.train_model import train_model_for_ticker

        # All recommended stocks
        all_recommended = [
            # US Stocks - Popular
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            # US Stocks - Recommended
            'AVGO', 'ORCL', 'NFLX', 'AMD', 'INTC', 'QCOM', 'CSCO', 'CRM', 'ADBE',
            # Korean Stocks - Popular
            '005930.KS', '000660.KS', '035420.KS', '035720.KS',
            # Korean Stocks - Recommended
            '051910.KS', '006400.KS', '207940.KS', '068270.KS', '105560.KS', '055550.KS'
        ]

        logger.info(f"📅 Weekly training for {len(all_recommended)} recommended stocks")

        success_count = 0
        failed_count = 0

        for ticker in all_recommended:
            try:
                logger.info(f"Weekly training: {ticker}...")
                train_model_for_ticker(ticker, save_dir="models")
                success_count += 1
                logger.info(f"✅ Successfully trained {ticker}")
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Failed to train {ticker}: {str(e)}")

        logger.info(f"Weekly training completed: {success_count} success, {failed_count} failed")
        log_job_complete(log_id, success_count, failed_count)

    except Exception as e:
        logger.error(f"Error in train_all_recommended_weekly: {e}")
        log_job_failed(log_id, str(e))


def check_portfolio_rebalancing():
    """Check all portfolios for rebalancing needs (daily)"""
    log_id = log_job_start("check_rebalancing", "포트폴리오 리밸런싱 체크")
    db = SessionLocal()
    try:
        from app.models.portfolio import Portfolio
        from app.services.rebalancer import Rebalancer
        from app.services.notification_service import NotificationService

        # Get all active portfolios
        portfolios = db.query(Portfolio).all()

        if not portfolios:
            logger.info("No portfolios to check for rebalancing")
            log_job_complete(log_id, 0, 0, "No portfolios found")
            return

        logger.info(f"⚖️ Checking {len(portfolios)} portfolios for rebalancing needs...")

        rebalancer = Rebalancer(db)

        checked_count = 0
        needs_rebalancing = 0
        notification_count = 0

        for portfolio in portfolios:
            try:
                # Check if rebalancing is needed using async wrapper
                import asyncio
                check_result = asyncio.run(rebalancer.check_rebalancing_needed(portfolio.id))

                checked_count += 1

                if check_result['needs_rebalancing']:
                    needs_rebalancing += 1
                    severity = check_result['severity']
                    triggers = check_result['triggers']
                    severity_score = check_result.get('severity_score', 0)

                    logger.info(f"⚠️ Portfolio {portfolio.name} (ID: {portfolio.id}) needs rebalancing - Severity: {severity}")
                    logger.info(f"   Triggers: {', '.join(triggers)}")

                    # Create notification for user using existing method
                    details = {
                        'portfolio_id': portfolio.id,
                        'severity': severity,
                        'triggers': triggers,
                        'severity_score': severity_score,
                        'timestamp': datetime.utcnow().isoformat()
                    }

                    NotificationService.create_rebalance_notification(
                        db=db,
                        user_id=portfolio.user_id,  # Send to portfolio owner
                        portfolio_name=portfolio.name,
                        deviation_percent=severity_score,  # Use severity score as deviation indicator
                        details=details
                    )
                    notification_count += 1

                else:
                    logger.info(f"✅ Portfolio {portfolio.name} (ID: {portfolio.id}) is balanced")

            except Exception as e:
                logger.error(f"❌ Failed to check portfolio {portfolio.id}: {str(e)}")
                continue

        logger.info(f"Rebalancing check completed: {checked_count} checked, {needs_rebalancing} need rebalancing, {notification_count} notifications sent")
        log_job_complete(log_id, checked_count, 0, f"{needs_rebalancing} portfolios need rebalancing")

    except Exception as e:
        logger.error(f"Error in check_portfolio_rebalancing: {e}")
        db.rollback()
        log_job_failed(log_id, str(e))
    finally:
        db.close()


def train_all_models():
    """Legacy function for manual training - trains everything"""
    try:
        from scripts.train_model import train_model_for_ticker

        db = SessionLocal()

        # Get unique tickers from holdings
        holdings = db.query(Holding).all()
        holding_tickers = list(set([h.ticker for h in holdings]))

        # All recommended stocks
        recommended_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'AVGO', 'ORCL', 'NFLX', 'AMD', 'INTC', 'QCOM', 'CSCO', 'CRM', 'ADBE',
            '005930.KS', '000660.KS', '035420.KS', '035720.KS',
            '051910.KS', '006400.KS', '207940.KS', '068270.KS', '105560.KS', '055550.KS'
        ]

        # Combine and deduplicate
        all_tickers = list(set(holding_tickers + recommended_tickers))

        logger.info(f"🔄 Manual training for {len(all_tickers)} stocks")

        success_count = 0
        failed_count = 0

        for ticker in all_tickers:
            try:
                logger.info(f"Training model for {ticker}...")
                train_model_for_ticker(ticker, save_dir="models")
                success_count += 1
                logger.info(f"✅ Successfully trained {ticker}")
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Failed to train {ticker}: {str(e)}")

        logger.info(f"Training completed: {success_count} success, {failed_count} failed")
        db.close()

    except Exception as e:
        logger.error(f"Error in train_all_models: {e}")


def run_manual_collection():
    """Manually trigger price collection (for testing)"""
    logger.info("Manual price collection triggered")
    collect_stock_prices()
