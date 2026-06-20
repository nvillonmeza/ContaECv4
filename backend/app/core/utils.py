"""
ContaEC - Utilidades compartidas
Funciones de uso común entre múltiples módulos
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client, TipoIdentificacion
from app.core.licenses import get_license_limits

logger = logging.getLogger(__name__)


async def ensure_consumidor_final(
    db: AsyncSession,
    company_id: str,
) -> Client:
    """
    Crea el cliente 'Consumidor Final' por defecto para una empresa.
    
    Este cliente es obligatorio según el SRI para facturas donde
    el comprador no se identifica (ventas al público en general).
    Tipo de identificación: 07 (Consumidor Final)
    Número de identificación: 9999999999999 (13 veces 9)
    
    Args:
        db: Sesión de base de datos asíncrona
        company_id: ID de la empresa
    
    Returns:
        El cliente Consumidor Final (existente o recién creado)
    """
    # Verificar si ya existe
    result = await db.execute(
        select(Client).where(
            Client.company_id == company_id,
            Client.is_default_consumer == True,
        )
    )
    existing = result.scalars().first()
    if existing:
        return existing

    # Crear Consumidor Final
    consumer = Client(
        company_id=company_id,
        tipo_identificacion=TipoIdentificacion.CONSUMIDOR_FINAL.value,
        identificacion="9999999999999",
        razon_social="CONSUMIDOR FINAL",
        is_default_consumer=True,
        is_active=True,
    )
    db.add(consumer)
    await db.flush()

    logger.info(f"Cliente 'Consumidor Final' creado para empresa {company_id}")
    return consumer
