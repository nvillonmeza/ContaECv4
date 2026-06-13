"""
ContaEC - Modelos de Integraciones
Integracion bancaria (extractos) y conectores e-commerce
"""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ========================================
# Integracion Bancaria
# ========================================

class BancoTipoCuenta(str, Enum):
    """Tipo de cuenta bancaria"""
    AHORROS = "ahorros"
    CORRIENTE = "corriente"


class ExtractoEstado(str, Enum):
    """Estado del extracto bancario"""
    IMPORTADO = "importado"
    EN_CONCILIACION = "en_conciliacion"
    CONCILIADO = "conciliado"
    CON_ERROR = "con_error"


class MovimientoTipo(str, Enum):
    """Tipo de movimiento bancario"""
    DEBITO = "debito"
    CREDITO = "credito"


class ConciliacionEstado(str, Enum):
    """Estado de la conciliacion bancaria"""
    PENDIENTE = "pendiente"
    CONCILIADO = "conciliado"
    IGNORADO = "ignorado"


class CuentaBancaria(Base):
    """
    Modelo de Cuenta Bancaria.
    Registra las cuentas bancarias de la empresa para importar
    extractos y realizar conciliaciones automaticas.
    """
    __tablename__ = "cuentas_bancarias"

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
    nombre_banco: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del banco (ej: Banco Pichincha, Banco Guayaquil)",
    )
    codigo_banco: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Codigo del banco segun SRI",
    )
    tipo_cuenta: Mapped[str] = mapped_column(
        String(20),
        default=BancoTipoCuenta.CORRIENTE.value,
        nullable=False,
        comment="Tipo de cuenta: ahorros, corriente",
    )
    numero_cuenta: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Numero de cuenta bancaria",
    )
    iban: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="IBAN de la cuenta",
    )
    titular: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del titular de la cuenta",
    )
    moneda: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
        comment="Moneda de la cuenta (USD para Ecuador)",
    )
    saldo_inicial: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Saldo inicial de la cuenta",
    )
    saldo_actual: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Saldo actual calculado",
    )
    ultima_fecha_sincronizacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Ultima fecha de sincronizacion de extractos",
    )
    formato_extracto: Mapped[str] = mapped_column(
        String(20),
        default="csv",
        nullable=False,
        comment="Formato del extracto: csv, ofx, mt940, excel",
    )
    configuracion_mapeo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con configuracion de mapeo de columnas del extracto",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la cuenta esta activa",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="cuentas_bancarias",
        lazy="selectin",
    )
    extractos: Mapped[list["ExtractoBancario"]] = relationship(
        "ExtractoBancario",
        back_populates="cuenta_bancaria",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    movimientos: Mapped[list["MovimientoBancario"]] = relationship(
        "MovimientoBancario",
        back_populates="cuenta_bancaria",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<CuentaBancaria(id={self.id}, banco={self.nombre_banco}, "
            f"cuenta={self.numero_cuenta})>"
        )


class ExtractoBancario(Base):
    """
    Modelo de Extracto Bancario.
    Registra cada importacion de extracto bancario con su periodo
    y estado de conciliacion.
    """
    __tablename__ = "extractos_bancarios"

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
    cuenta_bancaria_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_bancarias.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la cuenta bancaria",
    )
    fecha_desde: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha inicio del periodo del extracto",
    )
    fecha_hasta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha fin del periodo del extracto",
    )
    saldo_inicial: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Saldo inicial segun extracto",
    )
    saldo_final: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Saldo final segun extracto",
    )
    total_debitos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de debitos en el periodo",
    )
    total_creditos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de creditos en el periodo",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=ExtractoEstado.IMPORTADO.value,
        nullable=False,
        index=True,
        comment="Estado: importado, en_conciliacion, conciliado, con_error",
    )
    numero_movimientos: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Numero de movimientos importados",
    )
    movimientos_conciliados: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Numero de movimientos conciliados",
    )
    archivo_original: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Nombre del archivo original del extracto",
    )
    notas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionales del extracto",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    cuenta_bancaria: Mapped["CuentaBancaria"] = relationship(
        "CuentaBancaria",
        back_populates="extractos",
        lazy="selectin",
    )
    movimientos: Mapped[list["MovimientoBancario"]] = relationship(
        "MovimientoBancario",
        back_populates="extracto",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ExtractoBancario(id={self.id}, cuenta={self.cuenta_bancaria_id}, "
            f"periodo={self.fecha_desde} a {self.fecha_hasta})>"
        )


class MovimientoBancario(Base):
    """
    Modelo de Movimiento Bancario.
    Cada transaccion dentro de un extracto bancario con datos para
    conciliacion automatica y manual.
    """
    __tablename__ = "movimientos_bancarios"

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
    )
    cuenta_bancaria_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_bancarias.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    extracto_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("extractos_bancarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Fecha del movimiento",
    )
    tipo: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Tipo: debito, credito",
    )
    monto: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto del movimiento (siempre positivo)",
    )
    saldo_posterior: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment="Saldo despues del movimiento",
    )
    referencia: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Numero de referencia del movimiento",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripcion del movimiento segun el banco",
    )
    beneficiario: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nombre del beneficiario o originante",
    )
    documento: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Numero de documento (cheque, transferencia, etc.)",
    )
    conciliacion_estado: Mapped[str] = mapped_column(
        String(20),
        default=ConciliacionEstado.PENDIENTE.value,
        nullable=False,
        index=True,
        comment="Estado conciliacion: pendiente, conciliado, ignorado",
    )
    conciliacion_fecha: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que se concilio el movimiento",
    )
    comprobante_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del comprobante conciliado",
    )
    conciliacion_nota: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Nota de conciliacion",
    )
    categoria: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Categoria auto-detectada del movimiento",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    cuenta_bancaria: Mapped["CuentaBancaria"] = relationship(
        "CuentaBancaria",
        back_populates="movimientos",
        lazy="selectin",
    )
    extracto: Mapped["ExtractoBancario"] = relationship(
        "ExtractoBancario",
        back_populates="movimientos",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MovimientoBancario(id={self.id}, fecha={self.fecha}, "
            f"tipo={self.tipo}, monto={self.monto})>"
        )


# ========================================
# Conectores E-Commerce
# ========================================

class EcommercePlataforma(str, Enum):
    """Plataformas e-commerce soportadas"""
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    OPENCART = "opencart"
    PRESTASHOP = "prestashop"
    MAGENTO = "magento"
    MELI = "meli"  # Mercado Libre
    OTRO = "otro"


class ConnectorEstado(str, Enum):
    """Estado del conector e-commerce"""
    CONFIGURADO = "configurado"
    CONECTADO = "conectado"
    SINCRONIZANDO = "sincronizando"
    ERROR = "error"
    DESACTIVADO = "desactivado"


class SyncEstado(str, Enum):
    """Estado de una sincronizacion"""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CON_ERROR = "con_error"


class EcommerceConnector(Base):
    """
    Modelo de Conector E-Commerce.
    Configura la conexion con plataformas de comercio electronico
    para sincronizar productos, ordenes y clientes.
    """
    __tablename__ = "ecommerce_connectors"

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
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que creo el conector",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre descriptivo del conector",
    )
    plataforma: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Plataforma: shopify, woocommerce, opencart, prestashop, magento, meli, otro",
    )
    url_tienda: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="URL de la tienda e-commerce",
    )
    api_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="API Key / Token de acceso",
    )
    api_secret: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="API Secret (encriptado)",
    )
    access_token: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="Token de acceso OAuth (si aplica)",
    )
    refresh_token: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="Token de refresco OAuth (si aplica)",
    )
    webhook_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL del webhook configurado en la plataforma",
    )
    configuracion_extra: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con configuracion adicional especifica de la plataforma",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=ConnectorEstado.CONFIGURADO.value,
        nullable=False,
        index=True,
        comment="Estado: configurado, conectado, sincronizando, error, desactivado",
    )
    ultimo_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Ultimo mensaje de error",
    )
    ultima_sincronizacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de la ultima sincronizacion exitosa",
    )
    sincronizacion_auto: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si la sincronizacion es automatica",
    )
    frecuencia_sync: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
        comment="Frecuencia de sincronizacion automatica en minutos",
    )
    sync_productos: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Sincronizar productos",
    )
    sync_ordenes: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Sincronizar ordenes/pedidos",
    )
    sync_clientes: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Sincronizar clientes",
    )
    sync_inventario: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Sincronizar inventario/stock",
    )
    total_ordenes_sync: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total de ordenes sincronizadas",
    )
    total_productos_sync: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total de productos sincronizados",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="ecommerce_connectors",
        lazy="selectin",
    )
    sincronizaciones: Mapped[list["EcommerceSyncLog"]] = relationship(
        "EcommerceSyncLog",
        back_populates="connector",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<EcommerceConnector(id={self.id}, nombre={self.nombre}, "
            f"plataforma={self.plataforma}, estado={self.estado})>"
        )


class EcommerceSyncLog(Base):
    """
    Modelo de Log de Sincronizacion E-Commerce.
    Registra cada operacion de sincronizacion con sus resultados,
    errores y estadisticas para auditoria y seguimiento.
    """
    __tablename__ = "ecommerce_sync_logs"

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
    )
    connector_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("ecommerce_connectors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del conector",
    )
    tipo_sync: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Tipo: productos, ordenes, clientes, inventario, completo",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=SyncEstado.PENDIENTE.value,
        nullable=False,
        comment="Estado: pendiente, en_progreso, completada, con_error",
    )
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    fecha_fin: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    registros_procesados: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    registros_creados: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    registros_actualizados: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    registros_errores: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    detalle_errores: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con detalles de errores",
    )
    resultado_resumen: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con resumen de la sincronizacion",
    )
    creado_por: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID del usuario que inicio la sync (null = automatica)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    connector: Mapped["EcommerceConnector"] = relationship(
        "EcommerceConnector",
        back_populates="sincronizaciones",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<EcommerceSyncLog(id={self.id}, tipo={self.tipo_sync}, "
            f"estado={self.estado})>"
        )
