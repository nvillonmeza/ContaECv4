"""
ContaEC - Modelos de CRM (Customer Relationship Management)
CRMPipeline: Pipelines de ventas con etapas
CRMPipelineStage: Etapas dentro de un pipeline
CRMLead: Prospects/leads del CRM
CRMOpportunity: Oportunidades de venta en el pipeline
CRMActivity: Actividades relacionadas con leads y oportunidades
CRMContactSegment: Segmentos de contactos para marketing
CRMAutomation: Automatizaciones del CRM
"""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LeadSource(str, Enum):
    """Fuente de origen del lead"""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL = "social"
    AD = "ad"
    EVENT = "event"
    OTHER = "other"


class LeadStatus(str, Enum):
    """Estado del lead"""
    NUEVO = "nuevo"
    CONTACTADO = "contactado"
    CUALIFICADO = "cualificado"
    PROPUESTA = "propuesta"
    NEGOCIACION = "negociacion"
    GANADO = "ganado"
    PERDIDO = "perdido"


class OpportunityStatus(str, Enum):
    """Estado de la oportunidad"""
    ABIERTA = "abierta"
    GANADA = "ganada"
    PERDIDA = "perdida"


class ActivityType(str, Enum):
    """Tipo de actividad CRM"""
    LLAMADA = "llamada"
    EMAIL = "email"
    REUNION = "reunion"
    TAREA = "tarea"
    NOTA = "nota"


class ActivityStatus(str, Enum):
    """Estado de la actividad"""
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class SegmentType(str, Enum):
    """Tipo de segmento de contactos"""
    MANUAL = "manual"
    REGLA = "regla"
    RFM = "rfm"


class AutomationTriggerType(str, Enum):
    """Tipo de disparador de automatización"""
    LEAD_CREADO = "lead_creado"
    OPORTUNIDAD_GANADA = "oportunidad_ganada"
    OPORTUNIDAD_PERDIDA = "oportunidad_perdida"
    STAGE_CHANGED = "stage_changed"
    CLIENT_CREADO = "client_creado"


class CRMPipeline(Base):
    """
    Modelo de Pipeline de Ventas.

    Define el flujo de ventas de la empresa con etapas ordenadas.
    Cada pipeline pertenece a una empresa y puede tener múltiples etapas.
    """
    __tablename__ = "crm_pipelines"

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
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del pipeline",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción del pipeline",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si es el pipeline por defecto de la empresa",
    )
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Posición de orden del pipeline",
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
        back_populates="crm_pipelines",
        lazy="selectin",
    )
    stages: Mapped[list["CRMPipelineStage"]] = relationship(
        "CRMPipelineStage",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMPipeline(id={self.id}, name={self.name}, "
            f"is_default={self.is_default})>"
        )


class CRMPipelineStage(Base):
    """
    Modelo de Etapa de Pipeline.

    Cada etapa dentro de un pipeline con probabilidad asociada
    y color para representación visual en el Kanban.
    """
    __tablename__ = "crm_pipeline_stages"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    pipeline_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("crm_pipelines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del pipeline al que pertenece la etapa",
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre de la etapa",
    )
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Posición de orden dentro del pipeline",
    )
    probability_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Porcentaje de probabilidad de cierre (0-100)",
    )
    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
        comment="Color hex de la etapa (ej: #FF5733)",
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
    pipeline: Mapped["CRMPipeline"] = relationship(
        "CRMPipeline",
        back_populates="stages",
        lazy="selectin",
    )
    opportunities: Mapped[list["CRMOpportunity"]] = relationship(
        "CRMOpportunity",
        back_populates="stage",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMPipelineStage(id={self.id}, name={self.name}, "
            f"order={self.order}, probability={self.probability_percentage})>"
        )


class CRMLead(Base):
    """
    Modelo de Lead CRM.

    Representa un prospecto o contacto potencial. Puede ser convertido
    en una oportunidad de venta. Seguimiento del ciclo de vida del lead.
    """
    __tablename__ = "crm_leads"

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
    client_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del cliente asociado (opcional)",
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre del lead",
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Apellido del lead",
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Correo electrónico del lead",
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Teléfono del lead",
    )
    source: Mapped[str] = mapped_column(
        String(20),
        default=LeadSource.OTHER.value,
        nullable=False,
        index=True,
        comment="Fuente: website, referral, social, ad, event, other",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=LeadStatus.NUEVO.value,
        nullable=False,
        index=True,
        comment="Estado: nuevo, contactado, cualificado, propuesta, negociacion, ganado, perdido",
    )
    assigned_to: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del usuario asignado al lead",
    )
    estimated_value: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Valor estimado del lead",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionales del lead",
    )
    last_contact_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha del último contacto",
    )
    next_follow_up: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha del próximo seguimiento",
    )
    converted_to_opportunity: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si el lead fue convertido a oportunidad",
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
        back_populates="crm_leads",
        lazy="selectin",
    )
    assigned_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMLead(id={self.id}, name={self.first_name} {self.last_name}, "
            f"status={self.status}, source={self.source})>"
        )


class CRMOpportunity(Base):
    """
    Modelo de Oportunidad de Venta CRM.

    Oportunidad de venta dentro del pipeline. Asociada a una etapa
    del pipeline, con seguimiento de monto, probabilidad y fechas.
    """
    __tablename__ = "crm_opportunities"

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
    lead_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("crm_leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del lead origen (opcional)",
    )
    client_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del cliente asociado (opcional)",
    )
    pipeline_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("crm_pipelines.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del pipeline",
    )
    stage_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("crm_pipeline_stages.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID de la etapa actual del pipeline",
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre de la oportunidad",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción de la oportunidad",
    )
    estimated_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto estimado de la oportunidad",
    )
    probability: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Probabilidad de cierre (0-100)",
    )
    expected_close_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha esperada de cierre",
    )
    actual_close_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha real de cierre",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=OpportunityStatus.ABIERTA.value,
        nullable=False,
        index=True,
        comment="Estado: abierta, ganada, perdida",
    )
    assigned_to: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del usuario asignado",
    )
    lost_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Razón de pérdida (si aplica)",
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
        back_populates="crm_opportunities",
        lazy="selectin",
    )
    lead: Mapped["CRMLead | None"] = relationship(
        "CRMLead",
        lazy="selectin",
    )
    stage: Mapped["CRMPipelineStage"] = relationship(
        "CRMPipelineStage",
        back_populates="opportunities",
        lazy="selectin",
    )
    pipeline: Mapped["CRMPipeline"] = relationship(
        "CRMPipeline",
        lazy="selectin",
    )
    assigned_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMOpportunity(id={self.id}, name={self.name}, "
            f"status={self.status}, estimated_amount={self.estimated_amount})>"
        )


class CRMActivity(Base):
    """
    Modelo de Actividad CRM.

    Registro de actividades (llamadas, emails, reuniones, tareas, notas)
    asociadas a oportunidades o leads. Permite seguimiento detallado
    de todas las interacciones con los contactos.
    """
    __tablename__ = "crm_activities"

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
    opportunity_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("crm_opportunities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la oportunidad asociada (opcional)",
    )
    lead_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("crm_leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del lead asociado (opcional)",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que realiza la actividad",
    )
    type: Mapped[str] = mapped_column(
        String(20),
        default=ActivityType.NOTA.value,
        nullable=False,
        index=True,
        comment="Tipo: llamada, email, reunion, tarea, nota",
    )
    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Asunto de la actividad",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción de la actividad",
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha programada de la actividad",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de completación de la actividad",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=ActivityStatus.PENDIENTE.value,
        nullable=False,
        index=True,
        comment="Estado: pendiente, completada, cancelada",
    )
    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Resultado de la actividad",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación del registro",
    )

    # Relaciones
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="crm_activities",
        lazy="selectin",
    )
    user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMActivity(id={self.id}, subject={self.subject}, "
            f"type={self.type}, status={self.status})>"
        )


class CRMContactSegment(Base):
    """
    Modelo de Segmento de Contactos CRM.

    Permite agrupar contactos/clientes en segmentos para marketing
    dirigido. Soporta segmentos manuales, basados en reglas y RFM.
    """
    __tablename__ = "crm_contact_segments"

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
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del segmento",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción del segmento",
    )
    type: Mapped[str] = mapped_column(
        String(20),
        default=SegmentType.MANUAL.value,
        nullable=False,
        index=True,
        comment="Tipo: manual, regla, rfm",
    )
    rules: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reglas JSON para segmentos basados en reglas",
    )
    rfm_score: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Configuración RFM JSON para segmentos RFM",
    )
    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
        comment="Color hex del segmento (ej: #3498DB)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el segmento está activo",
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
        back_populates="crm_contact_segments",
        lazy="selectin",
    )
    client_members: Mapped[list["CRMContactSegmentMember"]] = relationship(
        "CRMContactSegmentMember",
        back_populates="segment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMContactSegment(id={self.id}, name={self.name}, "
            f"type={self.type}, is_active={self.is_active})>"
        )


class CRMContactSegmentMember(Base):
    """
    Modelo de Miembro de Segmento de Contactos.

    Tabla intermedia que relaciona clientes con segmentos.
    """
    __tablename__ = "crm_contact_segment_members"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    segment_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("crm_contact_segments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del segmento",
    )
    client_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del cliente miembro del segmento",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de adición al segmento",
    )

    # Relaciones
    segment: Mapped["CRMContactSegment"] = relationship(
        "CRMContactSegment",
        back_populates="client_members",
        lazy="selectin",
    )
    client: Mapped["Client"] = relationship(  # noqa: F821
        "Client",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMContactSegmentMember(id={self.id}, "
            f"segment_id={self.segment_id}, client_id={self.client_id})>"
        )


class CRMAutomation(Base):
    """
    Modelo de Automatización CRM.

    Define reglas de automatización que se ejecutan cuando ocurren
    eventos específicos (triggers) y ejecutan acciones predefinidas.
    """
    __tablename__ = "crm_automations"

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
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre de la automatización",
    )
    trigger_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Tipo de disparador: lead_creado, oportunidad_ganada, oportunidad_perdida, stage_changed, client_creado",
    )
    trigger_conditions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Condiciones del disparador en JSON",
    )
    actions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Lista de acciones en JSON: send_email, create_task, notify_user, change_stage, assign_user",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la automatización está activa",
    )
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de la última ejecución",
    )
    trigger_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de veces que se ha ejecutado",
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
        back_populates="crm_automations",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CRMAutomation(id={self.id}, name={self.name}, "
            f"trigger_type={self.trigger_type}, is_active={self.is_active})>"
        )
