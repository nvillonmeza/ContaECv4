"""
ContaEC - Modelos extendidos de RRHH
Contrato: Contratos laborales separados del modelo Employee
DecimoPago: Seguimiento de pagos de décimo tercero y cuarto
Anticipo: Seguimiento de anticipos de sueldo
RubroEmpleado: Rubros dinámicos de ingresos/descuentos por empleado
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ==========================================
# Enumeraciones
# ==========================================


class ContratoEstado(str, enum.Enum):
    """Estados del contrato laboral"""
    VIGENTE = "vigente"
    TERMINADO = "terminado"
    ANULADO = "anulado"


class DecimoTipo(str, enum.Enum):
    """Tipos de décimo pago"""
    TERCERO = "tercero"
    CUARTO = "cuarto"


class DecimoEstado(str, enum.Enum):
    """Estados del décimo pago"""
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    ANULADO = "anulado"


class AnticipoEstado(str, enum.Enum):
    """Estados del anticipo de sueldo"""
    PENDIENTE = "pendiente"
    PARCIAL = "parcial"
    COMPLETADO = "completado"
    ANULADO = "anulado"


class RubroTipo(str, enum.Enum):
    """Tipos de rubro (ingreso o descuento)"""
    INGRESO = "ingreso"
    DESCUENTO = "descuento"


class RubroCategoria(str, enum.Enum):
    """Categorías de rubro"""
    HORAS_EXTRAS = "horas_extras"
    BONO = "bono"
    COMISION = "comision"
    OTRO_INGRESO = "otro_ingreso"
    IESS = "iess"
    ANTICIPO = "anticipo"
    PRESTAMO = "prestamo"
    RETENCION = "retencion"
    OTRO_DESCUENTO = "otro_descuento"


# ==========================================
# Modelos
# ==========================================


class Contrato(Base):
    """
    Modelo de Contrato Laboral.

    Almacena la información contractual del empleado, separada del
    modelo Employee para permitir historial de contratos y mayor
    flexibilidad en la gestión de vínculos laborales conforme al
    Código del Trabajo ecuatoriano.
    """
    __tablename__ = "contratos"

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
        comment="ID del empleado al que pertenece el contrato",
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa a la que pertenece el contrato",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="ID del usuario que creó el registro",
    )

    # ==========================================
    # Información contractual
    # ==========================================
    tipo_contrato: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Tipo de contrato: indefinido, fijo, por_obra, temporal, pasantia",
    )
    cargo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Cargo o puesto del empleado en el contrato",
    )
    departamento: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Departamento o área del empleado",
    )
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de inicio del contrato",
    )
    fecha_fin: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de fin del contrato (null para indefinido)",
    )

    # ==========================================
    # Información salarial y jornada
    # ==========================================
    sueldo_mensual: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Sueldo mensual pactado en el contrato",
    )
    horas_trabajo_semanal: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("40.00"),
        nullable=False,
        comment="Horas de trabajo semanal (por defecto 40)",
    )
    jornada_parcial: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si el contrato es de jornada parcial",
    )
    porcentaje_jornada: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("100.00"),
        nullable=False,
        comment="Porcentaje de jornada laboral respecto a la completa",
    )

    # ==========================================
    # Beneficios sociales
    # ==========================================
    tiene_fondo_reserva: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si el contrato incluye fondo de reserva",
    )
    tiene_decimo_tercero: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el contrato incluye décimo tercero",
    )
    tiene_decimo_cuarto: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el contrato incluye décimo cuarto",
    )
    tiene_vacaciones: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el contrato incluye vacaciones",
    )

    # ==========================================
    # Estado y auditoría
    # ==========================================
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales del contrato",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=ContratoEstado.VIGENTE,
        nullable=False,
        comment="Estado del contrato: vigente, terminado, anulado",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el contrato está activo en el sistema",
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
    employee: Mapped["Employee"] = relationship(  # noqa: F821
        "Employee",
        back_populates="contratos",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="contratos",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Contrato(id={self.id}, employee_id={self.employee_id}, "
            f"tipo_contrato={self.tipo_contrato}, estado={self.estado})>"
        )


class DecimoPago(Base):
    """
    Modelo de Décimo Pago.

    Realiza el seguimiento de los pagos de décimo tercero y cuarto
    conforme a la legislación ecuatoriana (Arts. 95 y 97 del Código
    del Trabajo). El décimo tercero equivale a una remuneración mensual
    y el décimo cuarto al salario básico unificado, ambos pagaderos
    hasta el 24 de diciembre y 15 de abril respectivamente.
    """
    __tablename__ = "decimos_pagos"

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
        comment="ID del empleado al que pertenece el décimo pago",
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa a la que pertenece el décimo pago",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="ID del usuario que creó el registro",
    )

    # ==========================================
    # Información del décimo
    # ==========================================
    tipo: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        comment="Tipo de décimo: tercero o cuarto",
    )
    anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Año al que corresponde el décimo pago",
    )
    periodo_desde: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de inicio del período de cálculo",
    )
    periodo_hasta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de fin del período de cálculo",
    )

    # ==========================================
    # Valores
    # ==========================================
    meses_trabajados: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Meses trabajados en el período para el cálculo",
    )
    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Valor total del décimo calculado",
    )
    valor_pagado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Valor ya pagado del décimo",
    )

    # ==========================================
    # Pago
    # ==========================================
    fecha_pago: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que se realizó el pago",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=DecimoEstado.PENDIENTE,
        nullable=False,
        comment="Estado del décimo: pendiente, pagado, anulado",
    )
    rol_pago_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("roles_pago.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del rol de pago en el que se incluyó el décimo",
    )

    # ==========================================
    # Estado y auditoría
    # ==========================================
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales del décimo pago",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el décimo pago está activo en el sistema",
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
    employee: Mapped["Employee"] = relationship(  # noqa: F821
        "Employee",
        back_populates="decimos_pagos",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<DecimoPago(id={self.id}, employee_id={self.employee_id}, "
            f"tipo={self.tipo}, anio={self.anio}, estado={self.estado})>"
        )


class Anticipo(Base):
    """
    Modelo de Anticipo de Sueldo.

    Realiza el seguimiento de los anticipos de sueldo solicitados
    por los empleados, incluyendo el control de descuento por cuotas
    conforme a las políticas internas de la empresa y el Código del
    Trabajo ecuatoriano.
    """
    __tablename__ = "anticipos"

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
        comment="ID del empleado que solicita el anticipo",
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa a la que pertenece el anticipo",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="ID del usuario que creó el registro",
    )

    # ==========================================
    # Información del anticipo
    # ==========================================
    monto: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto total del anticipo solicitado",
    )
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha en que se solicita el anticipo",
    )
    fecha_pago: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que se realizó el pago del anticipo",
    )
    motivo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo de la solicitud del anticipo",
    )

    # ==========================================
    # Control de cuotas
    # ==========================================
    cuotas: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Número total de cuotas en que se descuenta el anticipo",
    )
    cuota_actual: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de cuota actual que se va descontando",
    )
    monto_cuota: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto de cada cuota a descontar",
    )
    monto_descontado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Monto total que ya ha sido descontado del anticipo",
    )

    # ==========================================
    # Estado y auditoría
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(20),
        default=AnticipoEstado.PENDIENTE,
        nullable=False,
        comment="Estado del anticipo: pendiente, parcial, completado, anulado",
    )
    rol_detalle_ids: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Lista JSON de IDs de RolPagoDetalle donde se aplicaron descuentos",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales del anticipo",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el anticipo está activo en el sistema",
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
    employee: Mapped["Employee"] = relationship(  # noqa: F821
        "Employee",
        back_populates="anticipos",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Anticipo(id={self.id}, employee_id={self.employee_id}, "
            f"monto={self.monto}, estado={self.estado})>"
        )


class RubroEmpleado(Base):
    """
    Modelo de Rubro por Empleado.

    Permite definir rubros dinámicos de ingresos y descuentos por empleado,
    reemplazando las columnas fijas en RolPagoDetalle. Cada rubro puede ser
    fijo (valor_fijo) o porcentual (porcentaje del sueldo base), recurrente
    o puntual, y configurable como imponible o no para efectos del IESS.
    """
    __tablename__ = "rubros_empleado"

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
        comment="ID del empleado al que pertenece el rubro",
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa a la que pertenece el rubro",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="ID del usuario que creó el registro",
    )

    # ==========================================
    # Información del rubro
    # ==========================================
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del rubro (ej: Horas Extras Diurnas, Bono Producción)",
    )
    tipo: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        comment="Tipo de rubro: ingreso o descuento",
    )
    categoria: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Categoría del rubro: horas_extras, bono, comision, otro_ingreso, iess, anticipo, prestamo, retencion, otro_descuento",
    )

    # ==========================================
    # Valor del rubro
    # ==========================================
    valor_fijo: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment="Valor fijo mensual del rubro (null si es porcentual)",
    )
    porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje del sueldo base (null si es valor fijo)",
    )

    # ==========================================
    # Configuración del rubro
    # ==========================================
    es_recurrente: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si es True, el rubro aplica cada mes automáticamente",
    )
    es_imponible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si es True, el rubro está sujeto a aportes al IESS",
    )

    # ==========================================
    # Vigencia del rubro
    # ==========================================
    fecha_inicio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que el rubro comienza a aplicar",
    )
    fecha_fin: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que el rubro deja de aplicar",
    )

    # ==========================================
    # Estado y auditoría
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(15),
        default="activo",
        nullable=False,
        comment="Estado del rubro: activo, inactivo",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales del rubro",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el rubro está activo en el sistema",
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
    employee: Mapped["Employee"] = relationship(  # noqa: F821
        "Employee",
        back_populates="rubros",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<RubroEmpleado(id={self.id}, employee_id={self.employee_id}, "
            f"nombre={self.nombre}, tipo={self.tipo}, categoria={self.categoria})>"
        )
