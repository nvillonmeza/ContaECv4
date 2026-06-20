
● 📋 PLAN MAESTRO - ContaEC 100%
  
  🎯 OBJETIVO: Completar el sistema contable según requerimientos

  ---
  FASE 0: CRÍTICO (Semana 1)

  Estos items bloquean el uso en producción

  ┌─────┬────────────────────────────────────────────────────────────┬─────────────────────────────────────────┬──────────────────────────────────────────────────────┐
  │  #  │                              Tarea                         │                Archivos                 │                 Criterio Aceptación                  │
  ├─────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ 0.1 │ Almacenamiento volátil - Limpieza automática de archivos   │ backend/app/core/cleanup.py, cron job   │ Archivos en /tmp se eliminan después de 1 hora       │
  │     │ temporales                                                 │                                         │                                                      │
  ├─────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ 0.2 │ Catálogos SRI completos - Todos los IVA                    │ backend/app/core/sri_catalogs.py        │ 0%, 5%, 8%, 12%, 13%, 14%, 15%, NO objeto, Exento    │
  ├─────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ 0.3 │ Códigos ICE - Tabla completa                               │ backend/app/core/sri_catalogs.py        │ Todos los códigos ICE del SRI                        │
  ├─────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ 0.4 │ Retenciones - Todas las tarifas                            │ backend/app/models/comprobante.py       │ 10%, 20%, 30%, 50%, 70%, 100%, 0%                    │
  ├─────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ 0.5 │ Estados comprobante                                        │ backend/app/models/comprobante.py       │ Autorizado, Anulado, Rechazado, Pendiente, Firmado   │
  ├─────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ 0.6 │ Tipos contribuyente                                        │ backend/app/models/company.py           │ NO obligado, Obligado, RIMPE Emprendedor, RIMPE      │
  │     │                                                            │                                         │ Popular                                              │
  ├─────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ 0.7 │ Verificar ClamAV                                           │ backend/app/api/v1/endpoints/uploads.py │ Escaneo real funciona en uploads                     │
  └─────┴────────────────────────────────────────────────────────────┴─────────────────────────────────────────┴──────────────────────────────────────────────────────┘

  ---
  FASE 1: NÓMINA RRHH COMPLETA (Semanas 2-3)

  Requerimiento 28 - Prioridad ALTA

  1.1 Modelos de RRHH Extendidos

  ┌──────────────────────────┬───────────────────────────────────┬─────────────────────────────────────────┐
  │          Tarea           │             Archivos              │                Detalles                 │
  ├──────────────────────────┼───────────────────────────────────┼─────────────────────────────────────────┤
  │ Modelo Contrato          │ backend/app/models/hr_contract.py │ Tipo contrato, fecha inicio/fin, estado │
  ├──────────────────────────┼───────────────────────────────────┼─────────────────────────────────────────┤
  │ Modelo Cargas Familiar   │ backend/app/models/hr_family.py   │ Hijos, cónyuge, padron                  │
  ├──────────────────────────┼───────────────────────────────────┼─────────────────────────────────────────┤
  │ Modelo Historial Laboral │ backend/app/models/hr_history.py  │ Ascensos, cambios salario               │
  ├──────────────────────────┼───────────────────────────────────┼─────────────────────────────────────────┤
  │ Modelo Vacaciones        │ backend/app/models/hr_vacation.py │ Días disponibles, tomados, pendientes   │
  ├──────────────────────────┼───────────────────────────────────┼─────────────────────────────────────────┤
  │ Modelo Préstamos         │ backend/app/models/hr_loan.py     │ Préstamos, descuentos mensuales         │
  └──────────────────────────┴───────────────────────────────────┴─────────────────────────────────────────┘

  1.2 Cálculos Automáticos

  ┌────────────────┬──────────────────────────────────────────┬──────────────────────────────────────────┐
  │     Tarea      │                 Archivos                 │                 Detalles                 │
  ├────────────────┼──────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Décimo Tercero │ backend/app/core/payroll_calculations.py │ Mensualizado o anual según configuración │
  ├────────────────┼──────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Décimo Cuarto  │ backend/app/core/payroll_calculations.py │ Sierra/Costa según región                │
  ├────────────────┼──────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Fondo Reserva  │ backend/app/core/payroll_calculations.py │ 8.33% tras 1 año                         │
  ├────────────────┼──────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Vacaciones     │ backend/app/core/payroll_calculations.py │ 15 días + 1 por año adicional            │
  ├────────────────┼──────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Horas Extras   │ backend/app/core/payroll_calculations.py │ 50% diurnas, 100% nocturnas              │
  ├────────────────┼──────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Utilidades     │ backend/app/core/payroll_calculations.py │ 15% empresa, 70% empleados               │
  ├────────────────┼──────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Liquidaciones  │ backend/app/core/payroll_liquidation.py  │ Cálculo completo por causal              │
  └────────────────┴──────────────────────────────────────────┴──────────────────────────────────────────┘

  1.3 Reportes SRI Nómina

  ┌────────────────┬─────────────────────────────────────────────────┬─────────────────────────┐
  │     Tarea      │                    Archivos                     │        Detalles         │
  ├────────────────┼─────────────────────────────────────────────────┼─────────────────────────┤
  │ RDEP           │ backend/app/api/v1/endpoints/payroll_reports.py │ XML según Ficha Técnica │
  ├────────────────┼─────────────────────────────────────────────────┼─────────────────────────┤
  │ Anexos IESS    │ backend/app/api/v1/endpoints/payroll_reports.py │ Batch upload            │
  ├────────────────┼─────────────────────────────────────────────────┼─────────────────────────┤
  │ SUT XIII-XIV   │ backend/app/api/v1/endpoints/payroll_reports.py │ Formato SRI             │
  ├────────────────┼─────────────────────────────────────────────────┼─────────────────────────┤
  │ Impuesto Renta │ backend/app/core/ir_calculation.py              │ Tablas vigentes 2026    │
  └────────────────┴─────────────────────────────────────────────────┴─────────────────────────┘

  1.4 Pagos Masivos

  ┌────────────────────┬─────────────────────────────────────────────────┬───────────────────────────────────────────────────┐
  │        Trea        │                    Archivos                     │                     Detalles                      │
  ├────────────────────┼─────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ Exportación bancos │ backend/app/api/v1/endpoints/payroll_exports.py │ Excel, CSV (Pichincha, Guayaquil, Pacífico, etc.) │
  ├────────────────────┼─────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ Excel/PDF roles    │ backend/app/api/v1/endpoints/payroll_exports.py │ Reporte detallado bruto/deducciones/neto          │
  └────────────────────┴─────────────────────────────────────────────────┴───────────────────────────────────────────────────┘

  1.5 Integración Asistencia

  ┌──────────────────┬────────────────────────────────────────────┬────────────────────┐
  │      Tarea       │                  Archivos                  │      Detalles      │
  ├──────────────────┼────────────────────────────────────────────┼────────────────────┤
  │ API biométricos  │ backend/app/api/v1/endpoints/attendance.py │ Importar registros │
  ├──────────────────┼────────────────────────────────────────────┼────────────────────┤
  │ Turnos rotativos │ backend/app/models/hr_shift.py             │ Gestión de turnos  │
  └──────────────────┴────────────────────────────────────────────┴────────────────────┘

  ✅ Criterio aceptación: Generar rol de pago completo + RDEP + archivo banco en 1 clic

  ---
  FASE 2: FACTURACIÓN ELECTRÓNICA COMPLETA (Semana 4)

  Requerimiento 75 - Prioridad ALTA

  ┌──────┬─────────────────────┬──────────────────────────────────────────────┬─────────────────────────────────────┐
  │  #   │        Tarea        │                   Archivos                   │         Criterio Aceptación         │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.1  │ Generación XML      │ backend/app/core/xml_generator.py            │ XML válido según Ficha Técnica v2.5 │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.2  │ Firma XAdES-BES     │ backend/app/core/xml_signer.py               │ signxml con certificado .p12        │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.3  │ Envío SRI SOAP      │ backend/app/core/sri_service.py              │ zeep con reintentos                 │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.4  │ Recepción respuesta │ backend/app/core/sri_service.py              │ Guardar número autorización         │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.5  │ RIDE PDF            │ backend/app/core/ride_generator.py           │ reportlab, formato SRI              │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.6  │ Email comprobante   │ backend/app/api/v1/endpoints/comprobantes.py │ Enviar con PDF adjunto              │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.7  │ Reprocesos          │ backend/app/api/v1/endpoints/comprobantes.py │ Reenviar, revertir estado           │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.8  │ Nota Crédito        │ backend/app/api/v1/endpoints/comprobantes.py │ Referência a comprobante original   │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.9  │ Nota Débito         │ backend/app/api/v1/endpoints/comprobantes.py │ Referência a comprobante original   │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.10 │ Guía Remisión       │ backend/app/api/v1/endpoints/comprobantes.py │ Transporte de bienes                │
  ├──────┼─────────────────────┼──────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 2.11 │ Retención           │ backend/app/api/v1/endpoints/comprobantes.py │ Retenciones IVA/IR automáticas      │
  └──────┴─────────────────────┴──────────────────────────────────────────────┴─────────────────────────────────────┘

  ✅ Criterio aceptación: Factura autorizada por SRI en < 2 minutos

  ---
  FASE 3: INVENTARIO Y KARDEX (Semana 5)

  Fase 4 requerimientos

  ┌─────┬───────────────────┬──────────────────────────────────────────┬─────────────────────────────┐
  │  #  │       Tarea       │                 Archivos                 │          Detalles           │
  ├─────┼───────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
  │ 3.1 │ Kardex valorado   │ backend/app/api/v1/endpoints/kardex.py   │ FIFO, LIFO, Precio Promedio │
  ├─────┼───────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
  │ 3.2 │ Movimientos       │ backend/app/models/kardex.py             │ Entradas, salidas, ajustes  │
  ├─────┼───────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
  │ 3.3 │ Importación Excel │ backend/app/api/v1/endpoints/imports.py  │ Productos masivos           │
  ├─────┼───────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
  │ 3.4 │ Exportación Excel │ backend/app/api/v1/endpoints/exports.py  │ Inventario valorado         │
  ├─────┼───────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
  │ 3.5 │ Exportación PDF   │ backend/app/api/v1/endpoints/exports.py  │ Kardex por producto         │
  ├─────┼───────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
  │ 3.6 │ Códigos barras    │ backend/app/api/v1/endpoints/products.py │ Generar e imprimir          │
  └─────┴───────────────────┴──────────────────────────────────────────┴─────────────────────────────┘

  ✅ Criterio aceptación: Importar 1000 productos desde Excel + ver kardex

  ---
  FASE 4: STUDIÓ SMTP Y CORREO (Semana 6)

  Fase 7 requerimientos

  ┌─────┬─────────────────────┬───────────────────────────────────────────────┬─────────────────────────────────┐
  │  #  │        Tarea        │                   Archivos                    │            Detalles             │
  ├─────┼─────────────────────┼───────────────────────────────────────────────┼─────────────────────────────────┤
  │ 4.1 │ Editor plantillas   │ src/components/email-template-editor.tsx      │ Preview HTML                    │
  ├─────┼─────────────────────┼───────────────────────────────────────────────┼─────────────────────────────────┤
  │ 4.2 │ Variables plantilla │ backend/app/models/email_template.py          │ {{razon_social}}, {{ruc}}, etc. │
  ├─────┼─────────────────────┼───────────────────────────────────────────────┼─────────────────────────────────┤
  │ 4.3 │ Logs envío          │ backend/app/models/email_log.py               │ Tracking envíos                 │
  ├─────┼─────────────────────┼───────────────────────────────────────────────┼─────────────────────────────────┤
  │ 4.4 │ Test SMTP           │ backend/app/api/v1/endpoints/smtp_profiles.py │ Verificar conexión              │
  └─────┴─────────────────────┴───────────────────────────────────────────────┴─────────────────────────────────┘

  ---
  FASE 5: COMPRAS Y PROVEEDORES (Semana 7)

  Fase 8 requerimientos

  ┌─────┬─────────────────────┬────────────────────────────────────────────────────┬───────────────────────┐
  │  #  │        Tarea        │                      Archivos                      │       Detalles        │
  ├─────┼─────────────────────┼────────────────────────────────────────────────────┼───────────────────────┤
  │ 5.1 │ Órdenes compra      │ backend/app/api/v1/endpoints/purchase_orders.py    │ Aprobación flujo      │
  ├─────┼─────────────────────┼────────────────────────────────────────────────────┼───────────────────────┤
  │ 5.2 │ Recepción           │ backend/app/api/v1/endpoints/receptions.py         │ mercadería            │
  ├─────┼─────────────────────┼────────────────────────────────────────────────────┼───────────────────────┤
  │ 5.3 │ Cuentas pagar       │ backend/app/api/v1/endpoints/cuentas_pagar.py      │ Gestión vencimientos  │
  ├─────┼─────────────────────┼────────────────────────────────────────────────────┼───────────────────────┤
  │ 5.4 │ Retenciones compras │ backend/app/api/v1/endpoints/retenciones_compra.py │ Generación automática │
  └─────┴─────────────────────┴────────────────────────────────────────────────────┴───────────────────────┘

  ---
  FASE 6: MULTI-ALMACÉN (Semana 8)

  Fase 9 requerimientos

  ┌─────┬──────────────────┬────────────────────────────────────────────────┬────────────────────┐
  │  #  │      Tarea       │                    Archivos                    │      Detalles      │
  ├─────┼──────────────────┼────────────────────────────────────────────────┼────────────────────┤
  │ 6.1 │ Transferencias   │ backend/app/api/v1/endpoints/transferencias.py │ Entre almacenes    │
  ├─────┼──────────────────┼────────────────────────────────────────────────┼────────────────────┤
  │ 6.2 │ Ubicaciones      │ backend/app/api/v1/endpoints/ubicaciones.py    │ Rack/estante/nivel │
  ├─────┼──────────────────┼────────────────────────────────────────────────┼────────────────────┤
  │ 6.3 │ Kardex detallado │ backend/app/api/v1/endpoints/kardex.py         │ Por almacén        │
  └─────┴──────────────────┴────────────────────────────────────────────────┴────────────────────┘

  ---
  FASE 7: PUNTO DE VENTA (Semanas 9-10)

  Fase 10 requerimientos

  ┌─────┬────────────────────┬──────────────────────────────────────────────┬─────────────────────────┐
  │  #  │       Tarea        │                   Archivos                   │        Detalles         │
  ├─────┼────────────────────┼──────────────────────────────────────────────┼─────────────────────────┤
  │ 7.1 │ Interfaz táctil    │ src/components/pos/pos-terminal.tsx          │ Botones grandes, rápido │
  ├─────┼────────────────────┼──────────────────────────────────────────────┼─────────────────────────┤
  │ 7.2 │ Escáner            │ src/components/pos/pos-scanner.tsx           │ Lector códigos barras   │
  ├─────┼────────────────────┼──────────────────────────────────────────────┼─────────────────────────┤
  │ 7.3 │ Impresión          │ backend/app/api/v1/endpoints/pos_printing.py │ Tickets 80mm            │
  ├─────┼────────────────────┼──────────────────────────────────────────────┼─────────────────────────┤
  │ 7.4 │ Arqueo             │ backend/app/api/v1/endpoints/pos_cashier.py  │ Apertura/cierre caja    │
  ├─────┼────────────────────┼──────────────────────────────────────────────┼─────────────────────────┤
  │ 7.5 │ Facturación rápida │ src/components/pos/pos-invoice.tsx           │ Flujo retail            │
  └─────┴────────────────────┴──────────────────────────────────────────────┴─────────────────────────┘

  ---
  FASE 8: BUSINESS INTELLIGENCE (Semana 11)

  Fase 11 requerimientos

  ┌─────┬───────────────────┬────────────────────────────────────────────┬──────────────────────────┐
  │  #  │       Tarea       │                  Archivos                  │         Detalles         │
  ├─────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────┤
  │ 8.1 │ KPIs tiempo real  │ backend/app/api/v1/endpoints/bi_kpis.py    │ Ventas, compras, cartera │
  ├─────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────┤
  │ 8.2 │ Dashboards        │ src/components/bi-dashboard.tsx            │ Recharts gráficos        │
  ├─────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────┤
  │ 8.3 │ Alertas           │ backend/app/core/alerts.py                 │ Stock bajo, vencimientos │
  ├─────┼───────────────────┼────────────────────────────────────────────┼──────────────────────────┤
  │ 8.4 │ Exportar Power BI │ backend/app/api/v1/endpoints/bi_exports.py │ Conexión directa         │
  └─────┴───────────────────┴────────────────────────────────────────────┴──────────────────────────┘

  ---
  FASE 9: PRESUPUESTOS (Semana 12)

  Fase 12 requerimientos

  ┌─────┬───────────────────┬─────────────────────────────────────────┬─────────────────────────┐
  │  #  │       Tarea       │                Archivos                 │        Detalles         │
  ├─────┼───────────────────┼─────────────────────────────────────────┼─────────────────────────┤
  │ 9.1 │ Presupuesto anual │ backend/app/api/v1/endpoints/budgets.py │ Por cuenta contable     │
  ├─────┼───────────────────┼─────────────────────────────────────────┼─────────────────────────┤
  │ 9.2 │ Ejecución mensual │ backend/app/api/v1/endpoints/budgets.py │ Comparativo vs real     │
  ├─────┼───────────────────┼─────────────────────────────────────────┼─────────────────────────┤
  │ 9.3 │ Alertas sobregiro │ backend/app/core/budget_alerts.py       │ Notificación 80% límite │
  └─────┴───────────────────┴─────────────────────────────────────────┴─────────────────────────┘

  ---
  FASE 10: CRM AVANZADO (Semana 13)

  Fase 13 requerimientos

  ┌──────┬─────────────────┬────────────────────────────────────────────┬─────────────────────────┐
  │  #   │      Tarea      │                  Archivos                  │        Detalles         │
  ├──────┼─────────────────┼────────────────────────────────────────────┼─────────────────────────┤
  │ 10.1 │ Pipeline ventas │ src/components/crm-pipeline.tsx            │ Drag-drop oportunidades │
  ├──────┼─────────────────┼────────────────────────────────────────────┼─────────────────────────┤
  │ 10.2 │ Cotizaciones    │ backend/app/api/v1/endpoints/quotations.py │ Conversión a factura    │
  ├──────┼─────────────────┼────────────────────────────────────────────┼─────────────────────────┤
  │ 10.3 │ Automatización  │ backend/app/core/crm_automation.py         │ Seguimiento automático  │
  └──────┴─────────────────┴────────────────────────────────────────────┴─────────────────────────┘

  ---
  FASE 11: PROYECTOS (Semana 14)

  Fase 14 requerimientos

  ┌──────┬──────────────┬───────────────────────────────────────────────────────┬────────────────────┐
  │  #   │    Tarea     │                       Archivos                        │      Detalles      │
  ├──────┼──────────────┼───────────────────────────────────────────────────────┼────────────────────┤
  │ 11.1 │ Timesheet    │ backend/app/api/v1/endpoints/timesheets.py            │ Registro horas     │
  ├──────┼──────────────┼───────────────────────────────────────────────────────┼────────────────────┤
  │ 11.2 │ Rentabilidad │ backend/app/api/v1/endpoints/project_profitability.py │ Costos vs ingresos │
  └──────┴──────────────┴───────────────────────────────────────────────────────┴────────────────────┘

  ---
  FASE 12: INTEGRACIONES (Semana 15)

  Fase 15 requerimientos

  ┌──────┬─────────────┬─────────────────────────────────────────────┬──────────────────────────┐
  │  #   │    Tarea    │                  Archivos                   │         Detalles         │
  ├──────┼─────────────┼─────────────────────────────────────────────┼──────────────────────────┤
  │ 12.1 │ Bancos      │ backend/app/api/v1/endpoints/banking.py     │ Extractos CSV            │
  ├──────┼─────────────┼─────────────────────────────────────────────┼──────────────────────────┤
  │ 12.2 │ Shopify     │ backend/app/api/v1/endpoints/shopify.py     │ Pedidos → Facturas       │
  ├──────┼─────────────┼─────────────────────────────────────────────┼──────────────────────────┤
  │ 12.3 │ WooCommerce │ backend/app/api/v1/endpoints/woocommerce.py │ Sincronización productos │
  └──────┴─────────────┴─────────────────────────────────────────────┴──────────────────────────┘

  ---
  FASE 13: ML/IA (Semana 16)

  Fase 16 requerimientos

  ┌──────┬───────────────────┬───────────────────────────────────────────────────┬──────────────────────┐
  │  #   │       Tarea       │                     Archivos                      │       Detalles       │
  ├──────┼───────────────────┼───────────────────────────────────────────────────┼──────────────────────┤
  │ 13.1 │ Predicción ventas │ backend/app/api/v1/endpoints/ml_forecasting.py    │ Prophet/scikit-learn │
  ├──────┼───────────────────┼───────────────────────────────────────────────────┼──────────────────────┤
  │ 13.2 │ Detección fraude  │ backend/app/api/v1/endpoints/ml_fraud.py          │ Anomalías            │
  ├──────┼───────────────────┼───────────────────────────────────────────────────┼──────────────────────┤
  │ 13.3 │ Categorización    │ backend/app/api/v1/endpoints/ml_categorization.py │ Asientos automáticos │
  ├──────┼───────────────────┼───────────────────────────────────────────────────┼──────────────────────┤
  │ 13.4 │ Chatbot           │ src/components/support-chatbot.tsx                │ FAQ contables        │
  └──────┴───────────────────┴───────────────────────────────────────────────────┴──────────────────────┘

  ---
  📊 RESUMEN POR PRIORIDAD

  ┌────────────┬────────────┬─────────┬────────────────────────────┐
  │ Prioridad  │   Fases    │ Semanas │          Impacto           │
  ├────────────┼────────────┼─────────┼────────────────────────────┤
  │ 🔴 CRÍTICO │ Fase 0     │ 1       │ Bloquea producción         │
  ├────────────┼────────────┼─────────┼────────────────────────────┤
  │ 🟠 ALTA    │ Fases 1-3  │ 6       │ Requisito legal SRI + RRHH │
  ├────────────┼────────────┼─────────┼────────────────────────────┤
  │ 🟡 MEDIA   │ Fases 4-8  │ 5       │ Funcionalidad completa     │
  ├────────────┼────────────┼─────────┼────────────────────────────┤
  │ 🟢 BAJA    │ Fases 9-13 │ 5       │ Valor agregado             │
  └────────────┴────────────┴─────────┴────────────────────────────┘

  TOTAL: 17 semanas (~4 meses)

  ---
  🚀 PRÓXIMOS PASOS INMEDIATOS

  1. Hoy: Crear backend/app/core/cleanup.py para archivos temporales
  2. Esta semana: Completar catálogos SRI (punto 75 requerimientos)
  3. Semana siguiente: Empezar Fase 1 - Nómina RRHH

  ¿Quieres que empiece con el Paso 0.1 (almacenamiento volátil)?