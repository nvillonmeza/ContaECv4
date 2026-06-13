"""
ContaEC - Modelo de Perfil SMTP
SMTPProfile: Perfiles SMTP múltiples por usuario para envío de comprobantes
"""
import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SmtpProviderType(str, enum.Enum):
    """Tipos de proveedor SMTP"""
    GMAIL = "GMAIL"
    ZOHO = "ZOHO"
    OFFICE365 = "OFFICE365"
    OUTLOOK = "OUTLOOK"
    YAHOO = "YAHOO"
    CUSTOM = "CUSTOM"


class SmtpConnectionProtocol(str, enum.Enum):
    """Protocolos de conexión SMTP"""
    SMTP = "SMTP"
    SMTP_SSL = "SMTP_SSL"
    STARTTLS = "STARTTLS"


class SMTPProfile(Base):
    """
    Modelo de Perfil SMTP para ContaEC.

    Permite a cada usuario configurar múltiples perfiles SMTP
    para el envío de comprobantes electrónicos. Soporta distintos
    proveedores (Gmail, Zoho, Office 365, etc.) con control de
    límites diarios de envío.
    """
    __tablename__ = "smtp_profiles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario propietario del perfil SMTP",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre descriptivo del perfil (ej: Gmail Personal, Zoho Empresa)",
    )
    provider_type: Mapped[str] = mapped_column(
        String(20),
        default=SmtpProviderType.CUSTOM,
        nullable=False,
        comment="Tipo de proveedor SMTP: GMAIL, ZOHO, OFFICE365, OUTLOOK, YAHOO, CUSTOM",
    )
    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Servidor SMTP (ej: smtp.gmail.com)",
    )
    port: Mapped[int] = mapped_column(
        Integer,
        default=587,
        nullable=False,
        comment="Puerto del servidor SMTP",
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Usuario del servidor SMTP (generalmente el correo electrónico)",
    )
    password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Contraseña del servidor SMTP - cifrada con encrypt_field",
    )
    use_ssl: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si se usa SSL para la conexión SMTP",
    )
    use_tls: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si se usa TLS para la conexión SMTP",
    )
    protocol: Mapped[str] = mapped_column(
        String(20),
        default=SmtpConnectionProtocol.STARTTLS,
        nullable=False,
        comment="Protocolo de conexión: SMTP, SMTP_SSL, STARTTLS",
    )
    imap_host: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Servidor IMAP (opcional, para recepción de correos)",
    )
    imap_port: Mapped[int | None] = mapped_column(
        Integer,
        default=993,
        nullable=True,
        comment="Puerto del servidor IMAP",
    )
    pop3_host: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Servidor POP3 (opcional, para recepción de correos)",
    )
    pop3_port: Mapped[int | None] = mapped_column(
        Integer,
        default=995,
        nullable=True,
        comment="Puerto del servidor POP3",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si es el perfil SMTP por defecto del usuario",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el perfil SMTP está activo",
    )
    daily_limit: Mapped[int] = mapped_column(
        Integer,
        default=500,
        nullable=False,
        comment="Límite diario de envíos para este perfil",
    )
    sent_today: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Cantidad de correos enviados hoy",
    )
    last_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora del último envío",
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
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<SMTPProfile(id={self.id}, nombre={self.nombre}, "
            f"provider={self.provider_type}, is_default={self.is_default})>"
        )
