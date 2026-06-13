"""
ContaEC - Modelo de Cliente
Client: Información del cliente para facturación electrónica
Incluye tipos de identificación según catálogos del SRI
"""
import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoIdentificacion(str, enum.Enum):
    """
    Tipos de identificación según catálogo del SRI (Tabla 7).
    Utilizados para identificar al comprador en comprobantes electrónicos.
    """
    RUC = "04"                    # Registro Único de Contribuyente
    CEDULA = "05"                 # Cédula de identidad
    PASAPORTE = "06"              # Pasaporte
    CONSUMIDOR_FINAL = "07"       # Consumidor final
    IDENTIFICACION_EXTERIOR = "08"  # Identificación del exterior


class Client(Base):
    """
    Modelo de Cliente para facturación electrónica del SRI.
    
    Almacena la información de los clientes/compradores que se utilizan
    en los comprobantes electrónicos. Cada cliente está asociado a una
    empresa específica.
    
    Nota: El cliente "Consumidor Final" (tipo 07) es especial y se crea
    automáticamente por defecto para cada empresa.
    """
    __tablename__ = "clients"

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
        comment="ID de la empresa a la que pertenece el cliente",
    )
    # Tipo y número de identificación
    tipo_identificacion: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Tipo de identificación SRI: 04=RUC, 05=Cédula, 06=Pasaporte, 07=Consumidor Final, 08=Exterior",
    )
    identificacion: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de identificación (RUC, cédula, pasaporte, etc.)",
    )
    # Información del cliente
    razon_social: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Razón social o nombre completo del cliente",
    )
    direccion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Dirección del cliente",
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Correo electrónico del cliente",
    )
    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de teléfono del cliente",
    )
    # Indicadores especiales
    is_default_consumer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si es el cliente Consumidor Final por defecto",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el cliente está activo",
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
        back_populates="clients",
        lazy="selectin",
    )
    comprobantes: Mapped[list["Comprobante"]] = relationship(  # noqa: F821
        "Comprobante",
        back_populates="client",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Client(id={self.id}, tipo_identificacion={self.tipo_identificacion}, "
            f"identificacion={self.identificacion}, razon_social={self.razon_social})>"
        )

    @property
    def is_consumidor_final(self) -> bool:
        """Indica si el cliente es consumidor final"""
        return self.tipo_identificacion == TipoIdentificacion.CONSUMIDOR_FINAL
