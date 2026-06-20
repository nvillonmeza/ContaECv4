"""
ContaEC - Modelo de Turnos Laborales
Turnos: Gestión de turnos rotativos para empleados
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


class TurnoTipo(str, enum.Enum):
    """Tipos de turno"""
    DIA = "dia"           # 6:00 - 14:00
    TARDE = "tarde"       # 14:00 - 22:00
    NOCHE = "noche"       # 22:00 - 6:00
    MADRUGADA = "madrugada"  # 4:00 - 12:00
    FIN_SEMANA = "fin_semana"  # Sábado/Domingo
    FESTIVO = "festivo"   # Días festivos
    PERSONALIZADO = "personalizado"


class TurnoEstado(str, enum.Enum):
    """Estados del turno"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    PROGRAMADO = "programado"
    CANCELADO = "cancelado"


class TurnoRotativo(Base):
    """
    Modelo de Turno Rotativo.

    Define turnos de trabajo con horarios específicos, permitiendo
    rotación entre turnos diurnos, vespertinos, nocturnos y de fin
    de semana.

    Conforme al Código del Trabajo ecuatoriano:
    - Turno diurno: 6:00 a 22:00 (máx 8 horas)
    - Turno nocturno: 22:00 a 6:00 (máx 7 horas, recargo 15%)
    - Turno mixto: combina diurno/nocturno (máx 8 horas)
    """
    __tablename__ = "turnos_rotativos"

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
        comment="ID del usuario que creó el turno",
    )

    # ==========================================
    # Información del turno
    # ==========================================
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre del turno (ej: Matutino A, Vespertino B)",
    )
    codigo: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment="Código único del turno",
    )
    tipo_turno: Mapped[str] = mapped_column(
        String(20),
        default=TurnoTipo.DIA,
        nullable=False,
        comment="Tipo: dia, tarde, noche, madrugada, fin_semana, festivo, personalizado",
    )

    # ==========================================
    # Horario del turno
    # ==========================================
    hora_entrada: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        comment="Hora de entrada (HH:MM formato 24h)",
    )
    hora_salida: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        comment="Hora de salida (HH:MM formato 24h)",
    )
    horas_jornada: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Total de horas de la jornada",
    )
    tiene_descanso: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si incluye tiempo de descanso dentro de la jornada",
    )
    duracion_descanso: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
        comment="Duración del descanso en minutos",
    )

    # ==========================================
    # Días de aplicación
    # ==========================================
    dias_semana: Mapped[str] = mapped_column(
        String(50),
        default="1,2,3,4,5",
        nullable=False,
        comment="Días de aplicación (1=Lunes, 7=Domingo), comma-separated",
    )
    es_turno_fijo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si es False, el turno es rotativo",
    )

    # ==========================================
    # Recargos
    # ==========================================
    porcentaje_recargo: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Porcentaje de recargo sobre hora normal (nocturno: 15%)",
    )
    valor_hora_extra: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Valor referencial de hora extra para este turno",
    )

    # ==========================================
    # Estado y auditoría
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(20),
        default=TurnoEstado.ACTIVO,
        nullable=False,
        index=True,
        comment="Estado: activo, inactivo, programado, cancelado",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones del turno",
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
    company: Mapped["Company"] = relationship(
        "Company",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )
    asignaciones: Mapped[list["TurnoAsignacion"]] = relationship(
        "TurnoAsignacion",
        back_populates="turno",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<TurnoRotativo(id={self.id}, nombre={self.nombre}, "
            f"tipo={self.tipo_turno}, horario={self.hora_entrada}-{self.hora_salida})>"
        )

    @property
    def es_turno_nocturno(self) -> bool:
        """Verifica si es turno nocturno (22:00 - 6:00)"""
        return self.tipo_turno == TurnoTipo.NOCHE

    @property
    def tiene_recargo(self) -> bool:
        """Verifica si tiene recargo nocturno o especial"""
        return self.porcentaje_recargo > 0


class TurnoAsignacion(Base):
    """
    Modelo de Asignación de Turno.

    Asigna turnos específicos a empleados para fechas determinadas,
    permitiendo programación de turnos rotativos.
    """
    __tablename__ = "turnos_asignaciones"

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
    turno_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("turnos_rotativos.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del turno asignado",
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
        comment="ID del usuario que asignó el turno",
    )

    # ==========================================
    # Fecha de asignación
    # ==========================================
    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha para la cual se asigna el turno",
    )
    es_recurrente: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Si es True, se repite según patrón",
    )
    patron_repeticion: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Patrón de repetición: diario, semanal, cada_semana_n",
    )
    fecha_fin_repeticion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de fin de repeticion",
    )

    # ==========================================
    # Estado de la asignación
    # ==========================================
    estado: Mapped[str] = mapped_column(
        String(20),
        default=TurnoEstado.PROGRAMADO,
        nullable=False,
        comment="Estado: programado, completado, cancelado, inasistencia",
    )
    motivo_cambio: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo de cambio o cancelación",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones de la asignación",
    )

    # ==========================================
    # Registro real (post-ejecución)
    # ==========================================
    hora_entrada_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Hora real de entrada (registro biométrico)",
    )
    hora_salida_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Hora real de salida (registro biométrico)",
    )
    horas_trabajadas: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Horas realmente trabajadas",
    )
    horas_extras: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Horas extras trabajadas",
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
        back_populates="turnos_asignaciones",
        lazy="selectin",
    )
    turno: Mapped["TurnoRotativo"] = relationship(
        "TurnoRotativo",
        back_populates="asignaciones",
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

    def __repr__(self) -> str:
        return (
            f"<TurnoAsignacion(id={self.id}, employee_id={self.employee_id}, "
            f"fecha={self.fecha_asignacion}, estado={self.estado})>"
        )