"""
ContaEC - Modelo de Notificaciones del Sistema
Notification: Notificaciones generales del sistema para alertas,
mensajes informativos y comunicados a usuarios
"""
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NotificationType(str, Enum):
    """Tipos de notificación"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    SYSTEM = "system"


class NotificationCategory(str, Enum):
    """Categorías de notificación"""
    GENERAL = "general"
    BILLING = "billing"
    ACCOUNTING = "accounting"
    HR = "hr"
    LICENSE = "license"
    SECURITY = "security"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    """Niveles de prioridad de notificación"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    Modelo de Notificación del sistema ContaEC.

    Notificaciones generales para alertas, mensajes informativos,
    comunicados y avisos del sistema dirigidos a usuarios o empresas.
    Soporta notificaciones globales (company_id=null), por empresa
    (user_id=null = todos los usuarios de la empresa) o individuales.
    """
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    company_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID de la empresa (null = notificación global)",
    )
    user_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID del usuario destinatario (null = todos los usuarios de la empresa)",
    )
    type: Mapped[str] = mapped_column(
        String(30),
        default=NotificationType.INFO.value,
        nullable=False,
        index=True,
        comment="Tipo de notificación: info, warning, error, success, system",
    )
    category: Mapped[str] = mapped_column(
        String(30),
        default=NotificationCategory.GENERAL.value,
        nullable=False,
        index=True,
        comment="Categoría: general, billing, accounting, hr, license, security, system",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Título de la notificación",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mensaje detallado de la notificación",
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Indica si la notificación ha sido leída",
    )
    action_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL de navegación al hacer clic en la notificación",
    )
    action_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Etiqueta para el botón de acción",
    )
    priority: Mapped[str] = mapped_column(
        String(10),
        default=NotificationPriority.NORMAL.value,
        nullable=False,
        index=True,
        comment="Prioridad: low, normal, high, urgent",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de expiración para auto-ocultar la notificación",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Indica si la notificación está activa",
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
        back_populates="notifications",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Notification(id={self.id}, type={self.type}, "
            f"category={self.category}, title={self.title}, is_read={self.is_read})>"
        )
