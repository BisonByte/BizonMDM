from __future__ import annotations

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func

DB_PATH = os.getenv("BIZON_DB", "bizon.db")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    device_id = Column(String, unique=True, nullable=False)
    info = Column(Text)
    status = Column(Text)
    added = Column(DateTime(timezone=True), server_default=func.now())

    logs = relationship("LogEntry", back_populates="device", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="device", cascade="all, delete-orphan")

class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    log = Column(Text)

    device = relationship("Device", back_populates="logs")

class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    command = Column(Text)

    device = relationship("Device", back_populates="commands")

def init_db() -> None:
    Base.metadata.create_all(engine)
