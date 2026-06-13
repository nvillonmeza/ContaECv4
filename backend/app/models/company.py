"""
ContaEC - Modelos de Empresa y Establecimiento
Company: Información fiscal de la empresa (RUC, razón social, etc.)
Establishment: Establecimientos/sucursales de la empresa
"""
import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoAmbiente(str, enum.Enum):
    """Tipo de ambiente para facturación electrónica del SRI"""
    PRUEBAS = "1"       # Pruebas
    PRODUCCION = "2"    # Producción


class TipoEmision(str, enum.Enum):
    """Tipo de emisión de comprobantes electrónicos"""
    NORMAL = "1"        # Emisión normal
    CONTINGENCIA = "2"  # Emisión en contingencia (cuando el SRI está fuera de línea)


class ObligadoContabilidad(str, enum.Enum):
    """Obligación de llevar contabilidad"""
    SI = "SI"
    NO = "NO"


class ContribuyenteRimpe(str, enum.Enum):
    """Tipos de contribuyente RIMPE y regímenes fiscales"""
    RIMPE_EMPRENDEDOR = "RIMPE Emprendedor"
    RIMPE_NEGOCIO_POPULAR = "RIMPE Negocio Popular"
    RIMPE_GENERAL = "Régimen General"
    NO_RIMPE = ""
    CONTRIBUYENTE_ESPECIAL = "Contribuyente Especial"
    AGENTE_RETENCION = "Agente de Retención"
    SECTOR_PUBLICO = "Sector Público"
    RISE = "Régimen Simplificado RISE"


class Company(Base):
    """
    Modelo de Empresa para facturación electrónica del SRI.
    
    Contiene toda la información fiscal requerida por el SRI
    para la emisión de comprobantes electrónicos, incluyendo
    RUC, razón social, establecimientos y configuración fiscal.
    """
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario propietario de la empresa",
    )
    # Información fiscal principal
    ruc: Mapped[str] = mapped_column(
        String(13),
        nullable=False,
        index=True,
        comment="Registro Único de Contribuyente (13 dígitos)",
    )
    razon_social: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Razón social de la empresa (nombre legal)",
    )
    nombre_comercial: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nombre comercial de la empresa",
    )
    # Direcciones
    dir_matriz: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Dirección de la matriz de la empresa",
    )
    dir_establecimiento: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Dirección del establecimiento principal",
    )
    # Código de establecimiento y punto de emisión
    cod_establecimiento: Mapped[str] = mapped_column(
        String(3),
        default="001",
        nullable=False,
        comment="Código del establecimiento (3 dígitos)",
    )
    cod_punto_emision: Mapped[str] = mapped_column(
        String(3),
        default="001",
        nullable=False,
        comment="Código del punto de emisión (3 dígitos)",
    )
    # Información fiscal adicional
    contribuyente_especial: Mapped[str | None] = mapped_column(
        String(5),
        nullable=True,
        comment="Número de resolución como contribuyente especial",
    )
    obligado_contabilidad: Mapped[str] = mapped_column(
        String(2),
        default=ObligadoContabilidad.NO,
        nullable=False,
        comment="Indica si está obligado a llevar contabilidad (SI/NO)",
    )
    tipo_ambiente: Mapped[str] = mapped_column(
        String(1),
        default=TipoAmbiente.PRUEBAS,
        nullable=False,
        comment="Tipo de ambiente: 1=Pruebas, 2=Producción",
    )
    tipo_emision: Mapped[str] = mapped_column(
        String(1),
        default=TipoEmision.NORMAL,
        nullable=False,
        comment="Tipo de emisión: 1=Normal",
    )
    rise: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Régimen Simplificado RISE (número de resolución)",
    )
    agente_retencion: Mapped[str | None] = mapped_column(
        String(5),
        nullable=True,
        comment="Número de resolución como agente de retención",
    )
    contribuyente_rimpe: Mapped[str] = mapped_column(
        String(50),
        default="",
        nullable=False,
        comment="Tipo de contribuyente RIMPE",
    )
    # Contadores secuenciales (incrementados por cada comprobante emitido)
    secuencial_factura: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para facturas",
    )
    secuencial_nota_credito: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para notas de crédito",
    )
    secuencial_nota_debito: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para notas de débito",
    )
    secuencial_guia_remision: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para guías de remisión",
    )
    secuencial_retencion: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para comprobantes de retención",
    )
    secuencial_liquidacion: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para liquidaciones de compra",
    )
    secuencial_proforma: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para proformas",
    )
    secuencial_nota_venta: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para notas de venta",
    )
    secuencial_asiento: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Contador secuencial para asientos contables",
    )
    # Logo
    logo_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Ruta del logo de la empresa",
    )
    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la empresa está activa",
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
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="companies",
        lazy="selectin",
    )
    establishments: Mapped[list["Establishment"]] = relationship(
        "Establishment",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    clients: Mapped[list["Client"]] = relationship(  # noqa: F821
        "Client",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    suppliers: Mapped[list["Supplier"]] = relationship(  # noqa: F821
        "Supplier",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        "Product",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    comprobantes: Mapped[list["Comprobante"]] = relationship(  # noqa: F821
        "Comprobante",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    proformas: Mapped[list["Proforma"]] = relationship(  # noqa: F821
        "Proforma",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    employees: Mapped[list["Employee"]] = relationship(  # noqa: F821
        "Employee",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    roles_pago: Mapped[list["RolPago"]] = relationship(  # noqa: F821
        "RolPago",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    user_roles: Mapped[list["UserCompanyRole"]] = relationship(  # noqa: F821
        "UserCompanyRole",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    kardex_movements: Mapped[list["Kardex"]] = relationship(  # noqa: F821
        "Kardex",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Contabilidad
    cuentas_contables: Mapped[list["CuentaContable"]] = relationship(  # noqa: F821
        "CuentaContable",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    asientos_contables: Mapped[list["AsientoContable"]] = relationship(  # noqa: F821
        "AsientoContable",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    cuentas_por_cobrar: Mapped[list["CuentaPorCobrar"]] = relationship(  # noqa: F821
        "CuentaPorCobrar",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pagos: Mapped[list["Pago"]] = relationship(  # noqa: F821
        "Pago",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    periodos_fiscales: Mapped[list["PeriodoFiscal"]] = relationship(  # noqa: F821
        "PeriodoFiscal",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Compras
    ordenes_compra: Mapped[list["OrdenCompra"]] = relationship(  # noqa: F821
        "OrdenCompra",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    cuentas_por_pagar: Mapped[list["CuentaPorPagar"]] = relationship(  # noqa: F821
        "CuentaPorPagar",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    retenciones_compra: Mapped[list["RetencionCompra"]] = relationship(  # noqa: F821
        "RetencionCompra",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Almacén / Logística
    warehouses: Mapped[list["Warehouse"]] = relationship(  # noqa: F821
        "Warehouse",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Presupuestos
    presupuestos: Mapped[list["PresupuestoAnual"]] = relationship(  # noqa: F821
        "PresupuestoAnual",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Proyectos
    proyectos: Mapped[list["Proyecto"]] = relationship(  # noqa: F821
        "Proyecto",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Integraciones bancarias
    cuentas_bancarias: Mapped[list["CuentaBancaria"]] = relationship(  # noqa: F821
        "CuentaBancaria",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ecommerce_connectors: Mapped[list["EcommerceConnector"]] = relationship(  # noqa: F821
        "EcommerceConnector",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # ML / IA
    ml_predicciones: Mapped[list["MLPrediccion"]] = relationship(  # noqa: F821
        "MLPrediccion",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ml_alertas_fraude: Mapped[list["MLAlertaFraude"]] = relationship(  # noqa: F821
        "MLAlertaFraude",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ml_chatbot_sesiones: Mapped[list["MLChatbotSesion"]] = relationship(  # noqa: F821
        "MLChatbotSesion",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ml_recomendaciones: Mapped[list["MLRecomendacion"]] = relationship(  # noqa: F821
        "MLRecomendacion",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ml_categorias_reglas: Mapped[list["MLCategoriaRegla"]] = relationship(  # noqa: F821
        "MLCategoriaRegla",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # RRHH Extendido
    contratos: Mapped[list["Contrato"]] = relationship(  # noqa: F821
        "Contrato",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Notificaciones
    notifications: Mapped[list["Notification"]] = relationship(  # noqa: F821
        "Notification",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # CRM Avanzado
    crm_leads: Mapped[list["CRMLead"]] = relationship(  # noqa: F821
        "CRMLead",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    crm_opportunities: Mapped[list["CRMOpportunity"]] = relationship(  # noqa: F821
        "CRMOpportunity",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    crm_pipelines: Mapped[list["CRMPipeline"]] = relationship(  # noqa: F821
        "CRMPipeline",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    crm_activities: Mapped[list["CRMActivity"]] = relationship(  # noqa: F821
        "CRMActivity",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    crm_contact_segments: Mapped[list["CRMContactSegment"]] = relationship(  # noqa: F821
        "CRMContactSegment",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    crm_automations: Mapped[list["CRMAutomation"]] = relationship(  # noqa: F821
        "CRMAutomation",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, ruc={self.ruc}, razon_social={self.razon_social})>"

    @property
    def is_production(self) -> bool:
        """Indica si la empresa opera en ambiente de producción"""
        return self.tipo_ambiente == TipoAmbiente.PRODUCCION

    def get_next_secuencial(self, tipo_comprobante: str) -> str:
        """
        Obtiene e incrementa el siguiente número secuencial para un tipo de comprobante.
        Retorna el número secuencial como cadena de 9 dígitos rellenada con ceros.

        WARNING: This method is NOT thread-safe. Use `get_next_secuencial_async`
        in production endpoints for proper row-level locking.

        Args:
            tipo_comprobante: Código de tipo de comprobante según Tabla 1 del SRI
                "01" = Factura, "03" = Liquidación, "04" = Nota de Crédito,
                "05" = Nota de Débito, "06" = Guía de Remisión, "07" = Retención

        Returns:
            str: Número secuencial de 9 dígitos (ej: "000000001")
        """
        field_map = {
            "01": "secuencial_factura",
            "02": "secuencial_nota_venta",
            "03": "secuencial_liquidacion",
            "04": "secuencial_nota_credito",
            "05": "secuencial_nota_debito",
            "06": "secuencial_guia_remision",
            "07": "secuencial_retencion",
            "08": "secuencial_proforma",
        }
        field = field_map.get(tipo_comprobante, "secuencial_factura")
        current = getattr(self, field)
        setattr(self, field, current + 1)
        return str(current).zfill(9)

    async def get_next_secuencial_async(
        self, db, tipo_comprobante: str
    ) -> str:
        """
        Thread-safe version using SELECT ... FOR UPDATE for row-level locking.

        Args:
            db: AsyncSession for database operations
            tipo_comprobante: Código de tipo de comprobante

        Returns:
            str: Número secuencial de 9 dígitos (ej: "000000001")
        """
        from sqlalchemy import select, with_for_update

        # Lock the company row to prevent concurrent secuencial updates
        result = await db.execute(
            select(Company).where(Company.id == self.id).with_for_update()
        )
        locked_company = result.scalars().first()
        if not locked_company:
            raise ValueError(f"Company {self.id} not found")

        field_map = {
            "01": "secuencial_factura",
            "02": "secuencial_nota_venta",
            "03": "secuencial_liquidacion",
            "04": "secuencial_nota_credito",
            "05": "secuencial_nota_debito",
            "06": "secuencial_guia_remision",
            "07": "secuencial_retencion",
            "08": "secuencial_proforma",
        }
        field = field_map.get(tipo_comprobante, "secuencial_factura")
        current = getattr(locked_company, field)
        setattr(locked_company, field, current + 1)
        await db.flush()
        # Sync the value back to self
        setattr(self, field, current + 1)
        return str(current).zfill(9)

    def get_next_secuencial_proforma(self) -> str:
        """
        Obtiene e incrementa el siguiente número secuencial para proformas.
        Retorna el número secuencial en formato PRO-XXXXXX (6 dígitos, zero-padded).

        WARNING: This method is NOT thread-safe. Use `get_next_secuencial_proforma_async`
        in production endpoints for proper row-level locking.

        Returns:
            str: Número secuencial de proforma (ej: "PRO-000001")
        """
        current = self.secuencial_proforma
        self.secuencial_proforma = current + 1
        return f"PRO-{str(current).zfill(6)}"

    async def get_next_secuencial_proforma_async(self, db) -> str:
        """Thread-safe version using SELECT ... FOR UPDATE for row-level locking."""
        from sqlalchemy import select, with_for_update

        result = await db.execute(
            select(Company).where(Company.id == self.id).with_for_update()
        )
        locked_company = result.scalars().first()
        if not locked_company:
            raise ValueError(f"Company {self.id} not found")

        current = locked_company.secuencial_proforma
        locked_company.secuencial_proforma = current + 1
        await db.flush()
        self.secuencial_proforma = current + 1
        return f"PRO-{str(current).zfill(6)}"


class Establishment(Base):
    """
    Modelo de Establecimiento / Sucursal de una empresa.
    
    Cada empresa puede tener múltiples establecimientos con sus
    respectivos puntos de emisión para facturación electrónica.
    """
    __tablename__ = "establishments"

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
        comment="ID de la empresa a la que pertenece el establecimiento",
    )
    codigo: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="Código del establecimiento (3 dígitos, ej: 001)",
    )
    cod_punto_emision: Mapped[str] = mapped_column(
        String(3),
        default="001",
        nullable=False,
        comment="Código del punto de emisión (3 dígitos, ej: 001)",
    )
    direccion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Dirección del establecimiento",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el establecimiento está activo",
    )

    # Relaciones
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="establishments",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Establishment(id={self.id}, codigo={self.codigo}, company_id={self.company_id})>"
