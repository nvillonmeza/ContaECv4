"""
ContaEC - Modelo de Producto/Servicio
Product: Catálogo de productos y servicios para facturación electrónica
Incluye tipos según SRI: B=Bien, S=Servicio
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductoTipo(str, enum.Enum):
    """
    Tipo de producto según catálogo del SRI.
    B = Bien (producto físico)
    S = Servicio (servicio intangible)
    """
    BIEN = "B"        # Bien (producto)
    SERVICIO = "S"    # Servicio (service)


class Product(Base):
    """
    Modelo de Producto/Servicio para facturación electrónica del SRI.

    Almacena el catálogo de productos y servicios de la empresa
    con sus respectivos códigos, precios e impuestos aplicables
    según los catálogos del SRI (Tabla 16 para IVA, Tabla 18 para ICE).
    """
    __tablename__ = "products"

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
        comment="ID de la empresa a la que pertenece el producto",
    )
    # Códigos del producto
    codigo_principal: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código principal del producto (SKU)",
    )
    codigo_auxiliar: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Código auxiliar del producto",
    )
    # Descripción
    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Descripción del producto o servicio",
    )
    # Tipo: Bien o Servicio
    tipo: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        comment="Tipo de producto: B=Bien, S=Servicio",
    )
    # Precio unitario (sin impuestos)
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Precio unitario del producto (sin impuestos)",
    )
    # IVA - según Tabla 16 del SRI
    iva_codigo: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Código de tarifa de IVA según Tabla 16 del SRI (ej: 10 para 13%)",
    )
    iva_porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Porcentaje de IVA (0, 5, 8, 12, 13, 14, 15)",
    )
    # ICE - según Tabla 18 del SRI (opcional)
    ice_codigo: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
        comment="Código de tarifa de ICE según Tabla 18 del SRI",
    )
    ice_porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje de ICE (si aplica)",
    )
    # Unidad de medida y descuento
    unidad_medida: Mapped[str] = mapped_column(
        String(50),
        default="Unidad",
        nullable=False,
        comment="Unidad de medida del producto (ej: Unidad, Kilogramo, Litro)",
    )
    descuento: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Porcentaje de descuento por defecto",
    )
    # Código de barras e inventario
    codigo_barras: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Código de barras EAN/UPC del producto",
    )
    stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        default=Decimal("0"),
        nullable=False,
        comment="Cantidad actual en stock",
    )
    stock_minimo: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        default=Decimal("0"),
        nullable=False,
        comment="Nivel mínimo de stock para alertas",
    )
    ubicacion: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Ubicación física en bodega/almacén",
    )
    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el producto está activo",
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
        back_populates="products",
        lazy="selectin",
    )
    detalles: Mapped[list["ComprobanteDetalle"]] = relationship(  # noqa: F821
        "ComprobanteDetalle",
        back_populates="product",
        lazy="selectin",
    )
    kardex_movements: Mapped[list["Kardex"]] = relationship(  # noqa: F821
        "Kardex",
        back_populates="product",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, codigo_principal={self.codigo_principal}, "
            f"descripcion={self.descripcion}, tipo={self.tipo})>"
        )
