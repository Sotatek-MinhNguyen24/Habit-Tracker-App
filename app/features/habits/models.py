import enum
from sqlalchemy import Column,Integer,String,Text,Boolean,ForeignKey,DateTime,UniqueConstraint,Date,Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class HabitFrequency(enum.Enum):
    daily = "daily"
    monthly = "monthly"
    yearly = "yearly"


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    frequency = Column(SQLEnum(HabitFrequency, name="habit_frequency"),nullable=False,server_default=HabitFrequency.daily.value,)
    active = Column(Boolean, nullable=False, server_default="true")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False,)
    current_streak = Column(Integer, nullable=False, default=0)
    last_completed_date = Column(Date, nullable=True)

    owner = relationship("User")
    logs = relationship("HabitLog",back_populates="habit",cascade="all, delete-orphan",passive_deletes=True)


class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "timestamp", name="uq_habit_log"),)

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer,ForeignKey("habits.id", ondelete="CASCADE"),nullable=False,)
    timestamp = Column(Date,server_default=func.current_date(),nullable=False,)

    habit = relationship("Habit", back_populates="logs")
