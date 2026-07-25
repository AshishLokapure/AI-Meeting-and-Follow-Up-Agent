from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models import AILog, Meeting, MeetingSummary, MeetingTranscript, Task
from app.models.employee import Employee
from app.models.enums import MeetingStatus, TaskPriority, TaskStatus


@dataclass(frozen=True)
class AnalysisResult:
    executive_summary: str
    decisions: list[dict[str, Any]]
    action_items: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    model_name: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    raw_response: dict[str, Any] | None = None
    fallback_used: bool = False


class AIAnalysisService:
    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _normalise_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _first_sentence(text: str) -> str:
        match = re.split(r"(?<=[.!?])\s+", text.strip())
        return match[0] if match else text.strip()

    @classmethod
    def _build_fallback_analysis(cls, transcript_text: str, model_name: str) -> AnalysisResult:
        text = cls._normalise_text(transcript_text)
        first_sentence = cls._first_sentence(text)
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]

        decisions: list[dict[str, Any]] = []
        risks: list[dict[str, Any]] = []
        action_items: list[dict[str, Any]] = []

        for sentence in sentences:
            lowered = sentence.lower()
            if any(keyword in lowered for keyword in ["decide", "agreed", "approved", "confirmed", "decision"]):
                decisions.append({"decision": sentence, "rationale": "Detected by keyword matching"})
            if any(keyword in lowered for keyword in ["risk", "issue", "concern", "blocker", "challenge"]):
                risks.append({"risk": sentence, "impact": "Requires follow-up", "mitigation": None})
            if any(keyword in lowered for keyword in ["action item", "todo", "follow up", "need to", "will", "should"]):
                action_items.append(
                    {
                        "task": sentence,
                        "owner": None,
                        "deadline": None,
                        "priority": "medium",
                        "details": "Extracted by keyword matching",
                    }
                )

        if not decisions:
            decisions = [
                {
                    "decision": first_sentence or "No explicit decision detected.",
                    "rationale": "Fallback summary",
                }
            ]
        if not action_items:
            action_items = [
                {
                    "task": "Review transcript and confirm action items.",
                    "owner": None,
                    "deadline": None,
                    "priority": "medium",
                    "details": "Fallback extraction",
                }
            ]
        if not risks:
            risks = [{"risk": "No explicit risk detected.", "impact": "Unknown", "mitigation": None}]

        return AnalysisResult(
            executive_summary=first_sentence or "Transcript available for review.",
            decisions=decisions,
            action_items=action_items,
            risks=risks,
            model_name=f"fallback-{model_name}",
            raw_response={
                "summary": first_sentence or "Transcript available for review.",
                "decisions": decisions,
                "action_items": action_items,
                "risks": risks,
            },
            fallback_used=True,
        )

    @staticmethod
    def _parse_analysis_payload(payload: dict[str, Any], model_name: str) -> AnalysisResult:
        summary = str(payload.get("summary") or payload.get("executive_summary") or "").strip()
        decisions = payload.get("decisions") or []
        action_items = payload.get("action_items") or []
        risks = payload.get("risks") or []
        if not summary:
            raise ValueError("Analysis payload missing summary")

        return AnalysisResult(
            executive_summary=summary,
            decisions=list(decisions),
            action_items=list(action_items),
            risks=list(risks),
            model_name=model_name,
            raw_response=payload,
        )

    @classmethod
    def _call_openai(cls, transcript_text: str) -> AnalysisResult:
        settings = get_settings()
        if not settings.openai_api_key:
            return cls._build_fallback_analysis(transcript_text, settings.openai_model)

        try:
            from openai import OpenAI
        except ImportError:
            return cls._build_fallback_analysis(transcript_text, settings.openai_model)

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "You analyze meeting transcripts and return strict JSON with these keys: "
            "summary, decisions, action_items, risks. "
            "summary should be a concise executive summary. "
            "decisions should be an array of objects with decision and rationale. "
            "action_items should be an array of objects with task, owner, deadline, priority, and details. "
            "risks should be an array of objects with risk, impact, and mitigation. "
            "If owner or deadline is unclear, use null. "
            "Do not add markdown fences."
        )

        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcript_text},
                ],
            )

            message = response.choices[0].message.content or "{}"
            payload = json.loads(message)
            result = cls._parse_analysis_payload(payload, settings.openai_model)
            usage = getattr(response, "usage", None)
            if usage is not None:
                result = AnalysisResult(
                    executive_summary=result.executive_summary,
                    decisions=result.decisions,
                    action_items=result.action_items,
                    risks=result.risks,
                    model_name=result.model_name,
                    prompt_tokens=getattr(usage, "prompt_tokens", None),
                    completion_tokens=getattr(usage, "completion_tokens", None),
                    total_tokens=getattr(usage, "total_tokens", None),
                    raw_response=payload,
                    fallback_used=False,
                )
            return result
        except Exception:
            return cls._build_fallback_analysis(transcript_text, settings.openai_model)

    @classmethod
    def analyze_meeting(cls, db: Session, meeting: Meeting) -> AnalysisResult:
        transcript = db.scalar(select(MeetingTranscript).where(MeetingTranscript.meeting_id == meeting.id))
        if transcript is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transcript not available for analysis")

        transcript_text = transcript.cleaned_text or transcript.transcript_text
        analysis_result = cls._call_openai(transcript_text)

        summary = db.scalar(select(MeetingSummary).where(MeetingSummary.meeting_id == meeting.id))
        if summary is None:
            summary = MeetingSummary(
                meeting_id=meeting.id,
                executive_summary=analysis_result.executive_summary,
                decisions=analysis_result.decisions,
                action_items=analysis_result.action_items,
                risks=analysis_result.risks,
                model_name=analysis_result.model_name,
                analysis_payload=analysis_result.raw_response,
            )
            db.add(summary)
        else:
            summary.executive_summary = analysis_result.executive_summary
            summary.decisions = analysis_result.decisions
            summary.action_items = analysis_result.action_items
            summary.risks = analysis_result.risks
            summary.model_name = analysis_result.model_name
            summary.analysis_payload = analysis_result.raw_response

        meeting.status = MeetingStatus.analyzed.value

        # Persist action items as Task rows so the tasks API / dashboard reflect real data.
        existing_tasks = db.scalars(select(Task).where(Task.meeting_id == meeting.id)).all()
        if not existing_tasks:
            # Load all employees added by this meeting's owner for name-matching
            employees = db.scalars(
                select(Employee).where(
                    Employee.added_by_id == meeting.owner_id,
                    Employee.is_active.is_(True),
                )
            ).all()
            # Build lowercase name -> employee lookup
            emp_by_name = {e.name.lower(): e for e in employees}

            allowed_priorities = {item.value for item in TaskPriority}
            for item in analysis_result.action_items:
                raw_title = str(item.get("task") or item.get("title") or "").strip()
                if not raw_title:
                    continue
                raw_priority = str(item.get("priority") or TaskPriority.medium.value).lower().strip()
                if raw_priority == "urgent":
                    raw_priority = TaskPriority.critical.value
                if raw_priority not in allowed_priorities:
                    raw_priority = TaskPriority.medium.value

                # Match owner name from AI output to an employee
                raw_owner = str(item.get("owner") or "").strip().lower()
                matched_employee: Employee | None = None
                if raw_owner:
                    # exact match first
                    matched_employee = emp_by_name.get(raw_owner)
                    if not matched_employee:
                        # partial match — find first employee whose name contains the owner token
                        for emp_name, emp in emp_by_name.items():
                            if raw_owner in emp_name or emp_name in raw_owner:
                                matched_employee = emp
                                break
                if not matched_employee and employees:
                    # round-robin fallback: assign to employees in order
                    idx = analysis_result.action_items.index(item) % len(employees)
                    matched_employee = employees[idx]

                task = Task(
                    meeting_id=meeting.id,
                    assignee_id=meeting.owner_id,
                    assigned_by_id=meeting.owner_id,
                    title=raw_title[:255],
                    description=str(item.get("details") or item.get("description") or "").strip() or None,
                    priority=raw_priority,
                    status=TaskStatus.pending.value,
                    source_excerpt=raw_title,
                    extracted_metadata={
                        **(item if isinstance(item, dict) else {"raw": item}),
                        "matched_employee_id": matched_employee.id if matched_employee else None,
                        "matched_employee_email": matched_employee.email if matched_employee else None,
                        "matched_employee_name": matched_employee.name if matched_employee else None,
                    },
                    reminder_enabled=True,
                )
                db.add(task)

                # Send task assignment email to the matched employee immediately
                if matched_employee:
                    from app.services.email_service import EmailService
                    EmailService().send_task_assignment(
                        to=matched_employee.email,
                        assignee_name=matched_employee.name,
                        assigner_name="AI Meeting Agent",
                        task_title=raw_title,
                        task_description=task.description or "",
                        deadline=None,
                        priority=raw_priority,
                    )

        ai_log = AILog(
            meeting_id=meeting.id,
            operation="meeting_analysis",
            model_name=analysis_result.model_name,
            status="fallback" if analysis_result.fallback_used else "success",
            prompt_tokens=analysis_result.prompt_tokens,
            completion_tokens=analysis_result.completion_tokens,
            total_tokens=analysis_result.total_tokens,
            request_payload={
                "meeting_id": meeting.id,
                "transcript_length": len(transcript_text),
            },
            response_payload=analysis_result.raw_response,
            executed_at=cls._utcnow(),
        )
        db.add(ai_log)

        return analysis_result

    @classmethod
    def get_meeting_analysis(cls, db: Session, meeting_id: str) -> MeetingSummary | None:
        return db.scalar(select(MeetingSummary).where(MeetingSummary.meeting_id == meeting_id))
