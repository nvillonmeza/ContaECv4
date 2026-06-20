"""
ContaEC - Almacenamiento Volátil
Servicio de almacenamiento temporal de archivos con auto-eliminación
basada en TTL (Time To Live) configurable.

Los archivos se almacenan en TEMP_DIR con metadatos (creation_time, ttl)
en un archivo JSON sidecar (.meta.json) junto al archivo de datos.

Una tarea en segundo plano limpia los archivos expirados periódicamente.
"""
import asyncio
import aiofiles
import json
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ==========================================
# Configuración
# ==========================================

TEMP_DIR = Path(settings.TEMP_DIR)
DEFAULT_TTL_HOURS = 24  # Tiempo de vida por defecto: 24 horas
CLEANUP_INTERVAL_SECONDS = 3600  # Intervalo de limpieza: 1 hora


def _ensure_temp_dir() -> None:
    """Asegura que el directorio temporal exista."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def _get_meta_path(file_path: Path) -> Path:
    """Obtiene la ruta del archivo de metadatos sidecar."""
    return file_path.with_suffix(file_path.suffix + ".meta.json")


def _write_meta(file_path: Path, meta: dict) -> None:
    """Escribe los metadatos en el archivo sidecar JSON."""
    meta_path = _get_meta_path(file_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)


async def _write_meta_async(file_path: Path, meta: dict) -> None:
    """Escribe los metadatos en el archivo sidecar JSON (async)."""
    meta_path = _get_meta_path(file_path)
    async with aiofiles.open(meta_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(meta, indent=2, default=str))


async def _read_meta_async(file_path: Path) -> Optional[dict]:
    """Lee los metadatos del archivo sidecar JSON (async)."""
    meta_path = _get_meta_path(file_path)
    if not meta_path.exists():
        return None
    try:
        async with aiofiles.open(meta_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Error al leer metadatos de {meta_path}: {e}")
        return None


def _is_expired(meta: dict) -> bool:
    """Verifica si un archivo ha expirado según su TTL."""
    creation_time = datetime.fromisoformat(meta.get("creation_time", ""))
    ttl_hours = meta.get("ttl_hours", DEFAULT_TTL_HOURS)
    expiry_time = creation_time + timedelta(hours=ttl_hours)
    return datetime.now(timezone.utc) > expiry_time.replace(tzinfo=timezone.utc)


# ==========================================
# Funciones principales
# ==========================================

async def save_temp_file(
    content: bytes,
    filename: Optional[str] = None,
    prefix: str = "temp",
    suffix: str = "",
    ttl_hours: float = DEFAULT_TTL_HOURS,
    sub_dir: Optional[str] = None,
) -> dict:
    """
    Guarda un archivo en el almacenamiento temporal.

    Args:
        content: Contenido del archivo en bytes
        filename: Nombre del archivo (opcional, se genera uno si no se proporciona)
        prefix: Prefijo para el nombre generado
        suffix: Sufijo para el nombre generado
        ttl_hours: Tiempo de vida en horas (default: 24)
        sub_dir: Subdirectorio dentro de TEMP_DIR (opcional)

    Returns:
        Diccionario con: file_id, file_path, filename, creation_time, ttl_hours, expiry_time
    """
    _ensure_temp_dir()

    # Generar ID y nombre de archivo
    file_id = str(uuid.uuid4())
    if filename is None:
        filename = f"{prefix}_{file_id}{suffix}"

    # Sanitize sub_dir to prevent path traversal
    if sub_dir:
        # Only allow alphanumeric, hyphens, and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', sub_dir):
            raise ValueError(f"sub_dir contains invalid characters: {sub_dir}")
        target_dir = TEMP_DIR / sub_dir
    else:
        target_dir = TEMP_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / filename

    # Guardar contenido (async)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Guardar metadatos (async)
    now = datetime.now(timezone.utc)
    meta = {
        "file_id": file_id,
        "filename": filename,
        "creation_time": now.isoformat(),
        "ttl_hours": ttl_hours,
        "expiry_time": (now + timedelta(hours=ttl_hours)).isoformat(),
        "size_bytes": len(content),
    }
    await _write_meta_async(file_path, meta)

    logger.info(
        f"Archivo temporal guardado: {filename}, "
        f"TTL: {ttl_hours}h, expira: {meta['expiry_time']}"
    )

    return {
        "file_id": file_id,
        "file_path": str(file_path),
        "filename": filename,
        "creation_time": meta["creation_time"],
        "ttl_hours": ttl_hours,
        "expiry_time": meta["expiry_time"],
    }


async def get_temp_file(file_id: str) -> Optional[dict]:
    """
    Obtiene un archivo temporal por su ID.

    Args:
        file_id: ID del archivo temporal

    Returns:
        Diccionario con file_path, filename, meta, content, o None si no existe/expiró
    """
    _ensure_temp_dir()

    # Buscar archivo por ID en metadatos
    for meta_path in TEMP_DIR.rglob("*.meta.json"):
        try:
            async with aiofiles.open(meta_path, "r", encoding="utf-8") as f:
                content = await f.read()
                meta = json.loads(content)
        except (json.JSONDecodeError, IOError):
            continue

        if meta.get("file_id") == file_id:
            # Verificar si expiró
            if _is_expired(meta):
                logger.info(f"Archivo temporal expirado: {meta.get('filename')}")
                await _delete_file_and_meta_async(meta_path)
                return None

            # Obtener ruta del archivo de datos
            data_path = Path(str(meta_path).replace(".meta.json", ""))

            if not data_path.exists():
                logger.warning(f"Archivo de datos no encontrado: {data_path}")
                return None

            # Leer contenido (async)
            async with aiofiles.open(data_path, "rb") as f:
                content = await f.read()

            return {
                "file_id": file_id,
                "file_path": str(data_path),
                "filename": meta.get("filename"),
                "meta": meta,
                "content": content,
            }

    return None


async def get_temp_file_path(file_id: str) -> Optional[Path]:
    """
    Obtiene la ruta de un archivo temporal por su ID.

    Args:
        file_id: ID del archivo temporal

    Returns:
        Path del archivo, o None si no existe/expiró
    """
    result = await get_temp_file(file_id)
    if result:
        return Path(result["file_path"])
    return None


def _delete_file_and_meta(meta_path: Path) -> None:
    """Elimina un archivo de datos y su archivo de metadatos (síncrono, solo para uso interno)."""
    data_path = Path(str(meta_path).replace(".meta.json", ""))
    try:
        if data_path.exists():
            data_path.unlink()
    except OSError as e:
        logger.warning(f"Error al eliminar archivo {data_path}: {e}")
    try:
        if meta_path.exists():
            meta_path.unlink()
    except OSError as e:
        logger.warning(f"Error al eliminar metadatos {meta_path}: {e}")


async def _delete_file_and_meta_async(meta_path: Path) -> None:
    """Elimina un archivo de datos y su archivo de metadatos (async)."""
    data_path = Path(str(meta_path).replace(".meta.json", ""))
    try:
        if data_path.exists():
            await asyncio.to_thread(data_path.unlink)
    except OSError as e:
        logger.warning(f"Error al eliminar archivo {data_path}: {e}")
    try:
        if meta_path.exists():
            await asyncio.to_thread(meta_path.unlink)
    except OSError as e:
        logger.warning(f"Error al eliminar metadatos {meta_path}: {e}")


async def cleanup_expired_files() -> int:
    """
    Elimina todos los archivos temporales expirados.

    Returns:
        Número de archivos eliminados
    """
    _ensure_temp_dir()
    deleted_count = 0

    for meta_path in TEMP_DIR.rglob("*.meta.json"):
        try:
            async with aiofiles.open(meta_path, "r", encoding="utf-8") as f:
                content = await f.read()
                meta = json.loads(content)
        except (json.JSONDecodeError, IOError):
            continue

        if _is_expired(meta):
            await _delete_file_and_meta_async(meta_path)
            deleted_count += 1
            logger.debug(f"Archivo expirado eliminado: {meta.get('filename')}")

    if deleted_count > 0:
        logger.info(f"Limpieza de archivos temporales: {deleted_count} archivos eliminados")

    return deleted_count


async def delete_temp_file(file_id: str) -> bool:
    """
    Elimina un archivo temporal por su ID.

    Args:
        file_id: ID del archivo temporal

    Returns:
        True si se eliminó, False si no se encontró
    """
    _ensure_temp_dir()

    for meta_path in TEMP_DIR.rglob("*.meta.json"):
        try:
            async with aiofiles.open(meta_path, "r", encoding="utf-8") as f:
                content = await f.read()
                meta = json.loads(content)
        except (json.JSONDecodeError, IOError):
            continue

        if meta.get("file_id") == file_id:
            await _delete_file_and_meta_async(meta_path)
            logger.info(f"Archivo temporal eliminado: {meta.get('filename')}")
            return True

    return False


async def list_temp_files(
    prefix: Optional[str] = None,
    sub_dir: Optional[str] = None,
) -> list[dict]:
    """
    Lista los archivos temporales activos.

    Args:
        prefix: Filtrar por prefijo de nombre
        sub_dir: Filtrar por subdirectorio

    Returns:
        Lista de diccionarios con información de los archivos
    """
    _ensure_temp_dir()
    files = []

    search_dir = TEMP_DIR / sub_dir if sub_dir else TEMP_DIR

    for meta_path in search_dir.rglob("*.meta.json"):
        try:
            async with aiofiles.open(meta_path, "r", encoding="utf-8") as f:
                content = await f.read()
                meta = json.loads(content)
        except (json.JSONDecodeError, IOError):
            continue

        # Filtrar por prefijo
        if prefix and not meta.get("filename", "").startswith(prefix):
            continue

        # Verificar expiración
        if _is_expired(meta):
            continue

        files.append({
            "file_id": meta.get("file_id"),
            "filename": meta.get("filename"),
            "creation_time": meta.get("creation_time"),
            "ttl_hours": meta.get("ttl_hours"),
            "expiry_time": meta.get("expiry_time"),
            "size_bytes": meta.get("size_bytes"),
        })

    return files


# ==========================================
# Tarea en segundo plano
# ==========================================

_cleanup_running = False


async def start_cleanup_task() -> None:
    """
    Inicia la tarea de limpieza periódica de archivos expirados.
    Se ejecuta en segundo plano como parte del ciclo de vida de la aplicación.
    Corre indefinidamente con un intervalo de CLEANUP_INTERVAL_SECONDS.
    """
    global _cleanup_running
    if _cleanup_running:
        return

    _cleanup_running = True
    logger.info("Tarea de limpieza de archivos temporales iniciada (periódica)")

    try:
        while _cleanup_running:
            try:
                await cleanup_expired_files()
            except Exception as e:
                logger.error(f"Error en tarea de limpieza: {e}")

            # Sleep in small increments so we can exit quickly when stopped
            for _ in range(CLEANUP_INTERVAL_SECONDS):
                if not _cleanup_running:
                    break
                await asyncio.sleep(1)
    finally:
        _cleanup_running = False
        logger.info("Tarea de limpieza de archivos temporales detenida")


async def get_storage_stats() -> dict:
    """
    Obtiene estadísticas del almacenamiento temporal.

    Returns:
        Diccionario con: total_files, total_size_bytes, expired_files, active_files
    """
    _ensure_temp_dir()
    total_files = 0
    total_size = 0
    expired_files = 0
    active_files = 0

    for meta_path in TEMP_DIR.rglob("*.meta.json"):
        try:
            async with aiofiles.open(meta_path, "r", encoding="utf-8") as f:
                content = await f.read()
                meta = json.loads(content)
        except (json.JSONDecodeError, IOError):
            continue

        total_files += 1
        total_size += meta.get("size_bytes", 0)

        if _is_expired(meta):
            expired_files += 1
        else:
            active_files += 1

    return {
        "total_files": total_files,
        "total_size_bytes": total_size,
        "expired_files": expired_files,
        "active_files": active_files,
        "temp_dir": str(TEMP_DIR),
    }


async def run_cleanup_now() -> dict:
    """
    Ejecutar limpieza inmediata de archivos temporales.

    Returns:
        Diccionario con estadísticas de limpieza
    """
    from app.core.cleanup import cleanup_expired_files, cleanup_old_temp_dirs

    logger.info("Ejecutando limpieza inmediata...")

    stats = cleanup_expired_files()
    dir_stats = cleanup_old_temp_dirs()

    # Combinar estadísticas
    stats["dirs_deleted"] = dir_stats["dirs_deleted"]
    stats["bytes_freed_total"] = stats["bytes_freed"] + dir_stats["bytes_freed"]

    logger.info(
        f"Limpieza inmediata completada: {stats['files_deleted']} archivos, "
        f"{stats['dirs_deleted']} directorios, "
        f"{stats['bytes_freed_total'] / 1024:.2f} KB liberados"
    )

    return stats


def get_storage_status() -> dict:
    """
    Obtener estado actual del almacenamiento volátil.

    Returns:
        Diccionario con uso de espacio temporal
    """
    from app.core.cleanup import get_temp_storage_status
    return get_temp_storage_status()
