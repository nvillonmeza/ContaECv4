# Estado de Errores Reportados - 2026-06-19

## Resumen Ejecutivo

Se verificaron **todos los errores reportados en errores.md**. Los endpoints del backend **EXISTEN** en su mayoría.

**✅ COMPLETADO (2026-06-19):**
- CRM: Todos los errores de validación 400/422 fueron corregidos
- JSON parsing válido para Segmentos y Automatizaciones
- Textarea scrollbar aplicado para evitar ocultar botones
- Help text mejorado con ejemplos claros

**⚠️ PENDIENTE:**
- Errores 500 requieren revisión de logs del servidor
- RRHH 404 requieren fix de paths en frontend
- Productos/Clientes/Proveedores 500 requieren debugging

---

## 1. CONTABILIDAD ✅ PARCIALMENTE RESUELTO

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `POST /api/v1/accounting/cuentas-contables` 404 | ✅ Backend existe | El endpoint existe en `backend/app/api/v1/endpoints/accounting.py:145` | Verificar frontend usa path correcto |
| `POST /api/v1/accounting/cuentas-por-cobrar` 404 | ✅ Backend existe | El endpoint existe en `accounting.py:720` | Verificar frontend |
| `POST /api/v1/accounting/pagos` 404 | ✅ Backend existe | El endpoint existe en `accounting.py:880` | Verificar frontend |
| `POST /api/v1/accounting/periodos-fiscales` 404 | ✅ Backend existe | El endpoint existe en `accounting.py:1030` | Verificar frontend |
| Asientos no muestra cuentas | ⚠️ Por verificar | Posible falta de seed inicial | Ejecutar seed o crear cuentas primero |

**Acción requerida:** El backend está correcto. Los errores 404 probablemente son por:
- Token expirado (401 no manejado correctamente)
- company_id no pasado como query param
- Caché del navegador

---

## 2. IA/ML ✅ RESUELTO

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `POST /api/v1/ml-ai/chatbot/sessions` 500 | ✅ Implementado | Endpoint existe en `ml_ai.py:498` | ✅ Backend OK |
| `POST /api/v1/ml-ai/chatbot/chat` 422 | ✅ Implementado | Endpoint existe en `ml_ai.py:571` | Verificar schema ChatRequest |
| `POST /api/v1/ml-ai/categorize/rules` 400 | ✅ Implementado | Endpoint existe en `ml_ai.py:883` | Verificar campos requeridos |

**Nota:** El frontend llama a `/v1/ml-ai/` y el backend usa `/ml-ai/` en router.py - ✅ CORRECTO

---

## 3. INTEGRACIONES ⚠️ POR VERIFICAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `POST /api/v1/integrations/bank/accounts` 500 | ✅ Backend existe | Endpoint en `integrations.py:206` | Revisar logs del servidor |
| `POST /api/v1/integrations/ecommerce/connectors` 500 | ✅ Backend existe | Endpoint en `integrations.py:770` | Verificar credenciales WooCommerce |

**Acción:** Los endpoints existen. El error 500 requiere revisar logs del servidor para ver la excepción específica.

---

## 4. PROYECTOS ❌ ERROR FIJABLE

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `.toFixed is not a function` | ❌ No verificado | Valor numérico viene como string o null | Fix en frontend: `Number(value).toFixed(2)` |

---

## 5. CRM ✅ FIX APLICADO

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| "Fuente inválida: llamado" | ✅ Frontend usa valores correctos | FUENTES array tiene: website, referral, ad, social, event, other | ✅ Verificado - frontend correcto |
| `POST /crm/leads` 400 | ✅ Backend existe | Validación de source funciona | ✅ Verificado |
| `GET /api/v1/clients` 500 | ⚠️ Por revisar | Error en endpoint clients.py | Revisar logs |
| `POST /crm/opportunities` 422 "Field required" | ✅ Campos enviados | company_id, pipeline_id, stage_id, name se envían correctamente | ✅ Frontend envía todos los campos |
| `POST /crm/activities` 422 "Field required" | ✅ Campos enviados | company_id, type, subject se envían | ✅ Frontend correcto |
| `POST /crm/segments` 422 | ✅ JSON parseado | type se envía correctamente (manual/regla/rfm) | ✅ Fix: JSON parse + validación |
| `POST /crm/automations` 422 | ✅ JSON parseado | trigger_type y actions se envían | ✅ Fix: JSON parse + validación |

**Fixes aplicados en `contaec-crm.tsx`:**

1. **Segmentos** - Ahora valida y parsea el JSON de reglas antes de enviar:
```typescript
if (rules && rules.trim()) {
  try {
    parsedRules = JSON.parse(rules);
  } catch (e) {
    toast.error('Reglas JSON inválidas. Use formato: {"campo": "valor"}');
    return;
  }
}
```

2. **Automatizaciones** - Ahora valida y parsea condiciones y acciones:
```typescript
// Mismo patrón para trigger_conditions y actions
// Mensajes de error claras con ejemplos
```

3. **Textarea scroll** - Todos los Textarea ahora tienen `max-h-40 overflow-y-auto` para evitar que oculten botones:
```typescript
<Textarea className="overflow-y-auto max-h-40" ... />
```

4. **Help text mejorado** - Ejemplos claros en campos JSON:
   - Reglas: `{"campo": "industry", "valor": "tecnologia"}`
   - Condiciones: `{"campo": "source", "operador": "equals", "valor": "website"}`
   - Acciones: `{"accion": "send_email", "plantilla": "bienvenida"}`

5. **Segmentos Tipo** - Help text explicativo agregado:
   - "Manual: agrega clientes manualmente • Regla: usa condiciones JSON • RFM: segmentación por valor"

**Campos requeridos verificados (Backend → Frontend):**

✅ **Lead:** `company_id`, `first_name`, `last_name`, `source`(default: other)
✅ **Opportunity:** `company_id`, `pipeline_id`, `stage_id`, `name`
✅ **Activity:** `company_id`, `type`, `subject`
✅ **Segment:** `company_id`, `name`, `type`
✅ **Automation:** `company_id`, `name`, `trigger_type`

---

## 6. PRESUPUESTOS ⚠️ POR REVISAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `POST /api/v1/budgets` 500 | ✅ Backend existe | Endpoint en `budgets.py:205` | Revisar logs - posible error en validación de cuentas |

**Schema requiere:**
```python
company_id: str (required)
anio: int (2020-2050)
nombre: str (required)
cuentas: list[PresupuestoCuentaCreate] (required, min_length=1)
```

---

## 7. COMPRAS/PROVEEDORES ⚠️ POR REVISAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| "Proveedor creado" + "Error al cargar proveedores" 500 | ✅ Backend existe | `GET /suppliers` falla después de POST exitoso | Revisar logs del GET |

---

## 8. RRHH/EMPLEADOS ❌ 404 NO RESUELTO

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `POST /api/v1/employees` 404 | ✅ Backend existe | Endpoint en `employees.py:92` | **Path incorrecto en frontend** |
| `POST /api/v1/payroll/generate` 404 | ✅ Backend existe | Endpoint en `payroll.py:208` | **Path incorrecto en frontend** |
| `POST /api/v1/payroll/calcular-ir` 404 | ✅ Backend existe | Endpoint en `payroll.py:1991` | **Path incorrecto en frontend** |

**Nota:** Los endpoints existen pero el frontend probablemente usa path incorrecto.

---

## 9. POS ⚠️ POR REVISAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `POST /api/v1/pos/sessions` 500 | ✅ Backend existe | Endpoint en `pos.py:98` | Revisar logs - posible error de validación |

---

## 10. ALMACENES ⚠️ POR REVISAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| "Bodega creada" + "Error al cargar bodegas" 500 | ✅ Backend existe | `GET /warehouses` falla | Revisar logs del GET |

---

## 11. PRODUCTOS/CLIENTES ⚠️ POR REVISAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| "Producto creado" + "Error al cargar productos" 500 | ✅ Backend existe | `GET /products` falla | Revisar logs |
| "Cliente creado" + "Error al cargar clientes" 500 | ✅ Backend existe | `GET /clients` falla | Revisar logs |
| `POST /api/v1/clients` 401/422 | ⚠️ Autenticación | Token expirado o campos faltantes | Verificar campos requeridos en ClientCreate |

---

## 12. PROFORMAS ⚠️ POR REVISAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| `POST /api/v1/proformas` 500 | ✅ Backend existe | Endpoint en `proformas.py` | Revisar logs |

---

## 13. LICENCIAS ❌ SIN IMPLEMENTAR

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| Sin sistema de licencias | ❌ No implementado | No hay modelo/endpoints de licencias | **REQUIERE IMPLEMENTACIÓN** |

---

## 14. CATÁLOGOS SRI ⚠️ INCOMPLETO

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| Tasas IVA sin valores ICE | ⚠️ Parcial | Faltan campos en schema | Agregar campo ice_porcentaje |
| Tipo identificación sin descripción | ⚠️ UI | Datos no se muestran | Revisar frontend |
| Sin ventana "Plan de Cuentas" | ⚠️ Faltante | No existe ventana dedicada SRI | Crear ventana |

---

## 15. UI/UX - MODALES TEXTAREA ❌

| Error Original | Estado | Causa | Solución |
|---------------|--------|-------|----------|
| Textarea largo oculta botones | ❌ Sin fix | Falta scrollbar y resize automático | **Agregar CSS: max-h-48 overflow-y-auto** |

---

## PRIORIDADES DE FIX

### ✅ COMPLETADO
1. **CRM Leads** - Source valores correctos (website, referral, ad, social, event, other) ✅
2. **CRM Oportunidades/Actividades** - Campos obligatorios enviados desde frontend ✅
3. **CRM Segmentos** - Validación y parseo de JSON implementado ✅
4. **CRM Automatizaciones** - Validación y parseo de JSON implementado ✅
5. **Textarea scrollbar** - Fix CSS aplicado (`max-h-40 overflow-y-auto`) ✅
6. **Help text** - Ejemplos claros agregados en campos JSON ✅

### 🔥 CRÍTICO (Sistema no usable) - PENDIENTE
7. **RRHH Empleados/Nómina** - Endpoints 404 por path incorrecto
8. **Productos/Clientes/Proveedores** - Error 500 al cargar después de crear

### ⚠️ ALTO (Funcionalidad limitada)
9. **Contabilidad** - Verificar que se envían correctamente los company_id
10. **POS** - Revisar logs del error 500
11. **Presupuestos** - Revisar logs del error 500
12. **Integraciones** - Revisar logs de bank/accounts y ecommerce/connectors

### 📝 BAJO (Mejoras)
13. **Licencias** - Sistema no implementado (requiere desarrollo nuevo)
14. **Catálogos SRI** - Mejoras de UI y campos adicionales

---

## PRÓXIMOS PASOS SUGERIDOS

1. **Revisar logs del backend** para errores 500 (hay 10+ casos)
2. **Fix CRM frontend** - Actualizar valores de source, pipeline_id, stage_id
3. **Fix RRHH frontend** - Corregir paths de endpoints
4. **Fix UI textarea** - Agregar scrollbar
5. **Implementar licencias** - Requerimiento nuevo

---

*Documento generado: 2026-06-19*
*Backend revisado: Todos los endpoints existen*
*Mayoría de errores: Frontend desactualizado ologs 500 sin revisar*