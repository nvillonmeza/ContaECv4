"""
ContaEC - Modelo de Historial Laboral
Historial Laboral: Seguimiento de cambios de cargo, salario, departamento
Conforme al Código del Trabajo ecuatoriano
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MovimientoTipo(str, enum.Enum):
    """Tipos de movimiento laboral"""
    INGRESO = "ingreso"
    ASCENSO = "ascenso"
    DESCENSO = "descenso"
    CAMBIO_DEPARTAMENTO = "cambio_departamento"
    CAMBIO_SALARIAL = "cambio_salarial"
    CAMBIO_JORNADA = "cambio_jornada"
    TRANSFERENCIA = "transferencia"
    SUSPENSION = "suspension"
    REINCORPORACION = "reincorporacion"
    CESE = "cese"


class MovimientoEstado(str, enum.Enum):
    """Estados del movimiento"""
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    CANCELADO = "cancelado"
    PROCESADO = "procesado"


class HistorialLaboral(Base):
    """
    Modelo de Historial Laboral.

    Registra todos los movimientos y cambios en la vida laboral
    del empleado dentro de la empresa: ascensos, cambios de salario,
    transfers, suspensiones, ceses, etc.

    Permite reconstruir la trayectoria completa del empleado.
    """
    __tablename__ = "historial_laboral"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    employee_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del empleado",
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="ID del usuario que registró el movimiento",
    )

    # ==========================================
    # Información del movimiento
    # ==========================================
    tipo_movimiento: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Tipo: ingreso, ascenso, descenso, cambio_departamento, cambio_salarial, etc.",
    )
    fecha_efectiva: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha efectiva del movimiento",
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de registro en el sistema",
    )

    # ==========================================
    # Datos anteriores (snapshot)
    # ==========================================
    cargo_anterior: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Cargo antes del movimiento",
    )
    departamento_anterior: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Departamento antes del movimiento",
    )
    sueldo_anterior: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment="Sueldo antes del movimiento",
    )
    jornada_anterior: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Jornada horas semanal antes del movimiento",
    )
    ubicacion_anterior: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Ubicación/lugar de trabajo anterior",
    )

    # ==========================================
    # Datos nuevos (después del movimiento)
    # ==========================================
    cargo_nuevo: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Cargo después del movimiento",
    )
    departamento_nuevo: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Departamento después del movimiento",
    )
    sueldo_nuevo: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment="Sueldo después del movimiento",
    )
    jornada_nueva: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Jornada horas semanal después del movimiento",
    )
    ubicacion_nueva: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Nueva ubicación/lugar de trabajo",
    )

    # ==========================================
    # Información del cambio salarial
    # ==========================================
    incremento_salarial: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Monto del incremento/disminución salarial",
    )
    porcentaje_incremento: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Porcentaje de incremento/disminución",
    )
    motivo_incremento: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Motivo: mérito, ajuste inflación, promoción, etc.",
    )

    # ==========================================
    # Aprobación y estado
    # ==========================================
    aprobado_por_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del usuario que aprobó el movimiento",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=MovimientoEstado.APROBADO,
        nullable=False,
        comment="Estado: pendiente, aprobado, rechazado, cancelado, procesado",
    )
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de aprobación",
    )

    # ==========================================
    # Observaciones
    # ==========================================
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones del movimiento",
    )
    comentario_aprobacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Comentario al aprobar/rechazar",
    )

    # ==========================================
    # Auditoría
    # ==========================================
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ==========================================
    # Relaciones
    # ==========================================
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="historial_laboral",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(
        "Company",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="selectin",
    )
    aprobado_por: Mapped["User"] = relationship(
        "User",
        foreign_keys=[aprobado_por_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<HistorialLaboral(id={self.id}, employee_id={self.employee_id}, "
            f"tipo={self.tipo_movimiento}, fecha={self.fecha_efectiva})>"
        )

    @property
    def es_promocion(self) -> bool:
        """Verifica si el movimiento es una promoción/ascenso"""
        return (
            self.tipo_movimiento == MovimientoTipo.ASCENSO
            or (self.incremento_salarial and self.incremento_salarial > 0)
        )

    @property
    def tiene_cambio_salarial(self) -> bool:
        """Verifica si hubo cambio salarial"""
        return (
            self.sueldo_anterior is not None
            and self.sueldo_nuevo is not None
            and self.sueldo_anterior != self.sueldo_nuevo
        )