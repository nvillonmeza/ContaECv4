"""
ContaEC - Modelo de Plantilla de Correo Electrónico
EmailTemplate: Plantillas personalizables para envío de comprobantes
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmailTemplate(Base):
    """
    Modelo de Plantilla de Correo Electrónico para ContaEC.

    Permite crear plantillas personalizadas para el envío de comprobantes
    electrónicos y otros correos del sistema. Soporta tipos específicos
    (factura, nota_crédito, etc.) y una plantilla general.
    """
    __tablename__ = "email_templates"

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
        comment="ID del usuario propietario de la plantilla",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre descriptivo de la plantilla",
    )
    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo de plantilla: factura, nota_credito, nota_debito, proforma, general",
    )
    asunto: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Asunto del correo electrónico (soporta variables {{variable}})",
    )
    cuerpo_html: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Cuerpo del correo en formato HTML (soporta variables {{variable}})",
    )
    cuerpo_texto: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Cuerpo del correo en texto plano (opcional, para clientes sin HTML)",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si es la plantilla por defecto para su tipo",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la plantilla está activa",
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
            f"<EmailTemplate(id={self.id}, nombre={self.nombre}, "
            f"tipo={self.tipo}, is_default={self.is_default})>"
        )
