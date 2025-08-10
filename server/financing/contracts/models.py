from __future__ import annotations

import os
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DEFAULT_DB_URL = "sqlite:///financing.db"
DB_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


class Contract(Base):
    """Modelo de contrato de financiamiento."""

    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    term = Column(Integer, nullable=False)  # número de cuotas

    schedules = relationship(
        "PaymentSchedule", back_populates="contract", cascade="all, delete-orphan"
    )


class PaymentSchedule(Base):
    """Cronograma de pagos asociado a un contrato."""

    __tablename__ = "payment_schedules"

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    paid = Column(Boolean, default=False)

    contract = relationship("Contract", back_populates="schedules")


def init_db(drop: bool = False) -> None:
    """Inicializa la base de datos del módulo de financiamiento."""

    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
