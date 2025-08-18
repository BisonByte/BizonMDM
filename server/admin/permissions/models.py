from __future__ import annotations

import os
from sqlalchemy import Column, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DEFAULT_DB_URL = "sqlite:///permissions.db"
DB_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


class Permission(Base):
    """Permiso de acción asociado a una entidad."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("entity_type", "entity_id", "action"),)


def init_db(drop: bool = False) -> None:
    """Inicializa la base de datos de permisos."""

    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


__all__ = ["Permission", "SessionLocal", "init_db"]
