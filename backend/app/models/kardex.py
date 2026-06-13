"""
ContaEC - Modelo de Kardex (Movimientos de Inventario)
Kardex: Registro de movimientos de entrada, salida y ajuste de inventario
con cálculo automático de saldos cantidades y valores
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class KardexTipoMovimiento(str, enum.Enum):
    """
    Tipo de movimiento de inventario.
    ENTRADA: Compra, devolución, ajuste positivo
    SALIDA: Venta, consumo, ajuste negativo
    AJUSTE: Ajuste de inventario (positivo o negativo)
    """
    ENTRADA = "entrada"    # Compra, devolución, ajuste+
    SALIDA = "salida"      # Venta, consumo, ajuste-
    AJUSTE = "ajuste"      # Ajuste de inventario


class Kardex(Base):
    """
    Modelo de Kardex para control de inventario.

    Registra cada movimiento de inventario con cálculo automático
    de saldos (cantidad y valor) para mantener la trazabilidad
    completa del stock de cada producto.

    Soporta métodos de valoración: FIFO, LIFO y Promedio Ponderado (PP).
    """
    __tablename__ = "kardex_movements"

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
        comment="ID de la empresa a la que pertenece el movimiento",
    )
    product_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del producto al que pertenece el movimiento",
    )
    warehouse_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del almacén asociado al movimiento (opcional)",
    )
    # Tipo de movimiento
    tipo_movimiento: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Tipo de movimiento: entrada, salida, ajuste",
    )
    # Cantidad del movimiento
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Cantidad del movimiento (positivo para entradas, positivo para salidas)",
    )
    # Costo unitario del movimiento
    costo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Costo unitario del producto en el movimiento",
    )
    # Costo total del movimiento (cantidad * costo_unitario)
    costo_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Costo total del movimiento (cantidad * costo_unitario)",
    )
    # Saldos acumulados (running balance)
    saldo_cantidad: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Saldo de cantidad acumulado después del movimiento",
    )
    saldo_valor: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Saldo de valor acumulado después del movimiento",
    )
    # Referencia al documento origen
    referencia_tipo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo de documento de referencia: comprobante, ajuste, compra, etc.",
    )
    referencia_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID del documento de referencia",
    )
    referencia_secuencial: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número secuencial del documento de referencia",
    )
    # Detalle del movimiento
    detalle: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Descripción del movimiento",
    )
    # Fecha del movimiento
    fecha_movimiento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Fecha y hora del movimiento",
    )
    # Usuario que registra el movimiento
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que registra el movimiento",
    )
    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el movimiento está activo",
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
        back_populates="kardex_movements",
        lazy="selectin",
    )
    product: Mapped["Product"] = relationship(  # noqa: F821
        "Product",
        back_populates="kardex_movements",
        lazy="selectin",
    )
    warehouse: Mapped["Warehouse | None"] = relationship(  # noqa: F821
        "Warehouse",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Kardex(id={self.id}, tipo={self.tipo_movimiento}, "
            f"cantidad={self.cantidad}, saldo_cantidad={self.saldo_cantidad})>"
        )
