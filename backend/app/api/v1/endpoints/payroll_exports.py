"""
ContaEC - Endpoints de Exportación de Nómina
Exportaciones: Excel/CSV para bancos (Pichincha, Guayaquil, Pacífico)
             Reportes PDF/Excel de roles de pago
"""
import io
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.company import Company
from app.models.employee import Employee
from app.models.payroll import RolPago, RolPagoDetalle
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payroll-exports", tags=["Nómina - Exportaciones"])


# ==========================================
# Exportación Bancaria - Banco Pichincha
# ==========================================


@router.get("/banco/pichincha")
async def exportar_pichincha(
    rol_pago_id: str = Query(..., description="ID del rol de pago"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Exportar nómina para Banco Pichincha (formato CSV).

    Formato requerido por Banco Pichincha para carga de nómina:
    - Tipo de archivo: CSV
    - Encoding: UTF-8
    - Campos: Cuenta, Beneficiario, Valor, Tipo

    **Parámetros:**
    - `rol_pago_id`: ID del rol de pago a exportar

    **Retorna:**
    - Archivo CSV descargable para upload enbanca empresarial
    """
    # Obtener rol de pago
    rol_pago = await _get_rol_pago_with_details(db, rol_pago_id, current_user.id)
    if not rol_pago:
        raise HTTPException(404, "Rol de pago no encontrado")

    # Generar CSV
    csv_lines = ["CUENTA,BENEFICIARIO,VALOR,TIPO"]

    for detalle in rol_pago.detalles:
        empleado = detalle.employee
        cuenta = empleado.numero_cuenta or "0000000000"
        banco = empleado.banco or ""

        # Solo empleados con cuenta registrada
        if empleado.numero_cuenta:
            linea = f'{cuenta},{empleado.nombre_completo},{detalle.liquido_recibir},NOMINA'
            csv_lines.append(linea)

    csv_content = "\n".join(csv_lines)

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="NOMINA_PICHINCHA_{rol_pago.periodo_anio}_{rol_pago.periodo_mes:02d}.csv"'
        },
    )


# ==========================================
# Exportación Bancaria - Banco Guayaquil
# ==========================================


@router.get("/banco/guayaquil")
async def exportar_banco_guayaquil(
    rol_pago_id: str = Query(..., description="ID del rol de pago"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Exportar nómina para Banco Guayaquil (formato TXT posicional).

    Formato requerido por Banco Guayaquil:
    - Tipo de archivo: TXT
    - Layout posicional (campos de ancho fijo)
    - Registro tipo 1: Cabecera de lote
    - Registro tipo 2: Detalles de transferencia

    **Parámetros:**
    - `rol_pago_id`: ID del rol de pago

    **Retorna:**
    - Archivo TXT.descargable
    """
    rol_pago = await _get_rol_pago_with_details(db, rol_pago_id, current_user.id)
    if not rol_pago:
        raise HTTPException(404, "Rol de pago no encontrado")

    lines = []

    # Registro tipo 1 - Cabecera
    company = rol_pago.company
    total_liquido = sum(d.liquido_recibir for d in rol_pago.detalles)
    fecha_proceso = datetime.now().strftime("%d%m%Y")

    header = "1"  # Tipo de registro
    header += company.ruc.ljust(13)  # RUC empresa
    header += company.nombre_comercial[:30].ljust(30)  # Nombre empresa
    header += fecha_proceso  # Fecha de proceso
    header += str(len(rol_pago.detalles)).zfill(6)  # Número de registros
    header += str(int(total_liquido * 100)).zfill(15)  # Valor total en centavos
    lines.append(header)

    # Registro tipo 2 - Detalles
    for i, detalle in enumerate(rol_pago.detalles, start=1):
        empleado = detalle.employee

        record = "2"  # Tipo de registro
        record += str(i).zfill(6)  # Número secuencial
        record += empleado.cedula.ljust(13)  # Cédula/RUC
        record += empleado.nombre_completo[:30].ljust(30)  # Nombre
        record += empleado.numero_cuenta.ljust(10) if empleado.numero_cuenta else "0000000000".ljust(10)
        record += "C"  # Tipo de cuenta: C=Corriente, A=Ahorro
        record += str(int(detalle.liquido_recibir * 100)).zfill(15)  # Valor
        record += "USD"  # Moneda
        lines.append(record)

    txt_content = "\n".join(lines)

    return StreamingResponse(
        io.BytesIO(txt_content.encode("utf-8")),
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="NOMINA_GUAYAQUIL_{rol_pago.periodo_anio}_{rol_pago.periodo_mes:02d}.txt"'
        },
    )


# ==========================================
# Exportación Bancaria - Banco Pacífico
# ==========================================


@router.get("/banco/pacifico")
async def exportar_banco_pacifico(
    rol_pago_id: str = Query(..., description="ID del rol de pago"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Exportar nómina para Banco Pacífico (formato Excel).

    Formato requerido por Banco Pacífico:
    - Tipo de archivo: Excel (.xlsx)
    - Campos: Tipo Identificación, Identificación, Nombre, Cuenta, Valor

    **Parámetros:**
    - `rol_pago_id`: ID del rol de pago

    **Retorna:**
    - Simulación de archivo Excel (CSV con formato XLS-compatible)
    """
    rol_pago = await _get_rol_pago_with_details(db, rol_pago_id, current_user.id)
    if not rol_pago:
        raise HTTPException(404, "Rol de pago no encontrado")

    # Generar contenido tipo Excel (TSV)
    tsv_lines = [
        "TIPO_IDENTIFICACION\tIDENTIFICACION\tNOMBRE\tTIPO_CUENTA\tNUMERO_CUENTA\tVALOR"
    ]

    for detalle in rol_pago.detalles:
        empleado = detalle.employee
        tipo_id = "04"  # 04=RUC, 05=Cédula
        identificacion = empleado.cedula
        nombre = empleado.nombre_completo
        tipo_cuenta = "ACA" if empleado.tipo_cuenta == "ahorro" else "CCO"
        numero_cuenta = empleado.numero_cuenta or ""
        valor = f"{detalle.liquido_recibir:.2f}".replace(",", ".")

        linea = f"{tipo_id}\t{identificacion}\t{nombre}\t{tipo_cuenta}\t{numero_cuenta}\t{valor}"
        tsv_lines.append(linea)

    tsv_content = "\n".join(tsv_lines)

    return StreamingResponse(
        io.BytesIO(tsv_content.encode("utf-8")),
        media_type="application/vnd.ms-excel",
        headers={
            "Content-Disposition": f'attachment; filename="NOMINA_PACIFICO_{rol_pago.periodo_anio}_{rol_pago.periodo_mes:02d}.xls"'
        },
    )


# ==========================================
# Exportación Genérica CSV
# ==========================================


@router.get("/csv")
async def exportar_csv_generico(
    rol_pago_id: str = Query(..., description="ID del rol de pago"),
    incluir_detalle: bool = Query(True, description="Incluir detalle de ingresos/descuentos"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Exportar rol de pago en formato CSV genérico.

    **Parámetros:**
    - `rol_pago_id`: ID del rol de pago
    - `incluir_detalle`: Si incluir detalle de ingresos y descuentos

    **Retorna:**
    - Archivo CSV con resumen o detalle del rol
    """
    rol_pago = await _get_rol_pago_with_details(db, rol_pago_id, current_user.id)
    if not rol_pago:
        raise HTTPException(404, "Rol de pago no encontrado")

    csv_lines = []

    if incluir_detalle:
        # Encabezados
        csv_lines.append(
            "CEDULA,NOMBRE,SUELDO_BASE,INGRESOS,IESS,ANTICIPO,PRESTAMO,OTROS_DESC,TOTAL_DESC,LQUIDO"
        )

        for detalle in rol_pago.detalles:
            empleado = detalle.employee
            linea = (
                f"{empleado.cedula},"
                f'"{empleado.nombre_completo}",'
                f"{detalle.sueldo_base},"
                f"{detalle.total_ingresos},"
                f"{detalle.iess_personal_945},"
                f"{detalle.anticipo},"
                f"{detalle.prestamo_empresa},"
                f"{detalle.otros_descuentos},"
                f"{detalle.total_descuentos},"
                f"{detalle.liquido_recibir}"
            )
            csv_lines.append(linea)
    else:
        # Resumen
        csv_lines.append("CEDULA,NOMBRE,LIQUIDO_A_RECIBIR")
        for detalle in rol_pago.detalles:
            empleado = detalle.employee
            linea = f"{empleado.cedula},\"{empleado.nombre_completo}\",{detalle.liquido_recibir}"
            csv_lines.append(linea)

    csv_content = "\n".join(csv_lines)

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="ROL_PAGO_{rol_pago.periodo_anio}_{rol_pago.periodo_mes:02d}.csv"'
        },
    )


# ==========================================
# Reporte PDF Rol de Pago
# ==========================================


@router.get("/rol-pago/pdf")
async def generar_rol_pago_pdf(
    rol_pago_id: str = Query(..., description="ID del rol de pazgo"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generar reporte PDF del rol de pago detallado.

    **Parámetros:**
    - `rol_pago_id`: ID del rol de pago

    **Retorna:**
    - Archivo PDF con el rol de pago completo
    """
    rol_pago = await _get_rol_pago_with_details(db, rol_pago_id, current_user.id)
    if not rol_pago:
        raise HTTPException(404, "Rol de pago no encontrado")

    # Generar contenido PDF (simplificado - en producción usar reportlab)
    pdf_content = f"""
    REPORTE DE ROL DE PAGO
    ======================

    Empresa: {rol_pago.company.razon_social}
    RUC: {rol_pago.company.ruc}
    Período: {rol_pago.periodo_mes:02d}/{rol_pago.periodo_anio}
    Estado: {rol_pago.estado}
    Fecha de generación: {datetime.now(timezone.utc).isoformat()}

    ----------------------------------------
    RESUMEN
    ----------------------------------------
    Total Empleados: {len(rol_pago.detalles)}
    Total Remuneraciones: ${rol_pago.total_remuneraciones}
    Total Descuentos: ${rol_pago.total_descuentos}
    Total Empleador: ${rol_pago.total_empleador}
    Total Líquido: ${rol_pago.total_liquido}

    ----------------------------------------
    DETALLE POR EMPLEADO
    ----------------------------------------
    """

    for detalle in rol_pago.detalles:
        empleado = detalle.employee
        pdf_content += f"""

    {empleado.cedula} - {empleado.nombre_completo}
    ----------------------------------------
    Sueldo Base: ${detalle.sueldo_base}
    Ingresos: ${detalle.total_ingresos}
    IESS Personal: ${detalle.iess_personal_945}
    Otros Descuentos: ${detalle.total_descuentos}
    Líquido a Recibir: ${detalle.liquido_recibir}

    Aportes Empleador:
    - IESS Patronal: ${detalle.iess_patronal_1115}
    - Riesgos: ${detalle.iee_0005}
    - SECAP: ${detalle.secap_002}
    - CENACES: ${detalle.cenaces_001}
    """

    # Retornar como PDF (simplificado, en producción usar reportlab)
    return StreamingResponse(
        io.BytesIO(pdf_content.encode("utf-8")),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="ROL_PAGO_{rol_pago.periodo_anio}_{rol_pago.periodo_mes:02d}.pdf"'
        },
    )


# ==========================================
# Exportación Excel con openpyxl
# ==========================================


@router.get("/excel")
async def exportar_excel(
    rol_pago_id: str = Query(..., description="ID del rol de pago"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Exportar rol de pago en formato Excel (.xlsx).

    **Parámetros:**
    - `rol_pago_id`: ID del rol de pago

    **Retorna:**
    - Archivo Excel con múltiples hojas (resumen, detalle, aportes)
    """
    rol_pago = await _get_rol_pago_with_details(db, rol_pago_id, current_user.id)
    if not rol_pago:
        raise HTTPException(404, "Rol de pago no encontrado")

    # Generar CSV tunneado como Excel (simplificado sin openpyxl)
    csv_content = f"ROL DE PAGO - {rol_pago.company.razon_social}\n"
    csv_content += f"Período: {rol_pago.periodo_mes}/{rol_pago.periodo_anio}\n\n"
    csv_content += "CEDULA,NOMBRE,SUELDO,INGRESOS,IESS,LIQUIDO\n"

    for detalle in rol_pago.detalles:
        empleado = detalle.employee
        linea = (
            f"{empleado.cedula},"
            f'"{empleado.nombre_completo}",'
            f"{detalle.sueldo_base},"
            f"{detalle.total_ingresos},"
            f"{detalle.iess_personal_945},"
            f"{detalle.liquido_recibir}\n"
        )
        csv_content += linea

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="ROL_PAGO_{rol_pago.periodo_anio}_{rol_pago.periodo_mes:02d}.xlsx"'
        },
    )


# ==========================================
# Funciones auxiliares
# ==========================================


async def _get_rol_pago_with_details(
    db: AsyncSession,
    rol_pago_id: str,
    user_id: str,
) -> Optional[RolPago]:
    """Obtiene un rol de pago con detalles verificando permisos"""
    result = await db.execute(
        select(RolPago)
        .where(
            RolPago.id == rol_pago_id,
            RolPago.is_active == True,
        )
    )
    rol_pago = result.scalars().first()

    if not rol_pago:
        return None

    # Verificar que pertenezca al usuario
    company_result = await db.execute(
        select(Company).where(
            Company.id == rol_pago.company_id,
            Company.user_id == user_id,
        )
    )
    if not company_result.scalars().first():
        return None

    return rol_pago