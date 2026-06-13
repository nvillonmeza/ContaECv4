"""
ContaEC - Modelo de Proveedor
Supplier: Información de proveedores para compras y retenciones
Incluye tipos de identificación según catálogos del SRI (Tabla 7)
"""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Supplier(Base):
    """
    Modelo de Proveedor para facturación electrónica del SRI.

    Almacena la información de los proveedores utilizados en las órdenes
    de compra, recepciones de mercadería, cuentas por pagar y retenciones
    de compra. Cada proveedor está asociado a una empresa específica.
    """
    __tablename__ = "suppliers"

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
        comment="ID de la empresa a la que pertenece el proveedor",
    )
    # Tipo y número de identificación
    tipo_identificacion: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Tipo de identificación SRI: 04=RUC, 05=Cédula, 06=Pasaporte, 08=Exterior",
    )
    identificacion: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de identificación (RUC, cédula, pasaporte, etc.)",
    )
    # Información del proveedor
    razon_social: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Razón social o nombre completo del proveedor",
    )
    nombre_comercial: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nombre comercial del proveedor",
    )
    direccion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Dirección del proveedor",
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Correo electrónico del proveedor",
    )
    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de teléfono del proveedor",
    )
    # Información de contacto
    contacto_nombre: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nombre del contacto principal del proveedor",
    )
    contacto_telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Teléfono del contacto principal del proveedor",
    )
    # Configuración de pago
    forma_pago_habitual: Mapped[str] = mapped_column(
        String(2),
        default="01",
        nullable=False,
        comment="Código de forma de pago habitual según Tabla 23 del SRI",
    )
    plazo_credito_dias: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Plazo de crédito habitual en días (0 = contado)",
    )
    # Retenciones habituales
    retencion_iva_codigo: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
        comment="Código de retención de IVA habitual según Tabla 19 del SRI",
    )
    retencion_iva_porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje de retención de IVA habitual",
    )
    retencion_renta_codigo: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
        comment="Código de retención de Renta habitual según Tabla 20 del SRI",
    )
    retencion_renta_porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje de retención de Renta habitual",
    )
    # Observaciones y estado
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales sobre el proveedor",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el proveedor está activo",
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
        back_populates="suppliers",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Supplier(id={self.id}, tipo_identificacion={self.tipo_identificacion}, "
            f"identificacion={self.identificacion}, razon_social={self.razon_social})>"
        )
