"""Scheduler API endpoints for viewing scheduler logs and status"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.scheduler_log import SchedulerLog
from app.services.scheduler import scheduler

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/logs")
def get_scheduler_logs(
    db: Session = Depends(get_db),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    days: int = Query(7, description="Number of days to fetch"),
    limit: int = Query(100, description="Maximum number of logs to return"),
):
    """Get scheduler execution logs"""
    query = db.query(SchedulerLog)

    # Filter by date range
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(SchedulerLog.started_at >= cutoff_date)

    # Filter by job_id if provided
    if job_id:
        query = query.filter(SchedulerLog.job_id == job_id)

    # Filter by status if provided
    if status:
        query = query.filter(SchedulerLog.status == status)

    # Order by most recent first
    logs = query.order_by(desc(SchedulerLog.started_at)).limit(limit).all()

    return {
        "logs": [log.to_dict() for log in logs],
        "total": len(logs),
        "filters": {
            "job_id": job_id,
            "status": status,
            "days": days,
        }
    }


@router.get("/status")
def get_scheduler_status():
    """Get current scheduler status and job information"""
    jobs = []

    if scheduler.running:
        for job in scheduler.get_jobs():
            next_run = job.next_run_time
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": next_run.isoformat() if next_run else None,
                "trigger": str(job.trigger),
            })

    return {
        "running": scheduler.running,
        "jobs": jobs,
        "job_count": len(jobs),
    }


@router.get("/jobs")
def get_scheduled_jobs():
    """Get list of all scheduled jobs with their schedules"""
    job_definitions = [
        {
            "id": "collect_prices",
            "name": "가격 수집",
            "description": "모든 보유 종목의 주가를 수집하고 캐시합니다",
            "schedule": "월-금 19:00",
            "cron": "day_of_week='mon-fri', hour=19, minute=0",
        },
        {
            "id": "update_actuals",
            "name": "예측 실제가 업데이트",
            "description": "예측의 실제 결과 가격을 업데이트합니다",
            "schedule": "월-금 19:30",
            "cron": "day_of_week='mon-fri', hour=19, minute=30",
        },
        {
            "id": "cleanup_data",
            "name": "데이터 정리",
            "description": "2년 이상 된 오래된 주가 데이터를 삭제합니다",
            "schedule": "일요일 02:00",
            "cron": "day_of_week='sun', hour=2, minute=0",
        },
        {
            "id": "train_portfolio",
            "name": "포트폴리오 훈련",
            "description": "포트폴리오에 담긴 종목의 모델을 훈련합니다",
            "schedule": "월-금 08:00",
            "cron": "day_of_week='mon-fri', hour=8, minute=0",
        },
        {
            "id": "train_untrained",
            "name": "미훈련 추천주 훈련",
            "description": "아직 훈련되지 않은 추천 종목의 모델을 훈련합니다",
            "schedule": "월-금 08:30",
            "cron": "day_of_week='mon-fri', hour=8, minute=30",
        },
        {
            "id": "train_weekly",
            "name": "전체 추천주 주간 훈련",
            "description": "모든 추천 종목의 모델을 주간 단위로 재훈련합니다",
            "schedule": "월요일 09:00",
            "cron": "day_of_week='mon', hour=9, minute=0",
        },
        {
            "id": "refresh_cache",
            "name": "예측 캐시 갱신",
            "description": "훈련된 모델의 예측 캐시를 갱신합니다",
            "schedule": "월-금 09:00-17:00 매 30분",
            "cron": "day_of_week='mon-fri', hour='9-17', minute='0,30'",
        },
    ]

    # Add runtime information if scheduler is running
    if scheduler.running:
        running_jobs = {job.id: job for job in scheduler.get_jobs()}
        for job_def in job_definitions:
            if job_def["id"] in running_jobs:
                job = running_jobs[job_def["id"]]
                job_def["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
                job_def["active"] = True
            else:
                job_def["next_run"] = None
                job_def["active"] = False
    else:
        for job_def in job_definitions:
            job_def["next_run"] = None
            job_def["active"] = False

    return {
        "scheduler_running": scheduler.running,
        "jobs": job_definitions,
    }


@router.get("/summary")
def get_scheduler_summary(
    db: Session = Depends(get_db),
    days: int = Query(7, description="Number of days for statistics"),
):
    """Get scheduler execution summary statistics"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get all logs within the time range
    logs = db.query(SchedulerLog).filter(
        SchedulerLog.started_at >= cutoff_date
    ).all()

    # Calculate statistics
    total_runs = len(logs)
    successful = sum(1 for log in logs if log.status == "completed")
    failed = sum(1 for log in logs if log.status == "failed")

    # Group by job_id
    job_stats = {}
    for log in logs:
        if log.job_id not in job_stats:
            job_stats[log.job_id] = {
                "job_id": log.job_id,
                "job_name": log.job_name,
                "total_runs": 0,
                "successful": 0,
                "failed": 0,
                "last_run": None,
                "avg_duration": 0,
            }

        stats = job_stats[log.job_id]
        stats["total_runs"] += 1

        if log.status == "completed":
            stats["successful"] += 1
        elif log.status == "failed":
            stats["failed"] += 1

        if log.completed_at:
            if stats["last_run"] is None or log.completed_at > datetime.fromisoformat(stats["last_run"]):
                stats["last_run"] = log.completed_at.isoformat()

        if log.duration_seconds:
            # Simple running average
            stats["avg_duration"] = (stats["avg_duration"] * (stats["total_runs"] - 1) + log.duration_seconds) / stats["total_runs"]

    return {
        "period_days": days,
        "total_runs": total_runs,
        "successful": successful,
        "failed": failed,
        "success_rate": round(successful / total_runs * 100, 1) if total_runs > 0 else 0,
        "by_job": list(job_stats.values()),
    }
