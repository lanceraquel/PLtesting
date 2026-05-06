from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_session
from app.models import Company, ResearchResult, ResearchTask, TaskStatus
from app.reports.exporter import export_task_reports
from app.schemas import ResearchResultRead, ResearchTaskCreate, ResearchTaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=ResearchTaskRead, status_code=201)
def create_task(payload: ResearchTaskCreate, session: Session = Depends(get_session)) -> ResearchTask:
    task = ResearchTask(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("", response_model=list[ResearchTaskRead])
def list_tasks(session: Session = Depends(get_session)) -> list[ResearchTask]:
    return list(session.scalars(select(ResearchTask).order_by(ResearchTask.created_at.desc())).all())


@router.get("/{task_id}", response_model=ResearchTaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)) -> ResearchTask:
    task = session.get(ResearchTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/run", response_model=ResearchTaskRead)
def queue_task_run(task_id: int, session: Session = Depends(get_session)) -> ResearchTask:
    task = session.get(ResearchTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == TaskStatus.running.value:
        raise HTTPException(status_code=409, detail="Task is already running")
    task.status = TaskStatus.queued.value
    task.error_message = None
    session.commit()
    session.refresh(task)
    return task


@router.get("/{task_id}/results", response_model=list[ResearchResultRead])
def list_task_results(task_id: int, session: Session = Depends(get_session)) -> list[ResearchResult]:
    if session.get(ResearchTask, task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    stmt = (
        select(ResearchResult)
        .where(ResearchResult.task_id == task_id)
        .options(
            selectinload(ResearchResult.company).selectinload(Company.sources),
            selectinload(ResearchResult.company).selectinload(Company.contacts),
        )
        .order_by(ResearchResult.rank.asc().nullslast(), ResearchResult.relevance_score.desc())
    )
    return list(session.scalars(stmt).all())


@router.post("/{task_id}/reports", response_model=dict[str, str])
def generate_reports(task_id: int, session: Session = Depends(get_session)) -> dict[str, str]:
    task = session.get(ResearchTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    report_paths = export_task_reports(session, task)
    task.report_paths = report_paths
    session.commit()
    return report_paths
