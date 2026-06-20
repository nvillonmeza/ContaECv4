"""
ContaEC - Endpoints de Almacenamiento Volátil
Administración de limpieza de archivos temporales
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.volatile_storage import (
    run_cleanup_now,
    get_storage_stats,
    get_storage_status as get_volatile_status,
)
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/volatile", tags=["Almacenamiento Volátil"])


@router.post("/cleanup")
async def trigger_cleanup(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ejecutar limpieza inmediata de archivos temporales expirados.

    Solo usuarios admin pueden ejecutar esta operación.
    Limpia archivos con edad mayor a 1 hora y directorios con más de 7 días.

    Returns:
        Estadísticas de la limpieza realizada
    """
    # Solo admin puede ejecutar cleanup manual
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ejecutar limpieza de archivos temporales.",
        )

    try:
        stats = await run_cleanup_now()
        return {
            "message": "Limpieza de archivos temporales completada",
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Error en cleanup manual: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la limpieza: {str(e)}",
        )


@router.get("/status")
async def get_volatile_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener estado actual del almacenamiento volátil.

    Muestra cantidad de archivos temporales, espacio usado,
    y distribución por categoría (exports, imports, backups).

    Returns:
        Estado del almacenamiento temporal
    """
    try:
        volatile_status = get_volatile_status()
        stats = await get_storage_stats()

        return {
            "volatile_storage": volatile_status,
            "temp_files": {
                "total_files": stats.get("total_files", 0),
                "total_size_bytes": stats.get("total_size_bytes", 0),
                "total_size_readable": f"{stats.get('total_size_bytes', 0) / 1024:.2f} KB",
                "active_files": stats.get("active_files", 0),
                "expired_files": stats.get("expired_files", 0),
                "temp_dir": stats.get("temp_dir", ""),
            },
        }
    except Exception as e:
        logger.error(f"Error obteniendo status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado: {str(e)}",
        )