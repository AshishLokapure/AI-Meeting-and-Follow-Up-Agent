from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user
from app.core.settings import get_settings
from app.database import get_db
from app.models import Meeting
from app.schemas import (
    MeetingAnalysisPublic,
    MeetingAnalysisResponse,
    MeetingPublic,
    MeetingDetailPublic,
    MeetingParticipantPublic,
    MeetingListResponse,
    MeetingUploadResponse,
    TranscriptPublic,
    TranscriptResponse,
)
from app.services import AIAnalysisService, BackgroundJobService, MeetingService, TranscriptService
from app.workers.tasks import process_meeting_pipeline

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/upload", response_model=MeetingUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_meeting(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> MeetingUploadResponse:
    meeting, job, storage_backend = MeetingService.upload_meeting(db=db, user=current_user, file=file, title=title)
    db.commit()
    db.refresh(meeting)

    try:
        async_result = process_meeting_pipeline.delay(job.id)
        job = BackgroundJobService.mark_dispatched(db, job, async_result.id)
        # In development (eager mode), the job already finished in-process.
        if get_settings().environment == "development":
            db.refresh(job)
    except Exception as exc:
        try:
            # Fallback: run the pipeline inline if the broker is unavailable.
            process_meeting_pipeline.apply(args=[job.id])
            db.refresh(job)
        except Exception as inline_exc:
            BackgroundJobService.mark_failed(
                db,
                job.id,
                f"Failed to enqueue Celery job: {exc}; inline fallback failed: {inline_exc}",
            )
    db.commit()
    db.refresh(job)

    return MeetingUploadResponse(
        message="Meeting uploaded successfully",
        meeting=MeetingPublic.model_validate(meeting),
        storage_backend=storage_backend,
        job_id=job.id,
        job_status=job.status,
    )


@router.get("", response_model=MeetingListResponse)
def list_meetings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> MeetingListResponse:
    base = db.query(Meeting).filter(Meeting.owner_id == current_user.id)
    if status:
        base = base.filter(Meeting.status == status)
    if q:
        base = base.filter(Meeting.title.ilike(f"%{q}%"))

    total = base.count()
    meetings_list = base.order_by(Meeting.created_at.desc()).offset(offset).limit(limit).all()

    res_meetings = []
    for m in meetings_list:
        participants = [
            MeetingParticipantPublic(
                id=p.id,
                name=p.participant_name,
                email=p.participant_email,
                role=p.participant_role
            )
            for p in m.participants
        ]

        summary_text = m.summary.executive_summary if m.summary else ""
        action_items_count = len(m.tasks)
        decisions_count = len(m.summary.decisions) if (m.summary and m.summary.decisions) else 0

        detail = MeetingDetailPublic(
            id=m.id,
            title=m.title,
            status=m.status,
            recording_url=m.recording_url,
            recording_filename=m.recording_filename,
            recording_mime_type=m.recording_mime_type,
            recording_size_bytes=m.recording_size_bytes,
            duration_minutes=m.duration_minutes,
            duration_seconds=m.duration_seconds,
            owner_id=m.owner_id,
            meeting_date=m.meeting_date,
            start_time=m.start_time,
            agenda=m.agenda,
            created_at=m.created_at,
            updated_at=m.updated_at,
            participants=participants,
            summary_text=summary_text,
            action_items_count=action_items_count,
            decisions_count=decisions_count
        )
        res_meetings.append(detail)

    return MeetingListResponse(meetings=res_meetings, total=total)


@router.get("/{meeting_id}", response_model=MeetingDetailPublic)
def get_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> MeetingDetailPublic:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    participants = [
        MeetingParticipantPublic(
            id=p.id,
            name=p.participant_name,
            email=p.participant_email,
            role=p.participant_role
        )
        for p in meeting.participants
    ]

    summary_text = meeting.summary.executive_summary if meeting.summary else ""
    action_items_count = len(meeting.tasks)
    decisions_count = len(meeting.summary.decisions) if (meeting.summary and meeting.summary.decisions) else 0

    return MeetingDetailPublic(
        id=meeting.id,
        title=meeting.title,
        status=meeting.status,
        recording_url=meeting.recording_url,
        recording_filename=meeting.recording_filename,
        recording_mime_type=meeting.recording_mime_type,
        recording_size_bytes=meeting.recording_size_bytes,
        duration_minutes=meeting.duration_minutes,
        duration_seconds=meeting.duration_seconds,
        owner_id=meeting.owner_id,
        meeting_date=meeting.meeting_date,
        start_time=meeting.start_time,
        agenda=meeting.agenda,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        participants=participants,
        summary_text=summary_text,
        action_items_count=action_items_count,
        decisions_count=decisions_count
    )


@router.get("/{meeting_id}/transcript", response_model=TranscriptResponse)
def get_transcript(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> TranscriptResponse:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    transcript = TranscriptService.get_meeting_transcript(db, meeting_id)
    if transcript is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not available")

    return TranscriptResponse(
        message="Transcript fetched successfully",
        transcript=TranscriptPublic.model_validate(transcript),
        meeting_status=meeting.status,
    )


@router.get("/{meeting_id}/analysis", response_model=MeetingAnalysisResponse)
def get_analysis(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> MeetingAnalysisResponse:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    analysis = AIAnalysisService.get_meeting_analysis(db, meeting_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting analysis not available")

    return MeetingAnalysisResponse(
        message="Meeting analysis fetched successfully",
        analysis=MeetingAnalysisPublic.model_validate(analysis),
        meeting_status=meeting.status,
    )

