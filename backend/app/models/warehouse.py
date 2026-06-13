"""
ContaEC - Modelos de Multi-Almacén y Logística
Warehouse: Almacenes/bodegas de la empresa
WarehouseLocation: Ubicaciones dentro de un almacén
WarehouseTransfer: Transferencias entre almacenes
WarehouseTransferDetalle: Detalle de líneas de transferencia
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TransferEstado(str, enum.Enum):
    """
    Estado de una transferencia entre almacenes.
    pendiente: Creada pero no enviada
    en_transito: Enviada al almacén destino
    recibida: Recibida en el almacén destino
    anulada: Cancelada
    """
    PENDIENTE = "pendiente"
    EN_TRANSITO = "en_transito"
    RECIBIDA = "recibida"
    ANULADA = "anulada"


class Warehouse(Base):
    """
    Modelo de Almacén/Bodega.

    Representa un almacén físico de la empresa donde se guarda inventario.
    Una empresa puede tener múltiples almacenes, uno de los cuales puede ser
    el almacén principal.
    """
    __tablename__ = "warehouses"

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
        comment="ID de la empresa a la que pertenece el almacén",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del almacén",
    )
    codigo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Código del almacén (ej: BOD-001), único por empresa",
    )
    direccion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Dirección del almacén",
    )
    ciudad: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Ciudad donde se ubica el almacén",
    )
    responsable: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Persona responsable del almacén",
    )
    telefono: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Teléfono del almacén",
    )
    is_principal: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si es el almacén principal de la empresa (solo uno por empresa)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el almacén está activo",
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
    locations: Mapped[list["WarehouseLocation"]] = relationship(
        "WarehouseLocation",
        back_populates="warehouse",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="warehouses",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Warehouse(id={self.id}, nombre={self.nombre}, "
            f"codigo={self.codigo}, is_principal={self.is_principal})>"
        )


class WarehouseLocation(Base):
    """
    Modelo de Ubicación dentro de un Almacén.

    Representa una ubicación física dentro de un almacén (zona, pasillo, rack, estante, bin).
    Puede estar asignada a un producto específico y tiene control de capacidad.
    """
    __tablename__ = "warehouse_locations"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    warehouse_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del almacén al que pertenece la ubicación",
    )
    producto_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del producto asignado a esta ubicación (opcional)",
    )
    zona: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Zona del almacén (ej: A, B, C, Refrigerados)",
    )
    pasillo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Pasillo o corredor dentro de la zona",
    )
    rack: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Rack o estante dentro del pasillo (ej: R1, R2, B)",
    )
    estante: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Nivel del rack o estante (ej: E1, E2, 2)",
    )
    nivel: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Posición dentro del estante/bin (opcional)",
    )
    codigo_ubicacion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Código de ubicación auto-generado (ej: A-P3-RB-E2)",
    )
    ubicacion_completa: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Descripción completa de la ubicación (ej: ZonaA-Pasillo3-RackB-Estante2)",
    )
    capacidad_maxima: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Capacidad máxima en unidades",
    )
    capacidad_actual: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Ocupación actual en unidades",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la ubicación está activa",
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
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse",
        back_populates="locations",
        lazy="selectin",
    )
    product: Mapped["Product | None"] = relationship(  # noqa: F821
        "Product",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<WarehouseLocation(id={self.id}, codigo={self.codigo_ubicacion}, "
            f"zona={self.zona}, rack={self.rack}, estante={self.estante})>"
        )


class WarehouseTransfer(Base):
    """
    Modelo de Transferencia entre Almacenes.

    Registra el traslado de productos de un almacén a otro
    con seguimiento de estado (pendiente → en_tránsito → recibida).
    """
    __tablename__ = "warehouse_transfers"

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
    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de transferencia (ej: TR-000001), único por empresa",
    )
    warehouse_origen_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del almacén de origen",
    )
    warehouse_destino_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID del almacén de destino",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=TransferEstado.PENDIENTE.value,
        nullable=False,
        index=True,
        comment="Estado: pendiente, en_transito, recibida, anulada",
    )
    motivo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo de la transferencia",
    )
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que creó la transferencia",
    )
    fecha_envio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que se envió la transferencia",
    )
    fecha_recepcion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que se recibió la transferencia",
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
    detalles: Mapped[list["WarehouseTransferDetalle"]] = relationship(
        "WarehouseTransferDetalle",
        back_populates="transferencia",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    warehouse_origen: Mapped["Warehouse"] = relationship(
        "Warehouse",
        foreign_keys=[warehouse_origen_id],
        lazy="selectin",
    )
    warehouse_destino: Mapped["Warehouse"] = relationship(
        "Warehouse",
        foreign_keys=[warehouse_destino_id],
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<WarehouseTransfer(id={self.id}, numero={self.numero}, "
            f"estado={self.estado})>"
        )


class WarehouseTransferDetalle(Base):
    """
    Modelo de Detalle de Transferencia entre Almacenes.

    Cada línea de la transferencia con producto, cantidad, costo
    y ubicaciones de origen y destino.
    """
    __tablename__ = "warehouse_transfer_detalles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    transferencia_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("warehouse_transfers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la transferencia",
    )
    product_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID del producto a transferir",
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Cantidad a transferir",
    )
    costo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Costo unitario del producto",
    )
    costo_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Costo total (cantidad * costo_unitario)",
    )
    ubicacion_origen_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("warehouse_locations.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID de la ubicación de origen dentro del almacén origen",
    )
    ubicacion_destino_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("warehouse_locations.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID de la ubicación de destino dentro del almacén destino",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación del registro",
    )

    # Relaciones
    transferencia: Mapped["WarehouseTransfer"] = relationship(
        "WarehouseTransfer",
        back_populates="detalles",
        lazy="selectin",
    )
    product: Mapped["Product"] = relationship(  # noqa: F821
        "Product",
        lazy="selectin",
    )
    ubicacion_origen: Mapped["WarehouseLocation | None"] = relationship(
        "WarehouseLocation",
        foreign_keys=[ubicacion_origen_id],
        lazy="selectin",
    )
    ubicacion_destino: Mapped["WarehouseLocation | None"] = relationship(
        "WarehouseLocation",
        foreign_keys=[ubicacion_destino_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<WarehouseTransferDetalle(id={self.id}, product_id={self.product_id}, "
            f"cantidad={self.cantidad})>"
        )
