from sqlalchemy import (create_engine, Column, Integer, String, Text,
                        ForeignKey)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os
from pathlib import Path

# Database file placed next to the repository root by default. You can override
# with the DATABASE_URL environment variable.
DB_PATH = Path(os.environ.get("DATABASE_FILE", Path(__file__).parent.parent / "data.db"))
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    schedule = Column(String(255), nullable=True)
    max_participants = Column(Integer, nullable=True)

    participants = relationship("Participant", back_populates="activity", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    email = Column(String(255), nullable=False)

    activity = relationship("Activity", back_populates="participants")


def create_tables():
    Base.metadata.create_all(bind=engine)
