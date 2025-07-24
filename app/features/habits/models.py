from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Habit(Base):
    __tablename__ = "habits"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    frequency   = Column(String(50), default="daily")
    active      = Column(Boolean, default=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner = relationship("User")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DATE, server_default=func.current_date(), nullable=False)

    habit = relationship("Habit", back_populates="logs")
