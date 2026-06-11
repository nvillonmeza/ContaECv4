"""
ContaEC - Sistema de Contabilidad y Facturación Electrónica del Ecuador
Backend FastAPI - Punto de entrada principal
Desarrollado por: T&M Technology Ec
Soporte: info@tymtechnology.shop | 0960068866
DNS: conta.tymtechnology.shop
"""
import logging
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.middleware.security import (
    RateLimitMiddleware,
    InputSanitizationMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.rate_limiter import limiter
from app.api.v1.router import api_router

# Import all models so SQLAlchemy registers them in Base.metadata
import app.models  # noqa: F401

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación FastAPI.
    Inicializa la base de datos y servicios al arrancar,
    y los cierra al detener.
    """
    # Startup
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}...")
    
    # Inicializar base de datos
    await init_db()
    logger.info("✅ Base de datos inicializada")
    
    # Validar secrets en producción
    security_warnings = settings.validate_production_secrets()
    if settings.is_production and security_warnings:
        logger.error("🔴 PRODUCCIÓN: Se encontraron problemas de seguridad críticos:")
        for warning in security_warnings:
            logger.error(f"  {warning}")
        raise RuntimeError(
            "No se puede iniciar en producción con secrets inseguros. "
            "Configure las variables de entorno necesarias."
        )
    elif security_warnings:
        for warning in security_warnings:
            logger.warning(warning)
    
    # Crear directorios necesarios
    import os
    for directory in [settings.BACKUP_DIR, settings.TEMP_DIR, settings.UPLOAD_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    # Inicializar usuario administrador por defecto
    await _init_admin_user()
    
    # Iniciar tarea de backup automático en background
    from app.api.v1.endpoints.backup import midnight_backup_task
    backup_task = asyncio.create_task(midnight_backup_task())
    
    # Iniciar tarea de limpieza de archivos volátiles
    from app.core.volatile_storage import start_cleanup_task
    asyncio.create_task(start_cleanup_task())
    logger.info("✅ Tarea de limpieza de archivos temporales iniciada")
    
    # Iniciar tarea de limpieza de token blacklist
    token_cleanup_task = asyncio.create_task(_token_blacklist_cleanup())
    logger.info("✅ Tarea de limpieza de token blacklist iniciada")
    
    logger.info(f"✅ {settings.APP_NAME} listo en http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    
    yield
    
    # Shutdown
    backup_task.cancel()
    token_cleanup_task.cancel()
    await close_db()
    logger.info(f"🔴 {settings.APP_NAME} detenido")


async def _token_blacklist_cleanup():
    """Tarea periódica para limpiar tokens expirados de la blacklist"""
    from app.core.token_blacklist import get_token_blacklist
    while True:
        try:
            await asyncio.sleep(3600)  # Clean up every hour
            blacklist = get_token_blacklist()
            removed = blacklist.cleanup_expired()
            if removed > 0:
                logger.info(f"Token blacklist cleanup: {removed} expired tokens removed")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in token blacklist cleanup: {e}")
            await asyncio.sleep(300)  # Wait 5 min before retry


async def _init_admin_user():
    """Crear usuario administrador por defecto si no existe"""
    from sqlalchemy import select
    from app.core.database import async_session_factory
    from app.models.user import User, UserConfig, LicenseType
    from app.core.security import get_password_hash
    from datetime import datetime, timezone, timedelta

    # Password from env var
    admin_password = settings.ADMIN_PASSWORD
    if not admin_password:
        logger.error(
            "🔴 ADMIN_PASSWORD no configurada. No se creará el usuario admin. "
            "Configure la variable de entorno ADMIN_PASSWORD."
        )
        return
    
    async with async_session_factory() as session:
        try:
            result = await session.execute(
                select(User).where(User.email == settings.ADMIN_EMAIL)
            )
            admin = result.scalars().first()
            
            if not admin:
                admin = User(
                    email=settings.ADMIN_EMAIL,
                    full_name="Administrador ContaEC",
                    hashed_password=get_password_hash(admin_password),
                    is_active=True,
                    is_admin=True,
                    language="es_EC",
                    theme="light",
                    license_type=LicenseType.ANUAL,
                    license_start_date=datetime.now(timezone.utc),
                    license_end_date=datetime.now(timezone.utc) + timedelta(days=3650),  # 10 años
                )
                session.add(admin)
                await session.flush()
                
                # Crear config por defecto
                admin_config = UserConfig(
                    user_id=admin.id,
                    environment_mode="production",
                )
                session.add(admin_config)
                await session.flush()
                await session.commit()
                
                logger.info(f"✅ Usuario administrador creado: {settings.ADMIN_EMAIL}")
            else:
                logger.info(f"ℹ️  Usuario administrador ya existe: {settings.ADMIN_EMAIL}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creando admin: {e}")


# Crear aplicación FastAPI
app = FastAPI(
    title="ContaEC",
    version=settings.APP_VERSION,
    description=(
        "Sistema de Contabilidad y Facturación Electrónica del Ecuador\n\n"
        "Desarrollado por: T&M Technology Ec\n"
        "Soporte: info@tymtechnology.shop | 0960068866\n"
        "DNS: conta.tymtechnology.shop\n\n"
        "Facturación electrónica conforme a la Ficha Técnica del SRI v2.32"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Rate limiting con slowapi
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ==================== MIDDLEWARE ====================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Headers de seguridad
app.add_middleware(SecurityHeadersMiddleware)

# Sanitización de entradas
app.add_middleware(InputSanitizationMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# ==================== RUTAS ====================

# API v1
app.include_router(api_router)

# Health check (sin versión para compatibilidad)
@app.get("/api/health")
async def health_check():
    """Verificación de estado del servidor"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "developer": "T&M Technology Ec",
        "support": "info@tymtechnology.shop",
        "phone": "0960068866",
    }


# Catálogos SRI (sin versión para fácil acceso)
@app.get("/api/sri/catalogs")
async def get_sri_catalogs():
    """Obtener todos los catálogos del SRI"""
    from app.schemas.sri import (
        IVA_TARIFAS,
        ICE_TARIFAS,
        RETENCION_IVA,
        RETENCION_RENTA,
        TIPOS_COMPROBANTE,
        TIPOS_IDENTIFICACION,
        FORMAS_PAGO,
        ESTADOS_COMPROBANTE,
        CONTRIBUYENTE_TIPOS,
        REGIMEN_TIPOS,
    )
    return {
        "iva_tarifas": [t.model_dump() for t in IVA_TARIFAS],
        "ice_tarifas": [t.model_dump() for t in ICE_TARIFAS],
        "retencion_iva": [r.model_dump() for r in RETENCION_IVA],
        "retencion_renta": [r.model_dump() for r in RETENCION_RENTA],
        "tipos_comprobante": [t.model_dump() for t in TIPOS_COMPROBANTE],
        "tipos_identificacion": [t.model_dump() for t in TIPOS_IDENTIFICACION],
        "formas_pago": [f.model_dump() for f in FORMAS_PAGO],
        "estados_comprobante": [e.model_dump() for e in ESTADOS_COMPROBANTE],
        "contribuyente_tipos": CONTRIBUYENTE_TIPOS,
        "regimen_tipos": REGIMEN_TIPOS,
    }


# Archivos estáticos para uploads
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
