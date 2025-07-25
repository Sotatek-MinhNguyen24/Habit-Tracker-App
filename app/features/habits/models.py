
from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Habit(Base):
    __tablename__ = "habits"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(200), nullable=False)
    description         = Column(Text, nullable=True)
    frequency           = Column(String(50), default="daily")
    active              = Column(Boolean, default=True)
    owner_id            = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    current_streak      = Column(Integer, default=0, nullable=False)
    last_completed_date = Column(DATE, nullable=True)

    owner = relationship("User")
    logs  = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")


class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "timestamp", name="uq_habit_log_per_day"),)

    id        = Column(Integer, primary_key=True, index=True)
    habit_id  = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DATE, server_default=func.current_date(), nullable=False)

    habit = relationship("Habit", back_populates="logs")
