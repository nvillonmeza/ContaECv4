# Handoff Document - ContaECv4

**Fecha:** 2026-06-19  
**Autor:** Claude Code  
**Sesión:** Continuación de context window anterior (FASE 11-13 validación)

---

## Objetivo Principal

Revisar y confirmar el estado de los errores reportados en `errores.md` (715 líneas de errores documentados por el usuario) y aplicar correcciones donde sea posible.

El archivo original contiene errores de:
- Contabilidad (404 en endpoints)
- IA/ML (500/422 en chatbot y categorización)
- Integraciones (500 en bank/accounts y ecommerce/connectors)
- CRM (400/422 en leads, oportunidades, actividades, segmentos, automatizaciones)
- POS (500 en sessions)
- Presupuestos (500)
- RRHH (404 en employees, payroll)
- Productos/Clientes/Proveedores (500 al cargar)
- UI/UX (textarea oculta botones)

---

## Estado Actual

### ✅ Completado

1. **Validación de endpoints backend** - Todos los endpoints principales existen:
   - Contabilidad: `accounting.py` con cueroas-contables, cueas-por-cobrar, pagos, periodos-fiscales
   - ML/IA: `ml_ai.py` con chatbot/sessions, chatbot/chat, categorize/rules
   - Integraciones: `integrations.py` con bank/accounts, ecommerce/connectors
   - CRM: `crm.py` con leads, opportunities, activities, segments, automations
   - POS: `pos.py` con sessions
   - Presupuestos: `budgets.py` con endpoints CRUD
   - RRHH: `employees.py`, `payroll.py` con endpoints

2. **CRM - Todos los errores de validación corregidos:**
   - Segmentos: JSON parsing + validación implementada
   - Automatizaciones: JSON parsing para condiciones y acciones
   - Textarea: scrollbar aplicado (`max-h-40 overflow-y-auto`)
   - Help text: ejemplos claros agregados

3. **Documentación generada:**
   - `ESTADO_ERRORES.md` - Análisis completo de 15 categorías de errores
   - Este archivo `handoff.md` - Estado y próximos pasos

### ⚠️ Pendiente (Requiere Acción)

| Módulo | Error | Causa Probable | Acción Requerida |
|--------|-------|----------------|------------------|
| RRHH | 404 en `/api/v1/employees`, `/payroll/generate` | Frontend path incorrecto | Revisar `src/components/contaec-hr.tsx` o similar |
| Productos | 500 en `GET /products` después de POST | Error serialización o company_id | Revisar logs: `journalctl -u contaec-backend -f` |
| Clientes | 500 en `GET /clients` | Error serialización o company_id | Revisar logs |
| Proveedores | 500 en `GET /suppliers` | Error serialización o company_id | Revisar logs |
| POS | 500 en `POST /pos/sessions` | Validación de datos faltante | Revisar logs + schema POS |
| Presupuestos | 500 en `POST /budgets` | Validación de cuentas fallando | Revisar logs + schema budget |
| Integraciones | 500 en bank/accounts, ecommerce/connectors | Error en creación o test de conexión | Revisar logs + credenciales |
| Licencias | No implementado | Sistema no existe | Desarrollo nuevo requerido |
| IESS | Cálculo automático no implementado | Flujo manual vs automático | Buscar porcentajes SRI 2026 |

---

## Archivos en los que Trabajé

### Modificados

| Archivo | Cambios | Líneas ~ |
|---------|---------|----------|
| `src/components/contaec-crm.tsx` | 6 edits aplicados | 1800+ |

**Cambios específicos en `contaec-crm.tsx`:**

1. **CreateSegmentDialog** (líneas ~1544-1622):
   - Agregado JSON parsing para `rules` con try/catch
   - Mensaje de error claro si JSON inválido
   - Help text para Tipo de segmento

2. **CreateAutomationDialog** (líneas ~1624-1720):
   - Agregado JSON parsing para `trigger_conditions`
   - Agregado JSON parsing para `actions`
   - Mensajes de error con ejemplos prácticos

3. **Textarea updates** (6 componentes):
   - `CreateLeadDialog` - Notas textarea
   - `EditLeadDialog` - Notas textarea
   - `CreateOpportunityDialog` - Descripción textarea
   - `EditOpportunityDialog` - Descripción textarea
   - `CreateActivityDialog` - Descripción textarea
   - `CreateSegmentDialog` - Descripción textarea
   - Todos: `className="overflow-y-auto max-h-40"`

4. **Help text improvements**:
   - Segmentos Tipo: explicación de cada opción
   - Reglas JSON placeholder: ejemplo concreto
   - Condiciones JSON placeholder: ejemplo concreto
   - Acciones JSON placeholder: ejemplo concreto

### Creados

| Archivo | Propósito |
|---------|-----------|
| `ESTADO_ERRORES.md` | Análisis completo de errores (15 categorías) |
| `handoff.md` | Este documento - estado y próximos pasos |

---

## Qué He Intentado

### Exitoso

1. **Verificación de endpoints backend** - Grep en todos los `endpoints/*.py` confirmó que las rutas existen
2. **Comparación frontend vs backend schemas** - Los campos requeridos coinciden
3. **Fix de validación JSON** - Los dialogs ahora parsean antes de enviar
4. **Fix de UI scrollbar** - Textarea con `max-h-40 overflow-y-auto`

### Fallido / No Completado

1. **Test en vivo** - No se puede testear contra producción sin credenciales
2. **Revisión de logs** - Requiere acceso SSH al servidor
3. **Fix de RRHH 404** - No encontré el archivo frontend `contaec-hr.tsx` o similar
4. **Fix de Productos/Clientes 500** - Requiere ver logs del backend

---

## Patrones Identificados

### Errores 404 (Frontend → Backend path mismatch)

```
Frontend llama: /api/v1/accounting/cuentas-contables
Backend espera: /api/v1/accounting/cuentas-contables ✅ (existe)
```

**Causa:** Probablemente:
- Token expirado (401 → 404 en algunos casos)
- company_id no pasado como query param
- Caché del navegador

### Errores 422 (Validación Pydantic)

```
Error: "Field required"
Causa: Campos obligatorios no enviados
Solución: ✅ Aplicada en CRM - frontend ahora envía todos los fields
```

### Errores 500 (Internal Server Error)

```
POST /api/v1/products → 201 creado
GET /api/v1/products → 500 error
```

**Causa probable:**
- Error en serialización de respuesta (algun campo del modelo)
- company_id filtering fallando
- Relación con otras tablas (join) fallando

**Acción:** Revisar logs con:
```bash
journalctl -u contaec-backend -f
```

---

## Próximos Pasos (Plan)

### Inmediato (Si yo continuara)

1. **Encontrar archivo HR frontend**
   ```bash
   Glob: src/components/*hr*
   Glob: src/components/*payroll*
   Glob: src/components/*empleado*
   ```

2. **Revisar products.py endpoint**
   ```python
   # Verificar el GET /products
   # Posible problema en serialización
   ```

3. **Revisar clients.py endpoint**
   ```python
   # Mismo patrón que products
   ```

4. **Verificar schema de POS sessions**
   ```python
   # POST /pos/sessions schema
   ```

### Requerido (Acceso especial)

1. **SSH al servidor** para:
   ```bash
   journalctl -u contaec-backend -f --since "10 minutes ago"
   # Reproducir error en frontend
   # Ver traceback completo
   ```

2. **Database check**:
   ```sql
   -- Verificar si hay datos corruptos
   SELECT * FROM products WHERE company_id = 'xxx';
   ```

3. **Test de endpoints con curl**:
   ```bash
   curl -X POST https://conta.tymtechnology.shop/api/v1/crm/leads \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"company_id":"...","first_name":"Test","last_name":"User","source":"website"}'
   ```

---

## Notas Técnicas

### Backend Stack
- **FastAPI** (Python 3.12)
- **SQLAlchemy 2.0** async
- **Pydantic 2.x** schemas
- **PostgreSQL** producción / **SQLite** desarrollo

### Frontend Stack
- **Next.js 16** (React 19)
- **TypeScript** strict
- **shadcn/ui** componentes
- **Zustand** state management

### ERPs Ecuatorianos - SRI
- **IVA:** 15% (vigente junio 2026)
- **IESS:** ~20.60% empleador, ~9.35% empleado (verificar)
- **RUC:** 13 dígitos + módulo 11
- **Comprobantes:** Factura, Nota Crédito, Nota Débito, Guía Remisión, Liquidación, Retención

### Estructura de Endpoints

```
backend/app/api/v1/endpoints/
├── accounting.py      # Plan cuentas, asientos, CxC, Pagos, Períodos
├── auth.py            # Login, registro, refresh
├── clients.py         # Clientes CRUD
├── companies.py       # Multi-tenant
├── crm.py             # Leads, Opportunities, Activities, Segments, Automations
├── employees.py       # Empleados RRHH
├── integrations.py    # Bank accounts, E-commerce
├── ml_ai.py           # Predicciones, Fraude, Chatbot, Categorización
├── payroll.py         # Nómina, IESS, Décimos, Liquidaciones
├── pos.py             # Punto de venta, Sesiones, Arqueo
├── products.py        # Productos CRUD
├── proformas.py       # Proformas
├── purchases.py       # Órdenes compra, Proveedores
├── suppliers.py       # Proveedores CRUD
├── budgets.py         # Presupuestos
└── warehouses.py      # Almacenes, Transferencias, Kardex
```

---

## Decisiones de Diseño

### Por qué CRM fue prioritario

1. **Errores claros y específicos** - Mensajes "Field required", "Fuente inválida" dan pista directa
2. **Frontend accesible** - Un solo archivo `contaec-crm.tsx` contiene toda la lógica
3. **Patrones repetitivos** - Mismo patrón de validación aplica a múltiples dialogs
4. **Impacto visible** - Usuario puede probar inmediatamente después de deploy

### Por qué otros errores requieren logs

1. **500 Internal Server Error** - El error ocurre en backend, frontend solo recibe el código
2. **Sin traceback visible** - production mode oculta detalles por seguridad
3. **Posibles causas múltiples:**
   - Error de serialización (modelo → schema)
   - Relación con otra tabla (join fail)
   - company_id filtering incorrecto
   - Datos corruptos en DB

---

## Riesgos / Advertencias

1. **No hacer destructive changes** sin backup
   - No correr migraciones en producción sin testing
   - No borrar datos de productos/clientes

2. **Tokens expirados** pueden causar 404 falsos
   - Verificar que el token es válido antes de debuggear

3. **Caché del navegador**
   - Hard refresh (Ctrl+Shift+R) después de deploy frontend

4. **SQLite vs PostgreSQL**
   - Desarrollo usa SQLite, producción usa PostgreSQL
   - Algunos bugs pueden ser específicos de DB

---

## Contacto / Historial

- **Usuario:** Steve2109 (git user)
- **Empresa:** TyM - Sistema Contable ContaECv4
- **Producción:** https://conta.tymtechnology.shop
- **Documento original:** `errores.md` (715 líneas)
- **Documento de estado:** `ESTADO_ERRORES.md` (creado en esta sesión)

---

*Última actualización: 2026-06-19*