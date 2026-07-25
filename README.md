# 🤖 AI Meeting & Follow-Up Agent

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![AWS S3](https://img.shields.io/badge/AWS-S3-orange)

## 📌 Project Overview

AI Meeting & Follow-Up Agent is an Agentic AI system that converts meeting recordings or transcripts into structured tasks, assigns owners and deadlines, and autonomously follows up until work is completed.

---

# Table of Contents

1. Project Overview
2. Problem Statement
3. Objectives
4. Features
5. System Architecture
6. Agent Workflow
7. Tech Stack
8. Folder Structure
9. Database Schema
10. REST APIs
11. Installation
12. Environment Variables
13. AI Models
14. LangGraph Workflow
15. Development Roadmap
16. Deployment
17. Future Scope
18. Contributing
19. License

---

# Problem Statement

Organizations conduct numerous meetings every day. Although important decisions and action items are discussed, they often remain untracked after the meeting ends.

Challenges include:

- Missing follow-ups
- Forgotten deadlines
- Manual reminder emails
- Lack of accountability
- No centralized tracking

This project solves these issues using Agentic AI.

---

# Objectives

- Convert meeting audio into text.
- Extract decisions and action items.
- Detect owners and deadlines.
- Store structured tasks.
- Send automated reminders.
- Escalate overdue tasks.
- Provide analytics dashboard.

---

# Key Features

- 🎤 Speech-to-text using Whisper
- 🧠 LLM-powered meeting understanding
- 📋 Action item extraction
- 👤 Owner assignment
- 📅 Deadline extraction
- 📧 Email reminders
- 💬 Slack / Teams / WhatsApp integration
- 📈 Analytics dashboard
- 🔄 Autonomous follow-up loop
- 🔐 JWT Authentication

---

# System Architecture

```text
Meeting Audio
      │
      ▼
 Whisper
      │
 Transcript
      │
      ▼
 GPT / LLM
      │
 Decisions + Tasks
      │
      ▼
 PostgreSQL
      │
      ▼
 Reminder Scheduler
      │
      ▼
 Email / Slack / Teams
      │
      ▼
 Dashboard
```

---

# Agent Workflow

1. Upload Agent
2. Speech Agent
3. Transcript Agent
4. Summary Agent
5. Action Item Agent
6. Assignment Agent
7. Reminder Agent
8. Escalation Agent
9. Dashboard Agent

---

# Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI |
| AI | GPT-5 / Llama, Whisper |
| Agent Framework | LangGraph |
| Database | PostgreSQL |
| Queue | Celery + Redis |
| Storage | AWS S3 |
| Deployment | Docker + Nginx + EC2 |

---

# Folder Structure

```text
AI-Meeting-Agent/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── ai/
│   │   ├── workflows/
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── database/
│   │   ├── core/
│   │   ├── middleware/
│   │   ├── templates/
│   │   └── utils/
│   ├── uploads/
│   ├── tests/
│   ├── logs/
│   └── alembic/
├── docs/
├── nginx/
├── scripts/
└── README.md
```

---

# Database Schema

## users

- id
- name
- email
- password
- role

## meetings

- id
- title
- transcript
- summary
- recording_url

## tasks

- id
- meeting_id
- owner
- description
- deadline
- priority
- status

## notifications

- id
- task_id
- channel
- sent_at
- status

---

# REST API

## Authentication

- POST /auth/register
- POST /auth/login
- POST /auth/refresh

## Meetings

- POST /api/meetings/upload
- GET /api/meetings
- GET /api/meetings/{id}

## Tasks

- GET /api/tasks
- PUT /api/tasks/{id}
- DELETE /api/tasks/{id}

## Notifications

- POST /api/reminders/send
- GET /api/reminders/history

---

# Installation

```bash
git clone <repo-url>
cd AI-Meeting-Agent
```

## Backend

```bash
cd backend
python -m venv venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# Environment Variables

Backend `.env`

```env
DATABASE_URL=
SECRET_KEY=
OPENAI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
BREVO_API_KEY=
REDIS_URL=
JWT_SECRET=
```

Frontend `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

# AI Models

- OpenAI Whisper
- GPT-5 / GPT-4.1
- Optional: Llama 3

---

# LangGraph Workflow

```text
Upload
 ↓
Transcribe
 ↓
Understand
 ↓
Extract Tasks
 ↓
Assign Owner
 ↓
Store
 ↓
Notify
 ↓
Monitor
 ↓
Escalate
```

---

# Development Roadmap

- Authentication
- Dashboard
- Upload
- Whisper
- LLM
- Task Extraction
- Notifications
- Scheduler
- LangGraph
- Docker
- Deployment

---

# Deployment

- Docker
- Docker Compose
- Nginx
- AWS EC2
- AWS S3
- PostgreSQL

---

# Future Scope

- Jira integration
- Trello integration
- GitHub Issues
- Calendar sync
- Risk prediction
- Live meeting support
- Multi-language meetings

---

# Screenshots

```
docs/screenshots/
dashboard.png
upload.png
tasks.png
analytics.png
```

---

# Demo

- Demo Video: *(Add link)*
- Live URL: *(Add URL)*

---

# Contributing

1. Fork repository.
2. Create feature branch.
3. Commit changes.
4. Open Pull Request.

---

# License

MIT License

---

# References

- FastAPI
- Next.js
- PostgreSQL
- LangGraph
- OpenAI Whisper
- Docker
- AWS

---

## Author

**Ashish Lokapure**

B.Tech CSE (AI) | Full Stack Developer | AI/ML Enthusiast

If you like this project, ⭐ star the repository.
