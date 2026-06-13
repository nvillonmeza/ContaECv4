"""
ContaEC - Modelos Contables Core
Plan de Cuentas, Asientos Contables, Cuentas por Cobrar, Pagos, Períodos Fiscales

Estos modelos conforman el núcleo contable del sistema, implementando:
- Plan de Cuentas (Catálogo con código, nombre, tipo)
- Asientos Contables con partida doble (débito/crédito)
- Cuentas por Cobrar con envejecimiento de cartera
- Pagos/Cobros con historial
- Períodos Fiscales con cierre contable
"""
import enum
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ==========================================
# Enums
# ==========================================

class TipoCuentaContable(str, enum.Enum):
    """Tipo de cuenta contable según el Plan General Contable ecuatoriano"""
    ACTIVO = "activo"
    PASIVO = "pasivo"
    PATRIMONIO = "patrimonio"
    INGRESO = "ingreso"
    GASTO = "gasto"
    COSTO = "costo"


class NaturalezaCuenta(str, enum.Enum):
    """Naturaleza de la cuenta: Deudora o Acreedora"""
    DEUDORA = "deudora"      # Saldo aumenta con débito (Activos, Gastos, Costos)
    ACREEDORA = "acreedora"  # Saldo aumenta con crédito (Pasivos, Patrimonio, Ingresos)


class AsientoEstado(str, enum.Enum):
    """Estado del asiento contable"""
    BORRADOR = "borrador"
    APROBADO = "aprobado"
    ANULADO = "anulado"


class TipoAsiento(str, enum.Enum):
    """Tipo de asiento contable"""
    APERTURA = "apertura"              # Asiento de apertura
    ORDINARIO = "ordinario"            # Asiento diario normal
    CIERRE = "cierre"                  # Asiento de cierre
    AJUSTE = "ajuste"                  # Asiento de ajuste
    ESTIMACION = "estimacion"          # Asiento de estimación
    RECLASIFICACION = "reclasificacion"  # Asiento de reclasificación


class CuentaPorCobrarEstado(str, enum.Enum):
    """Estado de la cuenta por cobrar"""
    PENDIENTE = "pendiente"
    PARCIALMENTE_PAGADA = "parcialmente_pagada"
    PAGADA = "pagada"
    VENCIDA = "vencida"
    EN_COBRANZA = "en_cobranza"
    INCOBRABLE = "incobrable"


class PagoTipo(str, enum.Enum):
    """Tipo de pago/cobro"""
    COBRO = "cobro"        # Cobro a cliente (CxC)
    PAGO = "pago"          # Pago a proveedor (CxP)
    OTRO = "otro"          # Otro tipo de pago


class PagoEstado(str, enum.Enum):
    """Estado del pago"""
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    ANULADO = "anulado"


class PeriodoFiscalEstado(str, enum.Enum):
    """Estado del período fiscal"""
    ABIERTO = "abierto"
    CERRADO = "cerrado"
    EN_CIERRE = "en_cierre"


# ==========================================
# Plan de Cuentas
# ==========================================

class CuentaContable(Base):
    """
    Plan de Cuentas Contable.

    Catálogo de cuentas con estructura jerárquica por código.
    Siguiendo el Plan General Contable ecuatoriano:
      1xxx = Activos
      2xxx = Pasivos
      3xxx = Patrimonio
      4xxx = Ingresos
      5xxx = Gastos
      6xxx = Costos

    Las cuentas pueden ser de movimiento (aceptan asientos) o
    de agrupación (solo agrupan cuentas hijas).
    """
    __tablename__ = "cuentas_contables"

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
        comment="ID de la empresa a la que pertenece la cuenta",
    )
    codigo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Código de la cuenta contable (ej: 1.1.01.01)",
    )
    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nombre de la cuenta contable",
    )
    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Tipo de cuenta: activo, pasivo, patrimonio, ingreso, gasto, costo",
    )
    naturaleza: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Naturaleza de la cuenta: deudora o acreedora",
    )
    nivel: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Nivel jerárquico de la cuenta (1=grupo, 2=subgrupo, etc.)",
    )
    cuenta_padre_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_contables.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID de la cuenta padre (para jerarquía)",
    )
    es_cuenta_movimiento: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si es True, acepta asientos; si False, es solo agrupación",
    )
    es_imputable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si es True, se puede imputar directamente en asientos",
    )
    saldo_inicial: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Saldo inicial de la cuenta al inicio del período",
    )
    saldo_actual: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Saldo actual de la cuenta",
    )
    total_debitos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de débitos acumulados",
    )
    total_creditos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de créditos acumulados",
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción detallada de la cuenta",
    )
    etiqueta: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Etiqueta para clasificación especial (ej: banco, caja, clientes, IVA)",
    )
    # Cuenta contable vinculada para automatización
    cuenta_contrapartida_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_contables.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID de la cuenta de contrapartida automática",
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
        back_populates="cuentas_contables",
        lazy="selectin",
    )
    cuenta_padre: Mapped["CuentaContable | None"] = relationship(
        "CuentaContable",
        remote_side="CuentaContable.id",
        foreign_keys=[cuenta_padre_id],
        lazy="selectin",
    )
    cuentas_hijas: Mapped[list["CuentaContable"]] = relationship(
        "CuentaContable",
        back_populates="cuenta_padre",
        lazy="selectin",
        foreign_keys=[cuenta_padre_id],
    )
    cuenta_contrapartida: Mapped["CuentaContable | None"] = relationship(
        "CuentaContable",
        remote_side="CuentaContable.id",
        foreign_keys=[cuenta_contrapartida_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CuentaContable(codigo={self.codigo}, nombre={self.nombre}, tipo={self.tipo})>"

    @property
    def codigo_nombre(self) -> str:
        return f"{self.codigo} - {self.nombre}"


# ==========================================
# Asientos Contables (Partidas Diarias)
# ==========================================

class AsientoContable(Base):
    """
    Asiento Contable / Partida Diaria.

    Implementa el sistema de partida doble donde cada asiento
    debe tener al menos un débito y un crédito, y la suma de
    débitos debe ser igual a la suma de créditos.

    Los asientos pueden generarse manualmente o automáticamente
    desde comprobantes electrónicos, roles de pago, etc.
    """
    __tablename__ = "asientos_contables"

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
        comment="ID del usuario que creó el asiento",
    )
    periodo_fiscal_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("periodos_fiscales.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del período fiscal al que pertenece el asiento",
    )
    # === Identificación ===
    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de asiento (AS-XXXXXX)",
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Fecha del asiento contable",
    )
    tipo: Mapped[str] = mapped_column(
        String(20),
        default=TipoAsiento.ORDINARIO,
        nullable=False,
        comment="Tipo de asiento: apertura, ordinario, cierre, ajuste, estimacion, reclasificacion",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=AsientoEstado.BORRADOR,
        nullable=False,
        index=True,
        comment="Estado del asiento: borrador, aprobado, anulado",
    )
    # === Totales ===
    total_debitos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Suma total de débitos del asiento",
    )
    total_creditos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Suma total de créditos del asiento",
    )
    # === Referencia al documento origen ===
    concepto: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Concepto o descripción del asiento",
    )
    referencia_tipo: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="Tipo de documento origen (comprobante, rol_pago, etc.)",
    )
    referencia_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID del documento origen",
    )
    referencia_secuencial: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Secuencial del documento origen",
    )
    # === Observaciones ===
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales del asiento",
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
        back_populates="asientos_contables",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )
    periodo_fiscal: Mapped["PeriodoFiscal | None"] = relationship(
        "PeriodoFiscal",
        back_populates="asientos",
        lazy="selectin",
    )
    detalles: Mapped[list["AsientoDetalle"]] = relationship(
        "AsientoDetalle",
        back_populates="asiento",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AsientoContable(numero={self.numero}, fecha={self.fecha}, estado={self.estado})>"

    @property
    def is_cuadrado(self) -> bool:
        """Indica si el asiento está cuadrado (débitos = créditos)"""
        return self.total_debitos == self.total_creditos


class AsientoDetalle(Base):
    """
    Detalle del Asiento Contable (línea de débito o crédito).

    Cada detalle referencia una cuenta contable y registra
    un movimiento de débito o crédito sobre la misma.
    """
    __tablename__ = "asiento_detalles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    asiento_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("asientos_contables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del asiento contable al que pertenece",
    )
    cuenta_contable_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_contables.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID de la cuenta contable afectada",
    )
    # === Movimiento ===
    debito: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto del débito (0 si es crédito)",
    )
    credito: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto del crédito (0 si es débito)",
    )
    # === Descripción ===
    descripcion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Descripción del movimiento",
    )
    # === Referencia al documento origen específico ===
    referencia_tipo: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="Tipo de documento origen específico",
    )
    referencia_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID del documento origen específico",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    asiento: Mapped["AsientoContable"] = relationship(
        "AsientoContable",
        back_populates="detalles",
        lazy="selectin",
    )
    cuenta_contable: Mapped["CuentaContable"] = relationship(
        "CuentaContable",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        mov = "D" if self.debito > 0 else "C"
        monto = self.debito if self.debito > 0 else self.credito
        return f"<AsientoDetalle(cuenta={self.cuenta_contable_id}, {mov}={monto})>"


# ==========================================
# Cuentas por Cobrar
# ==========================================

class CuentaPorCobrar(Base):
    """
    Cuentas por Cobrar.

    Registro de montos pendientes de cobro por parte de clientes.
    Se genera automáticamente al autorizar una factura electrónica
    o manualmente para otros conceptos.
    """
    __tablename__ = "cuentas_por_cobrar"

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
    client_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del cliente deudor",
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
        comment="ID del usuario que registró la CxC",
    )
    comprobante_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del comprobante electrónico asociado",
    )
    asiento_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("asientos_contables.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del asiento contable asociado",
    )
    # === Información de la CxC ===
    numero_factura: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de factura/comprobante",
    )
    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de emisión del documento",
    )
    fecha_vencimiento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Fecha de vencimiento del cobro",
    )
    # === Montos ===
    monto_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto total de la cuenta por cobrar",
    )
    monto_pagado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Monto total pagado/cobrado",
    )
    monto_pendiente: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto pendiente de cobro",
    )
    # === Estado ===
    estado: Mapped[str] = mapped_column(
        String(25),
        default=CuentaPorCobrarEstado.PENDIENTE,
        nullable=False,
        index=True,
        comment="Estado de la CxC",
    )
    dias_credito: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        comment="Días de crédito concedidos al cliente",
    )
    # === Envejecimiento de cartera ===
    dias_vencida: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Días de vencimiento (calculado respecto a fecha_vencimiento)",
    )
    # === Cliente desnormalizado ===
    cliente_nombre: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nombre del cliente (desnormalizado para consulta rápida)",
    )
    cliente_identificacion: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Identificación del cliente",
    )
    # === Observaciones ===
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones adicionales",
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
        back_populates="cuentas_por_cobrar",
        lazy="selectin",
    )
    client: Mapped["Client | None"] = relationship(  # noqa: F821
        "Client",
        lazy="selectin",
    )
    comprobante: Mapped["Comprobante | None"] = relationship(  # noqa: F821
        "Comprobante",
        lazy="selectin",
    )
    asiento: Mapped["AsientoContable | None"] = relationship(
        "AsientoContable",
        lazy="selectin",
    )
    pagos: Mapped[list["Pago"]] = relationship(
        "Pago",
        back_populates="cuenta_por_cobrar",
        lazy="selectin",
        foreign_keys="Pago.cuenta_por_cobrar_id",
    )

    def __repr__(self) -> str:
        return f"<CuentaPorCobrar(id={self.id}, monto={self.monto_total}, pendiente={self.monto_pendiente})>"

    @property
    def rango_vencimiento(self) -> str:
        """Clasificación por rango de envejecimiento"""
        if self.dias_vencida <= 0:
            return "vigente"
        elif self.dias_vencida <= 30:
            return "1-30 dias"
        elif self.dias_vencida <= 60:
            return "31-60 dias"
        elif self.dias_vencida <= 90:
            return "61-90 dias"
        elif self.dias_vencida <= 180:
            return "91-180 dias"
        else:
            return "mas de 180 dias"


# ==========================================
# Pagos / Cobros
# ==========================================

class Pago(Base):
    """
    Modelo de Pago / Cobro.

    Registra los pagos realizados (a proveedores) y los cobros
    recibidos (de clientes), con historial completo.
    """
    __tablename__ = "pagos"

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
        comment="ID del usuario que registró el pago",
    )
    # === Referencia a CxC o CxP ===
    cuenta_por_cobrar_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_por_cobrar.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la CxC asociada (si es cobro)",
    )
    cuenta_por_pagar_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_por_pagar.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la CxP asociada (si es pago)",
    )
    # === Asiento contable generado ===
    asiento_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("asientos_contables.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del asiento contable generado por este pago",
    )
    # === Información del pago ===
    tipo: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Tipo: cobro, pago, otro",
    )
    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de comprobante de pago/cobro",
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Fecha del pago/cobro",
    )
    monto: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="Monto del pago/cobro",
    )
    # === Forma de pago ===
    forma_pago: Mapped[str] = mapped_column(
        String(2),
        default="01",
        nullable=False,
        comment="Código de forma de pago según Tabla 23 del SRI",
    )
    referencia: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Número de referencia (cheque, transferencia, etc.)",
    )
    # === Cuenta bancaria ===
    cuenta_bancaria_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("cuentas_bancarias.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID de la cuenta bancaria utilizada",
    )
    # === Tercero ===
    tercero_nombre: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nombre del tercero (cliente/proveedor)",
    )
    tercero_identificacion: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Identificación del tercero",
    )
    # === Estado ===
    estado: Mapped[str] = mapped_column(
        String(15),
        default=PagoEstado.PENDIENTE,
        nullable=False,
        index=True,
        comment="Estado del pago: pendiente, confirmado, anulado",
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
        back_populates="pagos",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )
    cuenta_por_cobrar: Mapped["CuentaPorCobrar | None"] = relationship(
        "CuentaPorCobrar",
        back_populates="pagos",
        lazy="selectin",
        foreign_keys=[cuenta_por_cobrar_id],
    )
    cuenta_por_pagar: Mapped["CuentaPorPagar | None"] = relationship(  # noqa: F821
        "CuentaPorPagar",
        lazy="selectin",
        foreign_keys=[cuenta_por_pagar_id],
    )
    asiento: Mapped["AsientoContable | None"] = relationship(
        "AsientoContable",
        lazy="selectin",
    )
    cuenta_bancaria: Mapped["CuentaBancaria | None"] = relationship(  # noqa: F821
        "CuentaBancaria",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Pago(numero={self.numero}, tipo={self.tipo}, monto={self.monto})>"


# ==========================================
# Períodos Fiscales
# ==========================================

class PeriodoFiscal(Base):
    """
    Período Fiscal / Contable.

    Permite gestionar los períodos contables y controlar
    el cierre de los mismos. Una vez cerrado un período,
    no se pueden crear o modificar asientos contables
    en ese período.
    """
    __tablename__ = "periodos_fiscales"

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
        comment="ID del usuario que creó/cerró el período",
    )
    # === Identificación del período ===
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre del período (ej: Enero 2025, Q1 2025, Anual 2025)",
    )
    anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Año fiscal",
    )
    mes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Mes del período (1-12, None para períodos anuales)",
    )
    tipo_periodo: Mapped[str] = mapped_column(
        String(20),
        default="mensual",
        nullable=False,
        comment="Tipo de período: mensual, trimestral, semestral, anual",
    )
    # === Fechas ===
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de inicio del período",
    )
    fecha_fin: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de fin del período",
    )
    # === Estado ===
    estado: Mapped[str] = mapped_column(
        String(15),
        default=PeriodoFiscalEstado.ABIERTO,
        nullable=False,
        index=True,
        comment="Estado del período: abierto, cerrado, en_cierre",
    )
    # === Información de cierre ===
    fecha_cierre: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que se cerró el período",
    )
    cerrado_por: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID del usuario que cerró el período",
    )
    # === Totales del período ===
    total_debitos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de débitos del período",
    )
    total_creditos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Total de créditos del período",
    )
    total_asientos: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de asientos contables en el período",
    )
    # === Observaciones ===
    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observaciones sobre el cierre del período",
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
        back_populates="periodos_fiscales",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )
    asientos: Mapped[list["AsientoContable"]] = relationship(
        "AsientoContable",
        back_populates="periodo_fiscal",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<PeriodoFiscal(nombre={self.nombre}, estado={self.estado})>"

    @property
    def is_cerrado(self) -> bool:
        return self.estado == PeriodoFiscalEstado.CERRADO

    @property
    def is_en_cierre(self) -> bool:
        return self.estado == PeriodoFiscalEstado.EN_CIERRE
