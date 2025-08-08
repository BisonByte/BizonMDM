from __future__ import annotations

import os
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

DEFAULT_DB_URL = "postgresql+psycopg2://postgres:postgres@localhost/bizon"
DB_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    device_id = Column(String, unique=True, nullable=False)
    imei = Column(String)
    model = Column(String)
    serial = Column(String)
    info = Column(Text)
    status = Column(Text)
    fcm_token = Column(String)
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
    try:
        from alembic import command
        from alembic.config import Config

        base_dir = os.path.dirname(__file__)
        cfg = Config(os.path.join(base_dir, "alembic.ini"))
        cfg.set_main_option("sqlalchemy.url", DB_URL)
        cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
        command.upgrade(cfg, "head")
    except (ModuleNotFoundError, ImportError):
        # Alembic no disponible: crea las tablas directamente
        Base.metadata.create_all(engine)
