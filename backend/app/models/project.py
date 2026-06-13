"""
ContaEC - Modelos de Proyectos y Servicios
Proyecto: Gestión de proyectos con seguimiento de rentabilidad
ProyectoTarea: Tareas dentro de un proyecto con asignación y seguimiento
ProyectoRecurso: Recursos asignados a proyectos (humanos, materiales, equipos)
ProyectoTimesheet: Registro de horas trabajadas en proyectos
ProyectoCosto: Costos adicionales asociados a proyectos
"""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProyectoEstado(str, Enum):
    """Estado del proyecto"""
    PLANIFICACION = "planificacion"
    EN_PROGRESO = "en_progreso"
    EN_PAUSA = "en_pausa"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class TareaEstado(str, Enum):
    """Estado de la tarea del proyecto"""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class TareaPrioridad(str, Enum):
    """Prioridad de la tarea del proyecto"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class TipoRecurso(str, Enum):
    """Tipo de recurso del proyecto"""
    HUMANO = "humano"
    MATERIAL = "material"
    EQUIPO = "equipo"


class Proyecto(Base):
    """
    Modelo de Proyecto.

    Gestiona proyectos con seguimiento de presupuesto, costos reales,
    ingresos y rentabilidad. Permite controlar el progreso y estado
    de cada proyecto de la empresa.
    """
    __tablename__ = "proyectos"

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
        comment="ID del usuario que creó el proyecto",
    )
    codigo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código del proyecto (ej: PRY-001)",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del proyecto",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción detallada del proyecto",
    )
    cliente_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del cliente asociado al proyecto",
    )
    cliente_nombre: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nombre del cliente (denormalizado)",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=ProyectoEstado.PLANIFICACION.value,
        nullable=False,
        index=True,
        comment="Estado: planificacion, en_progreso, en_pausa, completado, cancelado",
    )
    fecha_inicio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de inicio del proyecto",
    )
    fecha_fin_estimada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de fin estimada del proyecto",
    )
    fecha_fin_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de fin real del proyecto",
    )
    presupuesto: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto presupuestado del proyecto",
    )
    costo_real: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Costo real acumulado del proyecto",
    )
    ingreso: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Ingreso total del proyecto",
    )
    margen: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Margen del proyecto (ingreso - costo_real)",
    )
    margen_porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Porcentaje de margen del proyecto",
    )
    progreso: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Porcentaje de progreso del proyecto",
    )
    responsable: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nombre del responsable / gerente del proyecto",
    )
    notas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionales del proyecto",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el proyecto está activo",
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
        back_populates="proyectos",
        lazy="selectin",
    )
    tareas: Mapped[list["ProyectoTarea"]] = relationship(
        "ProyectoTarea",
        back_populates="proyecto",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    recursos: Mapped[list["ProyectoRecurso"]] = relationship(
        "ProyectoRecurso",
        back_populates="proyecto",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    timesheets: Mapped[list["ProyectoTimesheet"]] = relationship(
        "ProyectoTimesheet",
        back_populates="proyecto",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    costos: Mapped[list["ProyectoCosto"]] = relationship(
        "ProyectoCosto",
        back_populates="proyecto",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Proyecto(id={self.id}, codigo={self.codigo}, "
            f"nombre={self.nombre}, estado={self.estado})>"
        )


class ProyectoTarea(Base):
    """
    Modelo de Tarea de Proyecto.

    Cada tarea dentro de un proyecto con asignación de responsable,
    seguimiento de horas estimadas vs reales y progreso individual.
    """
    __tablename__ = "proyecto_tareas"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    proyecto_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("proyectos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del proyecto al que pertenece la tarea",
    )
    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Título de la tarea",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción detallada de la tarea",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=TareaEstado.PENDIENTE.value,
        nullable=False,
        index=True,
        comment="Estado: pendiente, en_progreso, completada, cancelada",
    )
    prioridad: Mapped[str] = mapped_column(
        String(20),
        default=TareaPrioridad.MEDIA.value,
        nullable=False,
        comment="Prioridad: baja, media, alta, critica",
    )
    fase: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Nombre de la fase del proyecto",
    )
    asignado_a: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nombre de la persona asignada",
    )
    employee_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del empleado asignado",
    )
    fecha_inicio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de inicio de la tarea",
    )
    fecha_fin_estimada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de fin estimada de la tarea",
    )
    fecha_fin_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de fin real de la tarea",
    )
    horas_estimadas: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Horas estimadas para completar la tarea",
    )
    horas_reales: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Horas reales trabajadas en la tarea",
    )
    progreso: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Porcentaje de progreso de la tarea",
    )
    orden: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Orden de la tarea dentro del proyecto",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la tarea está activa",
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
    proyecto: Mapped["Proyecto"] = relationship(
        "Proyecto",
        back_populates="tareas",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ProyectoTarea(id={self.id}, titulo={self.titulo}, "
            f"estado={self.estado}, prioridad={self.prioridad})>"
        )


class ProyectoRecurso(Base):
    """
    Modelo de Recurso de Proyecto.

    Recursos asignados a un proyecto, pueden ser humanos (empleados),
    materiales o equipos. Cada recurso tiene costo unitario y cantidad.
    """
    __tablename__ = "proyecto_recursos"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    proyecto_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("proyectos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del proyecto al que pertenece el recurso",
    )
    tipo_recurso: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Tipo de recurso: humano, material, equipo",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del recurso",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción del recurso",
    )
    employee_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del empleado (si el recurso es humano)",
    )
    costo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Costo unitario del recurso",
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("1"),
        nullable=False,
        comment="Cantidad del recurso asignado",
    )
    costo_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Costo total del recurso (costo_unitario * cantidad)",
    )
    fecha_asignacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de asignación del recurso al proyecto",
    )
    fecha_liberacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de liberación del recurso del proyecto",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el recurso está activo",
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
    proyecto: Mapped["Proyecto"] = relationship(
        "Proyecto",
        back_populates="recursos",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ProyectoRecurso(id={self.id}, nombre={self.nombre}, "
            f"tipo_recurso={self.tipo_recurso}, costo_total={self.costo_total})>"
        )


class ProyectoTimesheet(Base):
    """
    Modelo de Timesheet de Proyecto.

    Registro de horas trabajadas por empleado en un proyecto,
    con tarifa horaria y cálculo de costo total. Permite marcar
    horas como facturables o no facturables.
    """
    __tablename__ = "proyecto_timesheets"

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
    proyecto_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("proyectos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del proyecto",
    )
    tarea_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("proyecto_tareas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la tarea asociada",
    )
    employee_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del empleado",
    )
    empleado_nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del empleado (denormalizado)",
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha del trabajo realizado",
    )
    horas: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        comment="Horas trabajadas",
    )
    tarifa_hora: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Tarifa por hora del empleado",
    )
    costo_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Costo total (horas * tarifa_hora)",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción del trabajo realizado",
    )
    es_facturable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si las horas son facturables",
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
    proyecto: Mapped["Proyecto"] = relationship(
        "Proyecto",
        back_populates="timesheets",
        lazy="selectin",
    )
    tarea: Mapped["ProyectoTarea | None"] = relationship(
        "ProyectoTarea",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ProyectoTimesheet(id={self.id}, empleado_nombre={self.empleado_nombre}, "
            f"fecha={self.fecha}, horas={self.horas})>"
        )


class ProyectoCosto(Base):
    """
    Modelo de Costo de Proyecto.

    Registra costos adicionales asociados a un proyecto que no
    corresponden a horas de trabajo (materiales, servicios externos,
    gastos operativos, etc.). Permite vincular con comprobantes.
    """
    __tablename__ = "proyecto_costos"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    proyecto_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("proyectos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del proyecto asociado al costo",
    )
    concepto: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Concepto del costo",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción detallada del costo",
    )
    monto: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto del costo",
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha del costo",
    )
    categoria: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Categoría del costo (ej: materiales, servicios, operativos)",
    )
    es_facturable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si el costo es facturable al cliente",
    )
    comprobante_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del comprobante vinculado al costo",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación del registro",
    )

    # Relaciones
    proyecto: Mapped["Proyecto"] = relationship(
        "Proyecto",
        back_populates="costos",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ProyectoCosto(id={self.id}, concepto={self.concepto}, "
            f"monto={self.monto}, categoria={self.categoria})>"
        )
