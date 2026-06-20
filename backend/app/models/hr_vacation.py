"""
ContaEC - Modelo de Vacaciones
Vacaciones: Gestión de días de vacaciones por empleado
Conforme al Código del Trabajo ecuatoriano (15 días + 1 por año adicional)
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VacacionesEstado(str, enum.Enum):
    """Estados de la solicitud de vacaciones"""
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"
    DISFRUTADA = "disfrutada"


class VacacionesPeriodo(Base):
    """
    Modelo de Período de Vacaciones.

    Registra el acumulado de días de vacaciones por período anual,
    permitiendo control de días disponibles, tomados y pendientes.

    Conforme al Código del Trabajo ecuatoriano:
    - 15 días de vacaciones por cada año completo de trabajo
    - 1 día adicional por cada año adicional (a partir del 2do año)
    - Máximo acumulable: 30 días
    """
    __tablename__ = "vacaciones_periodos"

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

    # ==========================================
    # Período devacaciones
    # ==========================================
    periodo_anio: Mapped[int] = mapped_column(
        Numeric(4),
        nullable=False,
        comment="Año del período de vacaciones (ej: 2024)",
    )
    fecha_inicio_periodo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de inicio del período (aniversario de ingreso)",
    )
    fecha_fin_periodo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de fin del período",
    )

    # ==========================================
    # Días de vacaciones
    # ==========================================
    dias_correspondientes: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("15.00"),
        nullable=False,
        comment="Días que corresponden por año de servicio (15 + adicionales)",
    )
    dias_tomados: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Días de vacaciones ya tomados/disfrutados",
    )
    dias_pendientes: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Días pendientes por tomar",
    )
    dias_acumulados_anteriores: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Días acumulados de períodos anteriores (máx 30)",
    )

    # ==========================================
    # Estado del período
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        comment="Estado: pendiente, en curso, completado, vencido",
    )
    fecha_vencimiento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de vencimiento para tomar vacaciones",
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
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="vacaciones_periodos",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(
        "Company",
        lazy="selectin",
    )
    solicitudes: Mapped[list["VacacionesSolicitud"]] = relationship(
        "VacacionesSolicitud",
        back_populates="periodo",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<VacacionesPeriodo(id={self.id}, employee_id={self.employee_id}, "
            f"anio={self.periodo_anio}, dias_pendientes={self.dias_pendientes})>"
        )

    @property
    def dias_disponibles_total(self) -> Decimal:
        """Total de días disponibles (pendientes + acumulados)"""
        return self.dias_pendientes + self.dias_acumulados_anteriores


class VacacionesSolicitud(Base):
    """
    Modelo de Solicitud de Vacaciones.

    Registra cada solicitud de vacaciones por empleado, con fechas
    de inicio/fin, estado de aprobación y registro de disfrute.
    """
    __tablename__ = "vacaciones_solicitudes"

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
    periodo_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("vacaciones_periodos.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del período de vacaciones al que aplica",
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa",
    )
    aprobado_por_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del usuario que aprobó la solicitud",
    )

    # ==========================================
    # Fechas de vacaciones
    # ==========================================
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de inicio de las vacaciones",
    )
    fecha_fin: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de fin de las vacaciones",
    )
    dias_solicitados: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Número de días solicitados",
    )

    # ==========================================
    # Estado de la solicitud
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(20),
        default=VacacionesEstado.PENDIENTE,
        nullable=False,
        index=True,
        comment="Estado: pendiente, aprobada, rechazada, cancelada, disfrutada",
    )
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de aprobación",
    )
    fecha_rechazo: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de rechazo",
    )
    motivo_rechazo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo del rechazo (si aplica)",
    )

    # ==========================================
    # Registro de disfrute
    # ==========================================
    fecha_real_inicio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha real de inicio (puede diferir de la solicitada)",
    )
    fecha_real_fin: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha real de fin",
    )
    dias_disfrutados: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Días realmente disfrutados",
    )

    # ==========================================
    # Observaciones
    # ==========================================
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones de la solicitud",
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
        back_populates="vacaciones_solicitudes",
        lazy="selectin",
    )
    periodo: Mapped["VacacionesPeriodo"] = relationship(
        "VacacionesPeriodo",
        back_populates="solicitudes",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(
        "Company",
        lazy="selectin",
    )
    aprobado_por: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<VacacionesSolicitud(id={self.id}, employee_id={self.employee_id}, "
            f"estado={self.estado}, dias={self.dias_solicitados})>"
        )

    @property
    def duracion_dias(self) -> int:
        """Calcula duración en días entre fecha_inicio y fecha_fin"""
        if not self.fecha_inicio or not self.fecha_fin:
            return 0
        delta = self.fecha_fin - self.fecha_inicio
        return delta.days + 1  # Incluir día inicial y final


class VacacionesHistorial(Base):
    """
    Modelo de Historial de Vacaciones.

    Registro histórico de vacaciones tomadas por empleado,
    útil para reportes y cálculos de antigüedad.
    """
    __tablename__ = "vacaciones_historial"

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
    )
    solicitud_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("vacaciones_solicitudes.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID de la solicitud origen (si existe)",
    )
    periodo_anio: Mapped[int] = mapped_column(
        Numeric(4),
        nullable=False,
        comment="Año del período",
    )
    dias_gozados: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Días de vacaciones gozados",
    )
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    fecha_fin: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relaciones
    employee: Mapped["Employee"] = relationship(
        "Employee",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<VacacionesHistorial(id={self.id}, employee_id={self.employee_id}, "
            f"anio={self.periodo_anio}, dias={self.dias_gozados})>"
        )