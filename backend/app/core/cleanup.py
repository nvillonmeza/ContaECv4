"""
ContaEC - Limpieza de Archivos Temporales
Funciones de limpieza para el sistema de almacenamiento volátil
"""
import json
import logging
import os
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Directorios temporales - usa TEMP_DIR del config
TEMP_BASE = Path(settings.TEMP_DIR)
TEMP_DIRS = [
    str(TEMP_BASE),
    str(TEMP_BASE / "exports"),
    str(TEMP_BASE / "imports"),
    str(TEMP_BASE / "backups"),
]


def ensure_temp_dirs() -> dict[str, Path]:
    """
    Asegura que los directorios temporales existan.

    Returns:
        Diccionario con nombres de directorio y sus paths
    """
    dirs = {}
    for dir_path in TEMP_DIRS:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        dirs[dir_path] = path
    return dirs


def get_temp_dir(category: str = "exports") -> Path:
    """
    Obtener directorio temporal para una categoría.

    Args:
        category: exports, imports, backups, general

    Returns:
        Path al directorio temporal
    """
    base = TEMP_BASE
    base.mkdir(parents=True, exist_ok=True)

    if category in ("exports", "imports", "backups"):
        subdir = base / category
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir

    return base


def cleanup_expired_files(max_age_hours: int = 1) -> dict:
    """
    Limpiar archivos temporales expirados.

    Args:
        max_age_hours: Edad máxima en horas antes de eliminar

    Returns:
        Diccionario con estadísticas de limpieza
    """
    stats = {
        "files_deleted": 0,
        "bytes_freed": 0,
        "dirs_cleaned": [],
        "errors": [],
    }

    now = datetime.now(timezone.utc)

    for dir_path in TEMP_DIRS:
        path = Path(dir_path)
        if not path.exists():
            continue

        try:
            for filepath in path.iterdir():
                # Saltar directorios
                if filepath.is_dir():
                    continue

                # Saltar archivos de metadatos
                if filepath.suffix == ".meta" or filepath.name.endswith(".meta.json"):
                    continue

                # Verificar si está expirado
                meta_file = path / f"{filepath.name}.meta"
                if not meta_file.exists():
                    # Try alternative naming
                    meta_file = path / f"{filepath.name}.meta.json"

                expires_at = None

                if meta_file.exists():
                    try:
                        metadata = json.loads(meta_file.read_text())
                        expires_at_str = metadata.get("expires_at") or metadata.get("expiry_time")
                        if expires_at_str:
                            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                    except (json.JSONDecodeError, KeyError, ValueError):
                        pass

                # Si no hay expires_at, calcular basado en mtime
                if expires_at is None:
                    try:
                        mtime = datetime.fromtimestamp(
                            filepath.stat().st_mtime, tz=timezone.utc
                        )
                        expires_at = mtime + timedelta(hours=max_age_hours)
                    except (OSError, ValueError):
                        continue

                # Eliminar si expiró
                if now > expires_at:
                    try:
                        file_size = filepath.stat().st_size
                        # Eliminar metadatos
                        if meta_file.exists():
                            meta_file.unlink()
                        # Eliminar archivo
                        filepath.unlink()
                        stats["files_deleted"] += 1
                        stats["bytes_freed"] += file_size
                        stats["dirs_cleaned"].append(str(path))
                    except Exception as e:
                        stats["errors"].append(f"Error eliminando {filepath}: {e}")

        except Exception as e:
            stats["errors"].append(f"Error procesando {dir_path}: {e}")

    # Log resultado
    if stats["files_deleted"] > 0:
        logger.info(
            f"Limpieza completada: {stats['files_deleted']} archivos, "
            f"{stats['bytes_freed'] / 1024:.2f} KB liberados"
        )

    return stats


def cleanup_old_temp_dirs(days: int = 7) -> dict:
    """
    Limpiar directorios temporales antiguos.

    Args:
        days: Días de antigüedad para eliminar directorios

    Returns:
        Diccionario con estadísticas de limpieza
    """
    stats = {
        "dirs_deleted": 0,
        "bytes_freed": 0,
        "errors": [],
    }

    if not TEMP_BASE.exists():
        return stats

    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=days)

    try:
        for subdir in TEMP_BASE.iterdir():
            if not subdir.is_dir():
                continue

            try:
                mtime = datetime.fromtimestamp(
                    subdir.stat().st_mtime, tz=timezone.utc
                )
                if mtime < threshold:
                    # Calcular tamaño antes de eliminar
                    size = sum(
                        f.stat().st_size for f in subdir.rglob("*") if f.is_file()
                    )
                    shutil.rmtree(subdir)
                    stats["dirs_deleted"] += 1
                    stats["bytes_freed"] += size
                    logger.info(f"Directorio temporal eliminado: {subdir} ({size} bytes)")
            except Exception as e:
                stats["errors"].append(f"Error eliminando {subdir}: {e}")

    except Exception as e:
        stats["errors"].append(f"Error general: {e}")

    return stats


def get_temp_storage_status() -> dict:
    """
    Obtener estado del almacenamiento temporal.

    Returns:
        Diccionario con uso actual de espacio temporal
    """
    status = {
        "total_files": 0,
        "total_bytes": 0,
        "by_category": {},
    }

    for dir_path in TEMP_DIRS:
        path = Path(dir_path)
        if not path.exists():
            continue

        category_name = path.name

        files = [f for f in path.iterdir() if f.is_file() and not f.name.endswith((".meta", ".meta.json"))]
        total_bytes = sum(f.stat().st_size for f in files)

        status["total_files"] += len(files)
        status["total_bytes"] += total_bytes
        status["by_category"][category_name] = {
            "files": len(files),
            "bytes": total_bytes,
        }

    # Convertir bytes a formato legible
    status["total_bytes_readable"] = f"{status['total_bytes'] / 1024:.2f} KB"

    return status