"""
ContaEC - Modelos de Compras
OrdenCompra: Órdenes de compra a proveedores
OrdenCompraDetalle: Detalle de líneas de la orden de compra
RecepcionMercaderia: Recepción de mercadería
RecepcionMercaderiaDetalle: Detalle de la recepción
CuentaPorPagar: Cuentas por pagar a proveedores
RetencionCompra: Retenciones en la fuente por compras
"""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrdenCompra(Base):
    """
    Modelo de Orden de Compra.

    Registra las órdenes de compra emitidas a proveedores con sus
    detalles, estado de envío y recepción, y totales.
    """
    __tablename__ = "ordenes_compra"

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
    supplier_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del proveedor",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que creó la orden",
    )
    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de orden de compra (ej: OC-000001)",
    )
    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de emisión de la orden",
    )
    fecha_entrega_estimada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha estimada de entrega",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default="borrador",
        nullable=False,
        index=True,
        comment="Estado: borrador, enviada, parcial, recibida, anulada",
    )
    subtotal_sin_impuestos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal sin impuestos",
    )
    total_iva: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total del IVA",
    )
    total_con_impuestos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total con impuestos",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la orden está activa",
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
    detalles: Mapped[list["OrdenCompraDetalle"]] = relationship(
        "OrdenCompraDetalle",
        back_populates="orden_compra",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    supplier: Mapped["Supplier"] = relationship(  # noqa: F821
        "Supplier",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="ordenes_compra",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<OrdenCompra(id={self.id}, numero={self.numero}, "
            f"estado={self.estado})>"
        )


class OrdenCompraDetalle(Base):
    """
    Modelo de Detalle de Orden de Compra.

    Cada línea de la orden de compra con cantidad, precio e impuestos.
    """
    __tablename__ = "ordenes_compra_detalles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    orden_compra_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("ordenes_compra.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la orden de compra",
    )
    product_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del producto (opcional)",
    )
    codigo_principal: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código principal del bien o servicio",
    )
    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Descripción del bien o servicio",
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Cantidad solicitada",
    )
    cantidad_recibida: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        default=Decimal("0"),
        nullable=False,
        comment="Cantidad recibida hasta la fecha",
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Precio unitario sin impuestos",
    )
    iva_codigo: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Código de tarifa de IVA según Tabla 16 del SRI",
    )
    iva_porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Porcentaje de IVA",
    )
    descuento: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto de descuento",
    )
    precio_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Precio total (cantidad * precio_unitario - descuento)",
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
    orden_compra: Mapped["OrdenCompra"] = relationship(
        "OrdenCompra",
        back_populates="detalles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<OrdenCompraDetalle(id={self.id}, descripcion={self.descripcion}, "
            f"cantidad={self.cantidad})>"
        )


class RecepcionMercaderia(Base):
    """
    Modelo de Recepción de Mercadería.

    Registra la recepción de mercadería, puede estar asociada o no
    a una orden de compra.
    """
    __tablename__ = "recepciones_mercaderia"

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
    orden_compra_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("ordenes_compra.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la orden de compra (opcional)",
    )
    supplier_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del proveedor",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que registró la recepción",
    )
    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de recepción (ej: RM-000001)",
    )
    fecha_recepcion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de recepción de la mercadería",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        index=True,
        comment="Estado: pendiente, conformada, rechazada",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la recepción está activa",
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
    detalles: Mapped[list["RecepcionMercaderiaDetalle"]] = relationship(
        "RecepcionMercaderiaDetalle",
        back_populates="recepcion",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    supplier: Mapped["Supplier"] = relationship(  # noqa: F821
        "Supplier",
        lazy="selectin",
    )
    orden_compra: Mapped["OrdenCompra | None"] = relationship(
        "OrdenCompra",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<RecepcionMercaderia(id={self.id}, numero={self.numero}, "
            f"estado={self.estado})>"
        )


class RecepcionMercaderiaDetalle(Base):
    """
    Modelo de Detalle de Recepción de Mercadería.

    Cada línea de la recepción con cantidad recibida, dañada y precios.
    """
    __tablename__ = "recepciones_mercaderia_detalles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    recepcion_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("recepciones_mercaderia.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la recepción de mercadería",
    )
    product_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del producto (opcional)",
    )
    orden_compra_detalle_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("ordenes_compra_detalles.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del detalle de orden de compra (opcional)",
    )
    codigo_principal: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código principal del bien o servicio",
    )
    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Descripción del bien o servicio",
    )
    cantidad_recibida: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Cantidad recibida",
    )
    cantidad_dañada: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        default=Decimal("0"),
        nullable=False,
        comment="Cantidad dañada o defectuosa",
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Precio unitario sin impuestos",
    )
    precio_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Precio total (cantidad_recibida * precio_unitario)",
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
    recepcion: Mapped["RecepcionMercaderia"] = relationship(
        "RecepcionMercaderia",
        back_populates="detalles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<RecepcionMercaderiaDetalle(id={self.id}, descripcion={self.descripcion}, "
            f"cantidad_recibida={self.cantidad_recibida})>"
        )


class CuentaPorPagar(Base):
    """
    Modelo de Cuenta por Pagar.

    Registra las obligaciones de pago a proveedores por facturas recibidas.
    """
    __tablename__ = "cuentas_por_pagar"

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
    supplier_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del proveedor",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que registró la cuenta por pagar",
    )
    comprobante_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del comprobante electrónico asociado (opcional)",
    )
    orden_compra_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("ordenes_compra.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la orden de compra asociada (opcional)",
    )
    numero_factura: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de factura del proveedor",
    )
    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de emisión de la factura",
    )
    fecha_vencimiento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de vencimiento del pago",
    )
    monto_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto total de la factura",
    )
    monto_pagado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto pagado hasta la fecha",
    )
    monto_pendiente: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto pendiente de pago",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        index=True,
        comment="Estado: pendiente, parcial, pagada, vencida, anulada",
    )
    dias_credito: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Días de crédito concedidos por el proveedor",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la cuenta por pagar está activa",
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
    supplier: Mapped["Supplier"] = relationship(  # noqa: F821
        "Supplier",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="cuentas_por_pagar",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CuentaPorPagar(id={self.id}, numero_factura={self.numero_factura}, "
            f"estado={self.estado}, monto_pendiente={self.monto_pendiente})>"
        )


class RetencionCompra(Base):
    """
    Modelo de Retención en la Fuente por Compras.

    Registra las retenciones de IVA y Renta practicadas a proveedores.
    Puede generar un comprobante de retención electrónico (tipo 07).
    """
    __tablename__ = "retenciones_compra"

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
    supplier_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del proveedor",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que creó la retención",
    )
    comprobante_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del comprobante de retención electrónico (tipo 07)",
    )
    cuenta_por_pagar_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_por_pagar.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la cuenta por pagar asociada",
    )
    numero_retencion: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de la retención (ej: RET-000001)",
    )
    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de emisión de la retención",
    )
    # Retención de IVA
    base_imponible_iva: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Base imponible para retención de IVA",
    )
    retencion_iva_codigo: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Código de retención de IVA según Tabla 19 del SRI",
    )
    retencion_iva_porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Porcentaje de retención de IVA",
    )
    retencion_iva_valor: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Valor de la retención de IVA",
    )
    # Retención de Renta
    base_imponible_renta: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Base imponible para retención de Renta",
    )
    retencion_renta_codigo: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="Código de retención de Renta según Tabla 20 del SRI",
    )
    retencion_renta_porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Porcentaje de retención de Renta",
    )
    retencion_renta_valor: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Valor de la retención de Renta",
    )
    # Estado y observaciones
    estado: Mapped[str] = mapped_column(
        String(20),
        default="borrador",
        nullable=False,
        index=True,
        comment="Estado: borrador, firmado, enviado, autorizado, rechazado",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la retención está activa",
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
    supplier: Mapped["Supplier"] = relationship(  # noqa: F821
        "Supplier",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="retenciones_compra",
        lazy="selectin",
    )
    cuenta_por_pagar: Mapped["CuentaPorPagar | None"] = relationship(
        "CuentaPorPagar",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<RetencionCompra(id={self.id}, numero_retencion={self.numero_retencion}, "
            f"estado={self.estado})>"
        )
