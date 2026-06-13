"""
ContaEC - Modelos de Nómina (Rol de Pago)
RolPago: Cabecera del rol de pago mensual
RolPagoDetalle: Detalle por empleado con ingresos, descuentos y aportes
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EstadoRol(str, enum.Enum):
    """Estados del rol de pago"""
    BORRADOR = "borrador"
    APROBADO = "aprobado"
    PAGADO = "pagado"
    ANULADO = "anulado"


class RolPago(Base):
    """
    Modelo de Rol de Pago (cabecera).

    Representa el rol de pago mensual de una empresa que agrupa
    los detalles de remuneración de todos los empleados activos
    para un período específico (mes/año).
    """
    __tablename__ = "roles_pago"

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
        comment="ID de la empresa a la que pertenece el rol",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario que creó el rol",
    )

    # Período
    periodo_mes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Mes del período (1-12)",
    )
    periodo_anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Año del período (ej: 2024)",
    )
    fecha_pago: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de pago del rol",
    )

    # Estado
    estado: Mapped[str] = mapped_column(
        String(20),
        default=EstadoRol.BORRADOR,
        nullable=False,
        comment="Estado del rol: borrador, aprobado, pagado, anulado",
    )

    # Totales
    total_remuneraciones: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Total de remuneraciones (ingresos) del rol",
    )
    total_descuentos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Total de descuentos del empleado del rol",
    )
    total_empleador: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Total de aportes del empleador del rol",
    )
    total_liquido: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Total líquido a pagar del rol",
    )

    # Observaciones
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones generales del rol de pago",
    )

    # Estado y auditoría
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el rol está activo en el sistema",
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

    # ==========================================
    # Relaciones
    # ==========================================
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="roles_pago",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )
    detalles: Mapped[list["RolPagoDetalle"]] = relationship(
        "RolPagoDetalle",
        back_populates="rol_pago",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<RolPago(id={self.id}, periodo={self.periodo_mes}/{self.periodo_anio}, "
            f"estado={self.estado})>"
        )


class RolPagoDetalle(Base):
    """
    Modelo de Detalle del Rol de Pago por empleado.

    Contiene todos los ingresos, descuentos, aportes del empleador,
    décimos, vacaciones y fondo de reserva calculados para un empleado
    en un período específico conforme a la legislación ecuatoriana.
    """
    __tablename__ = "roles_pago_detalles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    rol_pago_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("roles_pago.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del rol de pago al que pertenece el detalle",
    )
    employee_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del empleado",
    )

    # ==========================================
    # Ingresos
    # ==========================================
    sueldo_base: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Sueldo base del empleado para el período",
    )
    horas_extras_diurnas: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Horas extras diurnas trabajadas",
    )
    valor_horas_extras_diurnas: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Valor monetario de horas extras diurnas",
    )
    horas_extras_nocturnas: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Horas extras nocturnas trabajadas",
    )
    valor_horas_extras_nocturnas: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Valor monetario de horas extras nocturnas",
    )
    horas_extras_dominicales: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Horas extras dominicales/festivas trabajadas",
    )
    valor_horas_extras_dominicales: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Valor monetario de horas extras dominicales",
    )
    comisiones: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Comisiones obtenidas",
    )
    bonos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Bonos adicionales",
    )
    otros_ingresos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Otros ingresos gravados",
    )
    total_ingresos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Total de ingresos del empleado",
    )

    # ==========================================
    # Descuentos empleado
    # ==========================================
    iess_personal_945: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Aporte personal al IESS (9.45%)",
    )
    anticipo: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Anticipo de sueldo descontado",
    )
    prestamo_empresa: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Préstamo de la empresa descontado",
    )
    retencion_judicial: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Retención judicial descontada",
    )
    otros_descuentos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Otros descuentos aplicados",
    )
    total_descuentos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Total de descuentos del empleado",
    )

    # ==========================================
    # Aportes empleador
    # ==========================================
    iess_patronal_1115: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Aporte patronal al IESS (11.15%)",
    )
    iee_0005: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Aporte al IESS Seguro de Riesgos del Trabajo (0.5%)",
    )
    secap_002: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Aporte al SECAP (0.2%)",
    )
    cenaces_001: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Aporte al CENACES (0.1%)",
    )
    total_aportes_empleador: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Total de aportes del empleador",
    )

    # ==========================================
    # Décimos
    # ==========================================
    decimo_tercero: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Provisión décimo tercero (1/12 del sueldo mensual)",
    )
    decimo_cuarto: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Provisión décimo cuarto (1/12 del salario básico unificado)",
    )

    # ==========================================
    # Vacaciones
    # ==========================================
    vacaciones_provision: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Provisión de vacaciones",
    )

    # ==========================================
    # Fondos de reserva
    # ==========================================
    fondos_reserva: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Provisión de fondos de reserva",
    )

    # ==========================================
    # Total líquido
    # ==========================================
    liquido_recibir: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Total líquido a recibir por el empleado",
    )

    # ==========================================
    # Auditoría
    # ==========================================
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

    # ==========================================
    # Relaciones
    # ==========================================
    rol_pago: Mapped["RolPago"] = relationship(
        "RolPago",
        back_populates="detalles",
        lazy="selectin",
    )
    employee: Mapped["Employee"] = relationship(  # noqa: F821
        "Employee",
        back_populates="rol_detalles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<RolPagoDetalle(id={self.id}, employee_id={self.employee_id}, "
            f"liquido_recibir={self.liquido_recibir})>"
        )
