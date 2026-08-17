# Shooter Score Tracking API

A REST API for tracking shooters, their practice sessions, and scores at a shooting range — built as a project applying skills from a technical internship (system design, database management, API integration, testing, and version control).

## Features
- Manage shooter profiles
- Log practice sessions per shooter
- Record scores per target within a session
- Auto-calculated stats: average, best, and worst score percentage per shooter

## Tech Stack
- **FastAPI** — API framework
- **SQLAlchemy** — ORM / database layer
- **SQLite** — database
- **Pytest** — automated testing

## Setup

\`\`\`bash
python -m venv venv
venv\Scripts\Activate      # Windows
pip install fastapi uvicorn sqlalchemy pytest httpx
uvicorn main:app --reload
\`\`\`

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Running Tests

\`\`\`bash
pytest
\`\`\`

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | /shooters | Create a shooter |
| GET | /shooters | List all shooters |
| GET | /shooters/{id} | Get a shooter |
| POST | /sessions | Log a practice session |
| GET | /sessions/{shooter_id} | Get sessions for a shooter |
| POST | /scores | Add a score to a session |
| GET | /shooters/{id}/stats | Get average/best/worst score % for a shooter |
