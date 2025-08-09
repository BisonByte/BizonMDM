from __future__ import annotations

import os
import bcrypt
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

DEFAULT_DB_URL = "postgresql+psycopg2://postgres:postgres@localhost/bizon"
DB_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


client_devices = Table(
    "client_devices",
    Base.metadata,
    Column("client_id", ForeignKey("clients.id"), primary_key=True),
    Column("device_id", ForeignKey("devices.id"), primary_key=True),
)

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
    clients = relationship("Client", secondary=client_devices, back_populates="devices")


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
    password_hash = Column(String, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permissions = Column(Text, default="[]")

    user = relationship("User", back_populates="clients")
    devices = relationship("Device", secondary=client_devices, back_populates="clients")


def init_db(drop: bool = False) -> None:
    """Inicializa la base de datos.

    Por defecto solo aplica migraciones y crea las tablas si no existen. Si
    ``drop`` es ``True`` o la variable de entorno ``TESTING`` está establecida
    a un valor verdadero, se eliminan primero todas las tablas existentes.
    """

    should_drop = drop or os.getenv("TESTING", "").lower() in {"1", "true", "yes"}

    try:
        from alembic import command
        from alembic.config import Config

        base_dir = os.path.dirname(__file__)
        cfg = Config(os.path.join(base_dir, "alembic.ini"))
        cfg.set_main_option("sqlalchemy.url", DB_URL)
        cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
        if should_drop:
            Base.metadata.drop_all(engine)
        command.upgrade(cfg, "head")
        Base.metadata.create_all(engine)
    except (ModuleNotFoundError, ImportError, Exception):
        # Alembic no disponible o fallo en migraciones: crea las tablas directamente
        if should_drop:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
