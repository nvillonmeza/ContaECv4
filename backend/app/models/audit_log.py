"""
ContaEC - Modelo de Registro de Auditoría
AuditLog: Registro de acciones realizadas en el sistema
para trazabilidad y cumplimiento normativo
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    """
    Modelo de Registro de Auditoría del sistema ContaEC.

    Registra todas las acciones importantes realizadas por los usuarios
    para trazabilidad, seguridad y cumplimiento normativo.
    Incluye información del usuario, acción realizada, entidad afectada
    y valores anterior/nuevo para auditoría detallada.
    """
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del usuario que realizó la acción",
    )
    user_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Correo electrónico del usuario (desnormalizado para consulta)",
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Acción realizada: CREATE, UPDATE, DELETE, LOGIN, LOGOUT, SIGN, SEND, AUTHORIZE, etc.",
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo de entidad afectada: user, company, client, product, comprobante, etc.",
    )
    entity_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID de la entidad afectada",
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Descripción legible de la acción realizada",
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="Dirección IP desde donde se realizó la acción",
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User-Agent del navegador o cliente que realizó la acción",
    )
    old_values: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Valores anteriores a la acción (formato JSON)",
    )
    new_values: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Valores nuevos después de la acción (formato JSON)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha y hora en que se registró la acción",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action={self.action}, "
            f"entity_type={self.entity_type}, user_email={self.user_email})>"
        )
