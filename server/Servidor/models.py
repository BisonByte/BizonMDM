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
    client_id = Column(Integer, ForeignKey("clients.id"))

    logs = relationship("LogEntry", back_populates="device", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="device", cascade="all, delete-orphan")
    client = relationship("Client", back_populates="devices")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    permissions = Column(Text)

    devices = relationship("Device", back_populates="client")


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


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())


def init_db() -> None:
    try:
        from alembic import command
        from alembic.config import Config

        base_dir = os.path.dirname(__file__)
        cfg = Config(os.path.join(base_dir, "alembic.ini"))
        cfg.set_main_option("sqlalchemy.url", DB_URL)
        cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
        command.upgrade(cfg, "head")
        Base.metadata.create_all(engine)
    except Exception:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
