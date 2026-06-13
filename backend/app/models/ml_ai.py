"""
ContaEC - Modelos de Machine Learning / IA
Predicciones, detección de fraude, chatbot, recomendaciones, auto-categorización
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
# Enums
# ========================================

class PrediccionTipo(str, Enum):
    """Tipo de predicción ML"""
    VENTAS = "ventas"
    INGRESOS = "ingresos"
    GASTOS = "gastos"
    FLUJO_CAJA = "flujo_caja"


class PrediccionEstado(str, Enum):
    """Estado de la predicción"""
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    CON_ERROR = "con_error"


class FraudeSeveridad(str, Enum):
    """Severidad de la alerta de fraude"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class FraudeEstado(str, Enum):
    """Estado de la alerta de fraude"""
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    DESCARTADO = "descartado"
    INVESTIGANDO = "investigando"


class ChatbotEstado(str, Enum):
    """Estado de la sesión del chatbot"""
    ACTIVA = "activa"
    CERRADA = "cerrada"


class RecomendacionTipo(str, Enum):
    """Tipo de recomendación"""
    PRODUCTO = "producto"
    CLIENTE = "cliente"
    PRECIO = "precio"
    INVENTARIO = "inventario"
    FINANCIERA = "financiera"


class RecomendacionEstado(str, Enum):
    """Estado de la recomendación"""
    PENDIENTE = "pendiente"
    APLICADA = "aplicada"
    DESCARTADA = "descartada"


# ========================================
# Predicciones ML
# ========================================

class MLPrediccion(Base):
    """
    Modelo de Predicción ML.
    Registra predicciones de ventas, ingresos, gastos y flujo de caja
    con métricas de desempeño y datos de entrada/salida.
    """
    __tablename__ = "ml_predicciones"

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
        comment="ID del usuario que solicitó la predicción",
    )
    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Tipo: ventas, ingresos, gastos, flujo_caja",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=PrediccionEstado.PENDIENTE.value,
        nullable=False,
        index=True,
        comment="Estado: pendiente, completada, con_error",
    )
    periodo_desde: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha inicio del periodo de datos de entrada",
    )
    periodo_hasta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha fin del periodo de datos de entrada",
    )
    datos_entrada: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con datos de entrada usados para la predicción",
    )
    resultado: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con resultado de la predicción",
    )
    metricas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con métricas de desempeño (MAPE, RMSE, R2)",
    )
    modelo_usado: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Modelo usado: moving_average, exponential_smoothing, linear_regression, arima",
    )
    confianza: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Nivel de confianza de la predicción (0-100)",
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
        back_populates="ml_predicciones",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MLPrediccion(id={self.id}, tipo={self.tipo}, "
            f"modelo={self.modelo_usado}, estado={self.estado})>"
        )


# ========================================
# Alertas de Fraude
# ========================================

class MLAlertaFraude(Base):
    """
    Modelo de Alerta de Fraude.
    Registra alertas de posibles fraudes detectados automáticamente
    por el sistema de ML con puntuación y evidencia.
    """
    __tablename__ = "ml_alertas_fraude"

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
    comprobante_id: Mapped[str | None] = mapped_column(
        PG_UUID(),
        ForeignKey("comprobantes.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del comprobante asociado a la alerta",
    )
    tipo_deteccion: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Tipo: monto_anomalo, duplicado, patron_sospechoso, ruc_invalido, secuencia_anomala",
    )
    severidad: Mapped[str] = mapped_column(
        String(20),
        default=FraudeSeveridad.MEDIA.value,
        nullable=False,
        index=True,
        comment="Severidad: baja, media, alta, critica",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=FraudeEstado.PENDIENTE.value,
        nullable=False,
        index=True,
        comment="Estado: pendiente, confirmado, descartado, investigando",
    )
    puntuacion_fraude: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0"),
        nullable=False,
        comment="Puntuación de fraude (0-100)",
    )
    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Descripción de la alerta de fraude",
    )
    evidencia: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con evidencia que respalda la alerta",
    )
    resolucion_nota: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Nota de resolución de la alerta",
    )
    resolucion_fecha: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de resolución de la alerta",
    )
    resuelto_por: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID del usuario que resolvió la alerta",
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
        back_populates="ml_alertas_fraude",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MLAlertaFraude(id={self.id}, tipo={self.tipo_deteccion}, "
            f"severidad={self.severidad}, puntuacion={self.puntuacion_fraude})>"
        )


# ========================================
# Chatbot Sesiones y Mensajes
# ========================================

class MLChatbotSesion(Base):
    """
    Modelo de Sesión del Chatbot.
    Registra las sesiones de chat del asistente virtual
    con contexto acumulado para mantener la conversación.
    """
    __tablename__ = "ml_chatbot_sesiones"

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
        comment="ID del usuario de la sesión",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=ChatbotEstado.ACTIVA.value,
        nullable=False,
        index=True,
        comment="Estado: activa, cerrada",
    )
    titulo: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Título descriptivo de la sesión",
    )
    contexto: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con contexto acumulado de la conversación",
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
        back_populates="ml_chatbot_sesiones",
        lazy="selectin",
    )
    mensajes: Mapped[list["MLChatbotMensaje"]] = relationship(
        "MLChatbotMensaje",
        back_populates="sesion",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MLChatbotSesion(id={self.id}, estado={self.estado}, "
            f"titulo={self.titulo})>"
        )


class MLChatbotMensaje(Base):
    """
    Modelo de Mensaje del Chatbot.
    Registra cada mensaje dentro de una sesión del chatbot
    con detección de intención y entidades.
    """
    __tablename__ = "ml_chatbot_mensajes"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    sesion_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("ml_chatbot_sesiones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la sesión del chatbot",
    )
    rol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Rol: usuario, asistente, sistema",
    )
    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Contenido del mensaje",
    )
    intencion_detectada: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Intención detectada del mensaje",
    )
    entidades: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con entidades extraídas del mensaje",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    sesion: Mapped["MLChatbotSesion"] = relationship(
        "MLChatbotSesion",
        back_populates="mensajes",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MLChatbotMensaje(id={self.id}, rol={self.rol}, "
            f"intencion={self.intencion_detectada})>"
        )


# ========================================
# Recomendaciones
# ========================================

class MLRecomendacion(Base):
    """
    Modelo de Recomendación ML.
    Registra recomendaciones generadas por el sistema de ML
    para productos, clientes, precios, inventario y finanzas.
    """
    __tablename__ = "ml_recomendaciones"

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
        comment="ID del usuario que recibió la recomendación",
    )
    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Tipo: producto, cliente, precio, inventario, financiera",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default=RecomendacionEstado.PENDIENTE.value,
        nullable=False,
        index=True,
        comment="Estado: pendiente, aplicada, descartada",
    )
    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Título descriptivo de la recomendación",
    )
    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Descripción detallada de la recomendación",
    )
    datos_contexto: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON con datos de contexto de la recomendación",
    )
    impacto_estimado: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Impacto estimado de aplicar la recomendación",
    )
    confianza: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Nivel de confianza de la recomendación (0-100)",
    )
    fecha_aplicacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha en que se aplicó la recomendación",
    )
    aplicada_por: Mapped[str | None] = mapped_column(
        PG_UUID(),
        nullable=True,
        comment="ID del usuario que aplicó la recomendación",
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
        back_populates="ml_recomendaciones",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MLRecomendacion(id={self.id}, tipo={self.tipo}, "
            f"titulo={self.titulo}, estado={self.estado})>"
        )


# ========================================
# Categorización Automática (Reglas)
# ========================================

class MLCategoriaRegla(Base):
    """
    Modelo de Regla de Categorización.
    Registra las reglas para la categorización automática
    de movimientos bancarios y descripciones.
    """
    __tablename__ = "ml_categorias_reglas"

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
    categoria: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre de la categoría",
    )
    subcategoria: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Subcategoría (opcional)",
    )
    palabras_clave: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON con lista de palabras clave para matching",
    )
    patron_regex: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Patrón regex para matching avanzado",
    )
    prioridad: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Prioridad de la regla (mayor = más prioridad)",
    )
    es_activa: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la regla está activa",
    )
    aplicaciones_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de veces que se ha aplicado la regla",
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
        back_populates="ml_categorias_reglas",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MLCategoriaRegla(id={self.id}, categoria={self.categoria}, "
            f"prioridad={self.prioridad})>"
        )
