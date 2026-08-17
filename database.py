from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./shooters.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Shooter(Base):
    __tablename__ = "shooters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    join_date = Column(Date, nullable=False)

    sessions = relationship("PracticeSession", back_populates="shooter")


class PracticeSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    shooter_id = Column(Integer, ForeignKey("shooters.id"), nullable=False)
    target_design_id = Column(Integer, ForeignKey("target_designs.id"), nullable=True)
    date = Column(Date, nullable=False)
    discipline = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    shooter = relationship("Shooter", back_populates="sessions")
    scores = relationship("Score", back_populates="session")
    target_design = relationship("TargetDesign")

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    target_number = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    max_possible_score = Column(Float, nullable=False)

    session = relationship("PracticeSession", back_populates="scores")


class TargetDesign(Base):
    __tablename__ = "target_designs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    diameter_cm = Column(Float, nullable=False)
    num_rings = Column(Integer, nullable=False)
def init_db():
    Base.metadata.create_all(bind=engine)