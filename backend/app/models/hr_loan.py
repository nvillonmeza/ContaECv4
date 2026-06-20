"""
ContaEC - Modelo de Préstamos Laborales
Préstamo: Préstamos y anticipos a empleados con control de cuotas
Conforme al Código del Trabajo ecuatoriano
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PrestamoEstado(str, enum.Enum):
    """Estados del préstamo"""
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    EN_CURSO = "en_curso"
    COMPLETADO = "completado"
    MORA = "mora"
    CANCELADO = "cancelado"


class PrestamoTipo(str, enum.Enum):
    """Tipos de préstamo"""
    ANTICIPO_SUELDO = "anticipo_sueldo"
    PRESTAMO_PERSONAL = "prestamo_personal"
    PRESTAMO_VIVIENDA = "prestamo_vivienda"
    PRESTAMO_EDUCACION = "prestamo_educacion"
    PRESTAMO_MEDICO = "prestamo_medico"
    OTRO = "otro"


class PrestamoEmpleado(Base):
    """
    Modelo de Préstamo a Empleado.

    Registra préstamos o anticipos otorgados por la empresa al empleado,
    con plan de pago en cuotas y descuento por nómina.

    El Código del Trabajo ecuatoriano limita los descuentos por préstamo
    al 30% del sueldo líquido del empleado.
    """
    __tablename__ = "prestamos_empleados"

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
        comment="ID del usuario que aprobó el préstamo",
    )

    # ==========================================
    # Información del préstamo
    # ==========================================
    tipo_prestamo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Tipo: anticipo_sueldo, prestamo_personal, vivienda, educacion, medico, otro",
    )
    monto_solicitado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto total solicitado del préstamo",
    )
    monto_aprobado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment="Monto aprobado (puede diferir del solicitado)",
    )
    tasa_interes_anual: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Tasa de interés anual (%)",
    )
    plazo_meses: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Plazo en meses para pagar",
    )

    # ==========================================
    # Cuotas y pagos
    # ==========================================
    numero_cuotas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Número total de cuotas",
    )
    cuotas_pagadas: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de cuotas pagadas",
    )
    monto_cuota: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto de cada cuota mensual",
    )
    monto_descontado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Monto total ya descontado",
    )
    saldo_pendiente: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Saldo pendiente por pagar",
    )
    descuento_porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("10.00"),
        nullable=False,
        comment="Porcentaje de descuento mensual sobre sueldo",
    )

    # ==========================================
    # Fechas
    # ==========================================
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de solicitud del préstamo",
    )
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de aprobación",
    )
    fecha_primer_descuento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha del primer descuento",
    )
    fecha_ultimo_descuento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha del último descuento",
    )

    # ==========================================
    # Estado
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(20),
        default=PrestamoEstado.PENDIENTE,
        nullable=False,
        index=True,
        comment="Estado: pendiente, aprobado, en_curso, completado, mora, cancelado",
    )
    tiene_interes: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Si el préstamo genera interés",
    )
    motivo_cancelacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo de cancelación/rechazo",
    )

    # ==========================================
    # Observaciones y auditoría
    # ==========================================
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones del préstamo",
    )
    garantia: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Garantía ofrecida (si aplica)",
    )
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
        back_populates="prestamos",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(
        "Company",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )
    detalles: Mapped[list["PrestamoDetalle"]] = relationship(
        "PrestamoDetalle",
        back_populates="prestamo",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<PrestamoEmpleado(id={self.id}, employee_id={self.employee_id}, "
            f"monto={self.monto_solicitado}, estado={self.estado})>"
        )

    @property
    def porcentaje_pagado(self) -> Decimal:
        """Porcentaje del préstamo ya pagado"""
        if self.monto_solicitado == 0:
            return Decimal("0.00")
        return ((self.monto_descontado / self.monto_solicitado) * 100).quantize(
            Decimal("0.01")
        )

    @property
    def cuotas_pendientes(self) -> int:
        """Número de cuotas pendientes"""
        return self.numero_cuotas - self.cuotas_pagadas


class PrestamoDetalle(Base):
    """
    Modelo de Detalle de Cuota de Préstamo.

    Registro individual de cada cuota del préstamo, con fechas
    programadas y estado de pago.
    """
    __tablename__ = "prestamos_detalles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    prestamo_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("prestamos_empleados.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del préstamo",
    )
    rol_pago_detalle_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("roles_pago_detalles.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del detalle de rol donde se aplicó el descuento",
    )

    # ==========================================
    # Información de cuota
    # ==========================================
    numero_cuota: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Número de cuota (1, 2, 3, ...)",
    )
    monto_cuota: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto de la cuota",
    )
    monto_interes: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Monto de interés de la cuota",
    )
    monto_capital: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto de capital de la cuota",
    )

    # ==========================================
    # Fechas
    # ==========================================
    fecha_programada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha programada para el descuento",
    )
    fecha_pago: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha real del pago",
    )

    # ==========================================
    # Estado
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        comment="Estado: pendiente, pagado, atrasado, anulado",
    )
    observaciones: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Observaciones de la cuota",
    )

    # ==========================================
    # Auditoría
    # ==========================================
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
    prestamo: Mapped["PrestamoEmpleado"] = relationship(
        "PrestamoEmpleado",
        back_populates="detalles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<PrestamoDetalle(id={self.id}, prestamo_id={self.prestamo_id}, "
            f"cuota={self.numero_cuota}, estado={self.estado})>"
        )