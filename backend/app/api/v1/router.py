"""
ContaEC - Router principal API v1
Agrupa todos los endpoints de la versión 1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, admin, companies, config, licenses, backup, uploads, comprobantes, products, clients, proformas, audit, email_templates, email_receiver, smtp_profiles, suppliers, purchases, warehouses, ubicaciones, pos, bi, budgets, projects, integrations, ml_ai, accounting, notifications, user_roles, crm, cuentas_pagar, employees, payroll, payroll_reports, payroll_exports, attendance, exports, imports, kardex, volatile, email_logs

api_router = APIRouter(prefix="/api/v1")

# Autenticación
api_router.include_router(auth.router)

# Administración
api_router.include_router(admin.router)

# Empresas
api_router.include_router(companies.router)

# Configuración de usuario
api_router.include_router(config.router)

# Licencias
api_router.include_router(licenses.router)

# Backup y restauración
api_router.include_router(backup.router)

# Subida de archivos con escaneo de malware
api_router.include_router(uploads.router)

# Comprobantes electrónicos
api_router.include_router(comprobantes.router)

# Productos/Servicios
api_router.include_router(products.router)

# Clientes
api_router.include_router(clients.router)

# Proformas
api_router.include_router(proformas.router)

# Auditoría
api_router.include_router(audit.router)

# Plantillas de Correo
api_router.include_router(email_templates.router)

# Recepción de Correo
api_router.include_router(email_receiver.router)

# Perfiles SMTP
api_router.include_router(smtp_profiles.router)

# Proveedores
api_router.include_router(suppliers.router)

# Compras (Órdenes de compra, Recepciones, Cuentas por pagar, Retenciones)
api_router.include_router(purchases.router)

# Multi-Almacén y Logística
api_router.include_router(warehouses.router)

# Ubicaciones Físicas de Almacén
api_router.include_router(ubicaciones.router)

# Punto de Venta (POS)
api_router.include_router(pos.router)

# Business Intelligence y Dashboards
api_router.include_router(bi.router)

# Presupuestos y Control Presupuestario
api_router.include_router(budgets.router)

# Proyectos y Servicios
api_router.include_router(projects.router)

# Integraciones (Bancaria + E-Commerce)
api_router.include_router(integrations.router)

# Machine Learning / Inteligencia Artificial
api_router.include_router(ml_ai.router)

# Contabilidad Core (Plan de Cuentas, Asientos, CxC, Pagos, Períodos Fiscales)
api_router.include_router(accounting.router)

# Notificaciones del Sistema
api_router.include_router(notifications.router)

# Roles de Usuario por Empresa
api_router.include_router(user_roles.router)

# CRM Avanzado (Pipeline, Oportunidades, Seguimiento)
api_router.include_router(crm.router)

# Cuentas por Pagar (gestión de pagos, renegociación, exportación)
api_router.include_router(cuentas_pagar.router)

# Empleados (RRHH)
api_router.include_router(employees.router)

# Nómina / Rol de Pago
api_router.include_router(payroll.router)

# Nómina - Reportes SRI (RDEP, Anexos IESS, SUT XIII-XIV, IR)
api_router.include_router(payroll_reports.router)

# Nómina - Exportaciones (Bancos, PDF/Excel roles)
api_router.include_router(payroll_exports.router)

# Nómina - Asistencia y Turnos
api_router.include_router(attendance.router)

# Exportaciones
api_router.include_router(exports.router)

# Importaciones
api_router.include_router(imports.router)

# Kardex
api_router.include_router(kardex.router)

# Almacenamiento Volátil
api_router.include_router(volatile.router)

# Logs de Correo
api_router.include_router(email_logs.router)
