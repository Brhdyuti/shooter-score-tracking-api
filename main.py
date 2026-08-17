from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from database import SessionLocal, init_db, Shooter, PracticeSession, Score, TargetDesign
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Shooter Score Tracking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="dashboard")
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
    target_design_id: Optional[int] = None
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


class TargetDesignCreate(BaseModel):
    name: str
    diameter_cm: float
    num_rings: int

class TargetDesignOut(TargetDesignCreate):
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


# ---------- Target Design endpoints ----------

@app.post("/target-designs", response_model=TargetDesignOut)
def create_target_design(design: TargetDesignCreate):
    db = SessionLocal()
    db_design = TargetDesign(**design.dict())
    db.add(db_design)
    db.commit()
    db.refresh(db_design)
    db.close()
    return db_design


@app.get("/target-designs/{design_id}/image")
def generate_target_image(design_id: int):
    db = SessionLocal()
    design = db.query(TargetDesign).filter(TargetDesign.id == design_id).first()
    db.close()

    if not design:
        raise HTTPException(status_code=404, detail="Target design not found")

    size = 500
    center = size / 2
    max_radius = center - 20
    ring_gap = max_radius / design.num_rings

    circles = ""
    colors = ["#FFD700", "#FFFFFF", "#000000", "#4169E1", "#DC143C"]

    for i in range(design.num_rings, 0, -1):
        radius = ring_gap * i
        value = design.num_rings - i + 1
        color = colors[(design.num_rings - i) % len(colors)]
        stroke = "black" if color == "#FFFFFF" else "none"
        text_color = "white" if color in ["#000000", "#4169E1", "#DC143C"] else "black"

        circles += f'<circle cx="{center}" cy="{center}" r="{radius:.1f}" fill="{color}" stroke="{stroke}" stroke-width="1"/>'
        label_radius = radius - (ring_gap / 2)
        circles += f'<text x="{center}" y="{center - label_radius + 5}" font-size="14" text-anchor="middle" fill="{text_color}">{value}</text>'

    ring_diameter_cm = round(design.diameter_cm / design.num_rings, 2)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size+60}" viewBox="0 0 {size} {size+60}">
        <rect width="{size}" height="{size+60}" fill="white"/>
        {circles}
        <text x="{center}" y="{size+30}" font-size="16" text-anchor="middle" fill="black">
            {design.name} - {design.diameter_cm}cm diameter, {design.num_rings} rings ({ring_diameter_cm}cm each)
        </text>
    </svg>'''

    return Response(content=svg, media_type="image/svg+xml")


# ---------- Detailed scores endpoint (for dashboard chart) ----------

@app.get("/shooters/{shooter_id}/scores-detail")
def get_scores_detail(shooter_id: int):
    db = SessionLocal()
    sessions = db.query(PracticeSession).filter(PracticeSession.shooter_id == shooter_id).all()
    session_map = {s.id: s.date for s in sessions}
    session_ids = list(session_map.keys())

    scores = db.query(Score).filter(Score.session_id.in_(session_ids)).all()
    db.close()

    result = []
    for s in scores:
        result.append({
            "date": session_map[s.session_id].isoformat(),
            "target_number": s.target_number,
            "score": s.score,
            "max_possible_score": s.max_possible_score,
            "percentage": round((s.score / s.max_possible_score) * 100, 2)
        })

    result.sort(key=lambda x: x["date"])
    return result


# ---------- Sessions with target design info (for dashboard) ----------

@app.get("/shooters/{shooter_id}/sessions-detail")
def get_sessions_detail(shooter_id: int):
    db = SessionLocal()
    sessions = db.query(PracticeSession).filter(PracticeSession.shooter_id == shooter_id).all()
    result = []
    for s in sessions:
        result.append({
            "session_id": s.id,
            "date": s.date.isoformat(),
            "discipline": s.discipline,
            "target_design_id": s.target_design_id,
            "target_design_name": s.target_design.name if s.target_design else None
        })
    db.close()
    result.sort(key=lambda x: x["date"], reverse=True)
    return result