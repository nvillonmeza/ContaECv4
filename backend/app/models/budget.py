"""
ContaEC - Modelos de Presupuestos y Control Presupuestario
PresupuestoAnual: Presupuesto anual de la empresa
PresupuestoCuenta: Presupuesto por cuenta contable
PresupuestoEjecucionMensual: Ejecución presupuestaria mensual por cuenta
PresupuestoAlerta: Alertas de sobregiro y control presupuestario
"""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PresupuestoEstado(str, Enum):
    """Estado del presupuesto anual"""
    BORRADOR = "borrador"
    APROBADO = "aprobado"
    CERRADO = "cerrado"
    ANULADO = "anulado"


class TipoCuenta(str, Enum):
    """Tipo de cuenta presupuestaria"""
    INGRESO = "ingreso"
    EGRESO = "egreso"


class TipoAlertaPresupuesto(str, Enum):
    """Tipos de alerta presupuestaria"""
    SOBREGIRO = "sobregiro"
    NOVENTA_PORCIENTO = "90_porciento"
    SETENTA_CINCO_PORCIENTO = "75_porciento"
    CINCUENTA_PORCIENTO = "50_porciento"


class PresupuestoAnual(Base):
    """
    Modelo de Presupuesto Anual.

    Registra el presupuesto anual de la empresa con totales
    presupuestados y ejecutados para ingresos y egresos.
    """
    __tablename__ = "presupuestos_anuales"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
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
        index=True,
        comment="ID del usuario que creó el presupuesto",
    )
    anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Año fiscal del presupuesto (ej: 2024)",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre descriptivo del presupuesto",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción detallada del presupuesto",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=PresupuestoEstado.BORRADOR.value,
        nullable=False,
        index=True,
        comment="Estado: borrador, aprobado, cerrado, anulado",
    )
    total_ingresos_presupuestado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de ingresos presupuestados",
    )
    total_egresos_presupuestado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de egresos presupuestados",
    )
    total_ingresos_ejecutado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de ingresos ejecutados",
    )
    total_egresos_ejecutado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de egresos ejecutados",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el presupuesto está activo",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación del registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de última actualización",
    )

    # Relaciones
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="presupuestos",
        lazy="selectin",
    )
    cuentas: Mapped[list["PresupuestoCuenta"]] = relationship(
        "PresupuestoCuenta",
        back_populates="presupuesto",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<PresupuestoAnual(id={self.id}, anio={self.anio}, "
            f"nombre={self.nombre}, estado={self.estado})>"
        )


class PresupuestoCuenta(Base):
    """
    Modelo de Presupuesto por Cuenta Contable.

    Cada cuenta del plan contable con su monto anual presupuestado,
    monto ejecutado y monto disponible.
    """
    __tablename__ = "presupuestos_cuentas"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    presupuesto_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("presupuestos_anuales.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del presupuesto anual",
    )
    cuenta_codigo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Código de cuenta contable (ej: 1.1.1.01, 5.1.1.01)",
    )
    cuenta_nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre de la cuenta contable (ej: Caja, Servicios Básicos)",
    )
    cuenta_tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Tipo de cuenta: ingreso o egreso",
    )
    monto_anual: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto anual presupuestado para la cuenta",
    )
    monto_ejecutado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto ejecutado acumulado",
    )
    monto_disponible: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto disponible (monto_anual - monto_ejecutado)",
    )
    porcentaje_ejecucion: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Porcentaje de ejecución (monto_ejecutado / monto_anual * 100)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la cuenta está activa",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación del registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de última actualización",
    )

    # Relaciones
    presupuesto: Mapped["PresupuestoAnual"] = relationship(
        "PresupuestoAnual",
        back_populates="cuentas",
        lazy="selectin",
    )
    ejecuciones_mensuales: Mapped[list["PresupuestoEjecucionMensual"]] = relationship(
        "PresupuestoEjecucionMensual",
        back_populates="cuenta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    alertas: Mapped[list["PresupuestoAlerta"]] = relationship(
        "PresupuestoAlerta",
        back_populates="cuenta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<PresupuestoCuenta(id={self.id}, cuenta_codigo={self.cuenta_codigo}, "
            f"cuenta_nombre={self.cuenta_nombre}, monto_anual={self.monto_anual})>"
        )


class PresupuestoEjecucionMensual(Base):
    """
    Modelo de Ejecución Presupuestaria Mensual por Cuenta.

    Registra la ejecución mensual de cada cuenta presupuestaria,
    permitiendo comparar lo presupuestado vs lo ejecutado por mes.
    """
    __tablename__ = "presupuestos_ejecucion_mensual"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    presupuesto_cuenta_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("presupuestos_cuentas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la cuenta presupuestaria",
    )
    mes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Mes (1-12)",
    )
    monto_presupuestado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto presupuestado para el mes",
    )
    monto_ejecutado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto ejecutado en el mes",
    )
    monto_disponible: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto disponible en el mes (presupuestado - ejecutado)",
    )
    porcentaje_ejecucion: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Porcentaje de ejecución mensual",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones sobre la ejecución mensual",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación del registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de última actualización",
    )

    # Relaciones
    cuenta: Mapped["PresupuestoCuenta"] = relationship(
        "PresupuestoCuenta",
        back_populates="ejecuciones_mensuales",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<PresupuestoEjecucionMensual(id={self.id}, mes={self.mes}, "
            f"monto_presupuestado={self.monto_presupuestado}, "
            f"monto_ejecutado={self.monto_ejecutado})>"
        )


class PresupuestoAlerta(Base):
    """
    Modelo de Alertas de Sobregiro y Control Presupuestario.

    Genera alertas automáticas cuando la ejecución presupuestaria
    alcanza ciertos umbrales (50%, 75%, 90%) o cuando hay sobregiro.
    """
    __tablename__ = "presupuestos_alertas"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa",
    )
    presupuesto_cuenta_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("presupuestos_cuentas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la cuenta presupuestaria",
    )
    tipo_alerta: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Tipo de alerta: sobregiro, 90_porciento, 75_porciento, 50_porciento",
    )
    mensaje: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Mensaje descriptivo de la alerta",
    )
    monto_presupuestado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto presupuestado al momento de la alerta",
    )
    monto_ejecutado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto ejecutado al momento de la alerta",
    )
    monto_sobregiro: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto de sobregiro (0 si no hay sobregiro)",
    )
    porcentaje_ejecucion: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Porcentaje de ejecución al momento de la alerta",
    )
    is_leida: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si la alerta ha sido leída",
    )
    is_resuelta: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si la alerta ha sido resuelta",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación de la alerta",
    )

    # Relaciones
    cuenta: Mapped["PresupuestoCuenta"] = relationship(
        "PresupuestoCuenta",
        back_populates="alertas",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<PresupuestoAlerta(id={self.id}, tipo_alerta={self.tipo_alerta}, "
            f"porcentaje_ejecucion={self.porcentaje_ejecucion})>"
        )
