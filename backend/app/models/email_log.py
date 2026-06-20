"""
ContaEC - Modelo de Log de Envío de Correos
EmailLog: Registro de todos los correos enviados con tracking de estado
"""
import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmailLogTipo(str, enum.Enum):
    """Tipo de correo electrónico"""
    COMPROBANTE = "comprobante"       # Envío de comprobante autorizado
    PROFORMA = "proforma"             # Envío de proforma
    NOTIFICACION = "notificacion"     # Notificación del sistema
    MARKETING = "marketing"           # Correo de marketing
    OTRO = "otro"                     # Otro tipo


class EmailLogEstado(str, enum.Enum):
    """Estado del envío de correo"""
    PENDIENTE = "pendiente"           # En cola para envío
    ENVIADO = "enviado"               # Enviado exitosamente
    FALLIDO = "fallido"               # Error al enviar
    REINTENTANDO = "reintentando"     # Reintentando envío
    CANCELADO = "cancelado"           # Cancelado por usuario o sistema


class EmailLog(Base):
    """
    Modelo de Log de Envío de Correos.

    Registra cada correo enviado con información completa para
    tracking, auditoría y reintentos automáticos.
    """
    __tablename__ = "email_logs"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    # Relación con usuario propietario
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del usuario que originó el envío",
    )
    # Tipo de correo
    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo de correo: comprobante, proforma, notificacion, etc.",
    )
    # Destinatarios
    destinatario_principal: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Correo del destinatario principal",
    )
    destinatarios_cc: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Destinatarios en copia (separados por coma)",
    )
    destinatarios_cco: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Destinatarios en copia oculta (separados por coma)",
    )
    # Contenido
    asunto: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Asunto del correo",
    )
    cuerpo_html: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Cuerpo del correo en formato HTML",
    )
    cuerpo_texto: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Cuerpo del correo en texto plano",
    )
    # Estado del envío
    estado: Mapped[str] = mapped_column(
        String(20),
        default=EmailLogEstado.PENDIENTE,
        nullable=False,
        index=True,
        comment="Estado: pendiente, enviado, fallido, reintentando, cancelado",
    )
    # Reintentos
    intentos: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Número de intentos de envío",
    )
    max_intentos: Mapped[int] = mapped_column(
        default=3,
        nullable=False,
        comment="Máximo número de intentos permitidos",
    )
    proximo_intento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha programada para próximo reintento",
    )
    # Respuesta del servidor SMTP
    respuesta_smtp: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Respuesta completa del servidor SMTP",
    )
    error_mensaje: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Mensaje de error si el envío falló",
    )
    # Metadatos
    email_template_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("email_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la plantilla utilizada (si aplica)",
    )
    comprobante_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID del comprobante asociado (si aplica)",
    )
    smtp_profile_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("smtp_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del perfil SMTP utilizado",
    )
    # Archivo adjunto (ruta o metadata)
    adjuntos: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Lista de archivos adjuntos (JSON o ruta)",
    )
    # Timestamps
    fecha_envio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de envío exitoso",
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
    template: Mapped["EmailTemplate"] = relationship(  # noqa: F821
        "EmailTemplate",
        lazy="selectin",
    )
    comprobante: Mapped["Comprobante"] = relationship(  # noqa: F821
        "Comprobante",
        lazy="selectin",
    )
    smtp_profile: Mapped["SMTPProfile"] = relationship(  # noqa: F821
        "SMTPProfile",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<EmailLog(id={self.id}, destinatario={self.destinatario_principal}, "
            f"estado={self.estado}, intentos={self.intentos})>"
        )

    @property
    def puede_reintentar(self) -> bool:
        """Verifica si el correo puede ser reintentado"""
        return (
            self.estado in [EmailLogEstado.PENDIENTE, EmailLogEstado.FALLIDO, EmailLogEstado.REINTENTANDO]
            and self.intentos < self.max_intentos
            and (self.proximo_intento is None or self.proximo_intento <= datetime.now(timezone.utc))
        )