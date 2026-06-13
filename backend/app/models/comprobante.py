"""
ContaEC - Modelos de Comprobante Electrónico
Comprobante: Comprobante electrónico según Ficha Técnica v2.32 del SRI
ComprobanteDetalle: Detalle de líneas del comprobante (bienes/servicios)

Incluye todos los campos requeridos por el SRI para la generación
de XML, firma digital, envío y autorización de comprobantes electrónicos.
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ComprobanteEstado(str, enum.Enum):
    """
    Estado del comprobante electrónico en el ciclo de vida.
    Según los estados definidos por el SRI y el flujo de ContaEC.
    """
    BORRADOR = "borrador"            # Borrador - aún no enviado al SRI
    FIRMADO = "firmado"              # Firmado con firma digital, aún no enviado
    ENVIADO = "enviado"              # Enviado al SRI, pendiente de respuesta
    AUTORIZADO = "autorizado"        # Autorizado por el SRI
    RECHAZADO = "rechazado"          # Rechazado por el SRI
    DEVUELTA = "devuelta"            # Devuelto por el SRI para corrección
    CADUCADA = "caducada"            # Comprobante caducado (excedió tiempo de autorización)
    CONTINGENCIA = "contingencia"    # Modo contingencia fuera de línea
    ANULADO = "anulado"             # Anulado por el emisor


class ComprobanteTipo(str, enum.Enum):
    """
    Tipo de comprobante electrónico según Tabla 1 del SRI.
    Código de tipo de documento electrónico.
    """
    FACTURA = "01"                       # Factura
    NOTA_VENTA = "02"                    # Nota de Venta (emitida por sujetos no obligados a emitir comprobante)
    LIQUIDACION_COMPRA = "03"            # Liquidación de Compra de Bienes y Prestación de Servicios
    NOTA_CREDITO = "04"                  # Nota de Crédito
    NOTA_DEBITO = "05"                   # Nota de Débito
    GUIA_REMISION = "06"                 # Guía de Remisión
    COMPROBANTE_RETENCION = "07"         # Comprobante de Retención
    PROFORMA = "08"                      # Proforma (documento interno, no enviado al SRI)


class Comprobante(Base):
    """
    Modelo de Comprobante Electrónico según Ficha Técnica v2.32 del SRI.

    Contiene toda la información requerida para la generación del XML,
    firma digital, envío al SRI y obtención de la autorización.

    Incluye:
    - Identificación del comprobante (tipo, secuencial, clave de acceso)
    - Información del comprador (desnormalizada para XML del SRI)
    - Totales desglosados por tarifa de IVA
    - Retenciones de IVA y Renta
    - Referencia a comprobante modificado (notas de crédito/débito)
    - XML firmado y respuestas del SRI
    - Información adicional (campo libre del SRI)
    """
    __tablename__ = "comprobantes"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    # Llaves foráneas
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa emisora del comprobante",
    )
    client_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del cliente/comprador del comprobante",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que creó el comprobante",
    )

    # === Identificación del Comprobante ===
    tipo_comprobante: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
        comment="Código de tipo de comprobante según Tabla 1 del SRI (01, 03, 04, 05, 06, 07)",
    )
    secuencial: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
        comment="Número secuencial del comprobante (9 dígitos, rellenado con ceros)",
    )
    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha y hora de emisión del comprobante",
    )
    clave_acceso: Mapped[str | None] = mapped_column(
        String(49),
        nullable=True,
        unique=True,
        index=True,
        comment="Clave de acceso del SRI (49 dígitos)",
    )
    numero_autorizacion: Mapped[str | None] = mapped_column(
        String(49),
        nullable=True,
        comment="Número de autorización emitido por el SRI",
    )
    fecha_autorizacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de autorización por el SRI",
    )

    # === Estado ===
    estado: Mapped[str] = mapped_column(
        String(20),
        default=ComprobanteEstado.BORRADOR,
        nullable=False,
        index=True,
        comment="Estado actual del comprobante (borrador/firmado/enviado/autorizado/rechazado/contingencia)",
    )
    ambiente: Mapped[str] = mapped_column(
        String(1),
        default="1",
        nullable=False,
        comment="Tipo de ambiente: 1=Pruebas, 2=Producción",
    )
    tipo_emision: Mapped[str] = mapped_column(
        String(1),
        default="1",
        nullable=False,
        comment="Tipo de emisión: 1=Normal, 2=Contingencia",
    )

    # === Información del Comprador (desnormalizada para XML del SRI) ===
    cliente_tipo_identificacion: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
        comment="Tipo de identificación del comprador según Tabla 7 del SRI",
    )
    cliente_identificacion: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de identificación del comprador",
    )
    cliente_razon_social: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Razón social o nombre del comprador",
    )
    cliente_direccion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Dirección del comprador",
    )
    cliente_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Correo electrónico del comprador",
    )
    cliente_telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de teléfono del comprador",
    )

    # === Totales ===
    subtotal_sin_impuestos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Subtotal sin impuestos",
    )
    subtotal_iva_0: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA 0%",
    )
    subtotal_iva_5: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA 5%",
    )
    subtotal_iva_8: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA 8%",
    )
    subtotal_iva_12: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA 12% (tarifa anterior hasta 31/12/2023)",
    )
    subtotal_iva_13: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA 13% (tarifa vigente desde 01/01/2024)",
    )
    subtotal_iva_14: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA 14% (período transitorio)",
    )
    subtotal_iva_15: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA 15% (período transitorio)",
    )
    subtotal_no_objeto_iva: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal no objeto de IVA",
    )
    subtotal_exento_iva: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal exento de IVA",
    )
    subtotal_iva_diferenciado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Subtotal con IVA diferenciado (código 9 - Tabla 16 SRI)",
    )
    total_iva: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total del IVA",
    )
    total_ice: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total del ICE",
    )
    total_descuento: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de descuentos",
    )
    total_con_impuestos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Total con impuestos (gran total)",
    )

    # === Forma de Pago ===
    forma_pago: Mapped[str] = mapped_column(
        String(2),
        default="01",
        nullable=False,
        comment="Código de forma de pago según Tabla 23 del SRI",
    )
    moneda: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
        comment="Moneda del comprobante (USD por defecto)",
    )

    # === Retenciones ===
    retencion_iva_codigo: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
        comment="Código de retención de IVA según Tabla 19 del SRI",
    )
    retencion_iva_porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje de retención de IVA",
    )
    retencion_iva_valor: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment="Valor de la retención de IVA",
    )
    retencion_renta_codigo: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
        comment="Código de retención de Renta según Tabla 20 del SRI",
    )
    retencion_renta_porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje de retención de Renta",
    )
    retencion_renta_valor: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment="Valor de la retención de Renta",
    )

    # === Notas de Crédito/Débito ===
    comprobante_modificado_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del comprobante que se modifica (para notas de crédito/débito)",
    )
    motivo_modificacion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo de la modificación del comprobante",
    )
    fecha_emision_documento_sustento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de emisión del documento sustento (comprobante modificado)",
    )

    # === XML y Respuesta SRI ===
    xml_content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Contenido XML firmado enviado al SRI",
    )
    xml_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Ruta del archivo XML guardado",
    )
    sri_mensaje: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Mensaje de respuesta del SRI",
    )
    sri_mensaje_detallado: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Mensajes de error detallados del SRI (JSON)",
    )

    # === Info Adicional (campo libre SRI) ===
    info_adicional: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Información adicional en formato JSON con pares clave-valor para campoAdicional del SRI",
    )

    # === RIDE (Representación Impresa del Documento Electrónico) ===
    ride_pdf_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Ruta del archivo PDF del RIDE generado",
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el comprobante está activo",
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
        back_populates="comprobantes",
        lazy="selectin",
    )
    client: Mapped["Client | None"] = relationship(  # noqa: F821
        "Client",
        back_populates="comprobantes",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="comprobantes",
        lazy="selectin",
    )
    detalles: Mapped[list["ComprobanteDetalle"]] = relationship(
        "ComprobanteDetalle",
        back_populates="comprobante",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    comprobante_modificado: Mapped["Comprobante | None"] = relationship(
        "Comprobante",
        remote_side="Comprobante.id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Comprobante(id={self.id}, tipo={self.tipo_comprobante}, "
            f"secuencial={self.secuencial}, estado={self.estado})>"
        )

    @property
    def numero_comprobante(self) -> str:
        """
        Retorna el número completo del comprobante con formato:
        {cod_establecimiento}-{cod_punto_emision}-{secuencial}
        Requiere acceso a la empresa para los códigos de establecimiento.
        """
        # Nota: los códigos de establecimiento vienen de la empresa
        return self.secuencial

    @property
    def is_autorizado(self) -> bool:
        """Indica si el comprobante fue autorizado por el SRI"""
        return self.estado == ComprobanteEstado.AUTORIZADO

    @property
    def is_modificable(self) -> bool:
        """Indica si el comprobante aún puede ser modificado (solo en estado borrador)"""
        return self.estado == ComprobanteEstado.BORRADOR


class ComprobanteDetalle(Base):
    """
    Modelo de Detalle del Comprobante Electrónico.

    Cada línea del comprobante representa un bien o servicio con su
    cantidad, precio, descuentos e impuestos aplicables (IVA e ICE).
    Los datos están desnormalizados para facilitar la generación del XML del SRI.
    """
    __tablename__ = "comprobante_detalles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    comprobante_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del comprobante al que pertenece el detalle",
    )
    product_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del producto (nullable, puede ser un ítem ad-hoc)",
    )

    # === Detalle del bien/servicio ===
    codigo_principal: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código principal del bien o servicio",
    )
    codigo_auxiliar: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Código auxiliar del bien o servicio",
    )
    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Descripción del bien o servicio",
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Cantidad del bien o servicio (hasta 4 decimales)",
    )
    unidad_medida: Mapped[str] = mapped_column(
        String(50),
        default="Unidad",
        nullable=False,
        comment="Unidad de medida del bien o servicio",
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Precio unitario del bien o servicio (sin impuestos)",
    )
    descuento: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto de descuento aplicado al detalle",
    )
    precio_total_sin_impuestos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Precio total sin impuestos (cantidad * precio_unitario - descuento)",
    )

    # === Impuestos del detalle ===
    iva_codigo: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Código de tarifa de IVA según Tabla 16 del SRI",
    )
    iva_porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Porcentaje de IVA aplicado al detalle",
    )
    iva_valor: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Valor del IVA calculado para este detalle",
    )
    ice_codigo: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
        comment="Código de tarifa de ICE según Tabla 18 del SRI",
    )
    ice_porcentaje: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje de ICE aplicado al detalle",
    )
    ice_valor: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        default=Decimal("0"),
        comment="Valor del ICE calculado para este detalle",
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
    comprobante: Mapped["Comprobante"] = relationship(
        "Comprobante",
        back_populates="detalles",
        lazy="selectin",
    )
    product: Mapped["Product | None"] = relationship(  # noqa: F821
        "Product",
        back_populates="detalles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ComprobanteDetalle(id={self.id}, comprobante_id={self.comprobante_id}, "
            f"descripcion={self.descripcion}, cantidad={self.cantidad})>"
        )
