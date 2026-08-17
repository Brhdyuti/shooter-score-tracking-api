from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

from database import SessionLocal, init_db, Shooter, PracticeSession, Score

app = FastAPI(title="Shooter Score Tracking API")

init_db()  # creates shooters.db and tables if they don't exist


# ---------- Pydantic schemas (define what data looks like in/out) ----------

class ShooterCreate(BaseModel):
    name: str
    email: str
    join_date: date

class ShooterOut(ShooterCreate):
    id: int
    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    shooter_id: int
    date: date
    discipline: str
    notes: Optional[str] = None

class SessionOut(SessionCreate):
    id: int
    class Config:
        from_attributes = True


class ScoreCreate(BaseModel):
    session_id: int
    target_number: int
    score: float
    max_possible_score: float

class ScoreOut(ScoreCreate):
    id: int
    class Config:
        from_attributes = True


# ---------- Helper to get a DB session ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Shooter endpoints ----------

@app.post("/shooters", response_model=ShooterOut)
def create_shooter(shooter: ShooterCreate):
    db = SessionLocal()
    db_shooter = Shooter(**shooter.dict())
    db.add(db_shooter)
    db.commit()
    db.refresh(db_shooter)
    db.close()
    return db_shooter


@app.get("/shooters", response_model=List[ShooterOut])
def list_shooters():
    db = SessionLocal()
    shooters = db.query(Shooter).all()
    db.close()
    return shooters


@app.get("/shooters/{shooter_id}", response_model=ShooterOut)
def get_shooter(shooter_id: int):
    db = SessionLocal()
    shooter = db.query(Shooter).filter(Shooter.id == shooter_id).first()
    db.close()
    if not shooter:
        raise HTTPException(status_code=404, detail="Shooter not found")
    return shooter


# ---------- Session endpoints ----------

@app.post("/sessions", response_model=SessionOut)
def create_session(session: SessionCreate):
    db = SessionLocal()
    db_session = PracticeSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    db.close()
    return db_session


@app.get("/sessions/{shooter_id}", response_model=List[SessionOut])
def get_sessions_for_shooter(shooter_id: int):
    db = SessionLocal()
    sessions = db.query(PracticeSession).filter(PracticeSession.shooter_id == shooter_id).all()
    db.close()
    return sessions


# ---------- Score endpoints ----------

@app.post("/scores", response_model=ScoreOut)
def add_score(score: ScoreCreate):
    db = SessionLocal()
    db_score = Score(**score.dict())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    db.close()
    return db_score


# ---------- Stats endpoint (the "meaty logic" piece) ----------

@app.get("/shooters/{shooter_id}/stats")
def get_shooter_stats(shooter_id: int):
    db = SessionLocal()
    shooter = db.query(Shooter).filter(Shooter.id == shooter_id).first()
    if not shooter:
        db.close()
        raise HTTPException(status_code=404, detail="Shooter not found")

    sessions = db.query(PracticeSession).filter(PracticeSession.shooter_id == shooter_id).all()
    session_ids = [s.id for s in sessions]

    scores = db.query(Score).filter(Score.session_id.in_(session_ids)).all()
    db.close()

    if not scores:
        return {"shooter_id": shooter_id, "total_sessions": len(sessions), "message": "No scores recorded yet"}

    percentages = [(s.score / s.max_possible_score) * 100 for s in scores]

    return {
        "shooter_id": shooter_id,
        "total_sessions": len(sessions),
        "total_scores_recorded": len(scores),
        "average_percentage": round(sum(percentages) / len(percentages), 2),
        "best_percentage": round(max(percentages), 2),
        "worst_percentage": round(min(percentages), 2),
    }