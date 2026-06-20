"""
ContaEC - Cálculo de Impuesto a la Renta para Empleados
IR: Cálculo progresivo conforme a tablas SRI vigentes 2024-2026
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


@dataclass
class TablaIR:
    """Estructura de tramo de tabla de Impuesto a la Renta"""
    limite_inferior: Decimal
    limite_superior: Optional[Decimal]
    porcentaje: Decimal
    fraccion_fija: Decimal


# Tabla progresiva de Impuesto a la Renta 2024-2026 (Ecuador)
# Actualizada conforme Resolución NAC-DGERCGC24-00000XXX del SRI
TABLA_IR_2024 = [
    TablaIR(
        limite_inferior=Decimal("0.00"),
        limite_superior=Decimal("12870.00"),
        porcentaje=Decimal("0.00"),
        fraccion_fija=Decimal("0.00"),
    ),
    TablaIR(
        limite_inferior=Decimal("12870.01"),
        limite_superior=Decimal("16520.00"),
        porcentaje=Decimal("5.00"),
        fraccion_fija=Decimal("0.00"),
    ),
    TablaIR(
        limite_inferior=Decimal("16520.01"),
        limite_superior=Decimal("20180.00"),
        porcentaje=Decimal("10.00"),
        fraccion_fija=Decimal("182.50"),
    ),
    TablaIR(
        limite_inferior=Decimal("20180.01"),
        limite_superior=Decimal("23830.00"),
        porcentaje=Decimal("12.00"),
        fraccion_fija=Decimal("548.50"),
    ),
    TablaIR(
        limite_inferior=Decimal("23830.01"),
        limite_superior=Decimal("47650.00"),
        porcentaje=Decimal("15.00"),
        fraccion_fija=Decimal("986.50"),
    ),
    TablaIR(
        limite_inferior=Decimal("47650.01"),
        limite_superior=Decimal("69660.00"),
        porcentaje=Decimal("20.00"),
        fraccion_fija=Decimal("4559.50"),
    ),
    TablaIR(
        limite_inferior=Decimal("69660.01"),
        limite_superior=Decimal("88330.00"),
        porcentaje=Decimal("25.00"),
        fraccion_fija=Decimal("8961.50"),
    ),
    TablaIR(
        limite_inferior=Decimal("88330.01"),
        limite_superior=Decimal("115440.00"),
        porcentaje=Decimal("30.00"),
        fraccion_fija=Decimal("13629.00"),
    ),
    TablaIR(
        limite_inferior=Decimal("115440.01"),
        limite_superior=None,  # Sin límite superior
        porcentaje=Decimal("35.00"),
        fraccion_fija=Decimal("21762.00"),
    ),
]

# Fracción básica adicional por carga familiar (2024)
FRACCION_BASICA_CARGA_FAMILIAR = Decimal("794.00")  # USD mensuales
DEDUCCION_ANUAL_CARGA_FAMILIAR = Decimal("9528.00")  # USD anuales (794 * 12)

# Límite de deducciones personales (seguro médico, educación, etc.)
LIMITE_DEDUCCIONES_PERSONALES = Decimal("17076.00")  # 20% de la base imponible máxima


def calcular_base_imponible(
    ingresos_anuales: Decimal,
    deducciones: Optional[Decimal] = None,
    cargas_familiares: int = 0,
) -> Decimal:
    """
    Calcula la base imponible para Impuesto a la Renta.

    Args:
        ingresos_anuales: Total de ingresos gravados anuales
        deducciones: Deducciones personales (seguro médico, educación, etc.)
        cargas_familiares: Número de cargas familiares (hijos, cónyuge)

    Returns:
        Base imponible después de deducciones
    """
    # Deducción por cargas familiares
    deduccion_cargas = Decimal("0.00")
    if cargas_familiares > 0:
        deduccion_cargas = DEDUCCION_ANUAL_CARGA_FAMILIAR * Decimal(str(cargas_familiares))
        # Límite: máximo 10% de los ingresos
        deduccion_cargas = min(deduccion_cargas, ingresos_anuales * Decimal("0.10"))

    # Deducciones personales (con límite)
    deducciones_personales = deducciones or Decimal("0.00")
    deducciones_personales = min(deducciones_personales, LIMITE_DEDUCCIONES_PERSONALES)

    # Base imponible
    total_deducciones = deduccion_cargas + deducciones_personales
    base_imponible = ingresos_anuales - total_deducciones

    # La base no puede ser negativa
    return max(base_imponible, Decimal("0.00"))


def calcular_impuesto_renta_anual(
    base_imponible: Decimal,
    tabla_ir: Optional[list] = None,
) -> Decimal:
    """
    Calcula el Impuesto a la Renta anual progresivo.

    Aplica la tabla progresiva según el tramo que corresponda:
    IR = (Base Imponible - Límite Inferior) * Porcentaje + Fracción Fija

    Args:
        base_imponible: Base imponible anual después de deducciones
        tabla_ir: Tabla de IR a usar (default: TABLA_IR_2024)

    Returns:
        Impuesto a la Renta anual a pagar
    """
    tabla = tabla_ir or TABLA_IR_2024

    # Encontrar el tramo correspondiente
    tramo_seleccionado = None
    for tramo in tabla:
        if tramo.limite_superior is None:
            # Último tramo (sin límite superior)
            if base_imponible >= tramo.limite_inferior:
                tramo_seleccionado = tramo
                break
        elif tramo.limite_inferior <= base_imponible <= tramo.limite_superior:
            tramo_seleccionado = tramo
            break

    if tramo_seleccionado is None:
        # Base imponible muy baja, no paga impuesto
        return Decimal("0.00")

    # Calcular impuesto
    excedente = base_imponible - tramo_seleccionado.limite_inferior
    impuesto = (
        excedente * (tramo_seleccionado.porcentaje / Decimal("100"))
        + tramo_seleccionado.fraccion_fija
    ).quantize(Decimal("0.01"))

    return impuesto


def calcular_retencion_mensual(
    sueldo_mensual: Decimal,
    meses_proyeccion: int = 12,
    deducciones_anuales: Optional[Decimal] = None,
    cargas_familiares: int = 0,
    tabla_ir: Optional[list] = None,
) -> Decimal:
    """
    Calcula la retención mensual de Impuesto a la Renta.

    Proyecta ingresos anuales, calcula el impuesto anual y
    divide para 12 para obtener la retención mensual.

    Args:
        sueldo_mensual: Sueldo mensual del empleado
        meses_proyeccion: Meses a proyectar (default 12)
        deducciones_anuales: Deducciones personales anuales estimadas
        cargas_familiares: Número de cargas familiares
        tabla_ir: Tabla de IR a usar

    Returns:
        Retención mensual de Impuesto a la Renta
    """
    # Proyectar ingresos anuales
    ingresos_anuales = sueldo_mensual * Decimal(str(meses_proyeccion))

    # Calcular base imponible
    base_imponible = calcular_base_imponible(
        ingresos_anuales=ingresos_anuales,
        deducciones=deducciones_anuales,
        cargas_familiares=cargas_familiares,
    )

    # Calcular impuesto anual
    impuesto_anual = calcular_impuesto_renta_anual(base_imponible, tabla_ir)

    # Retención mensual (dividir para 12)
    retencion_mensual = (impuesto_anual / Decimal("12")).quantize(Decimal("0.01"))

    return retencion_mensual


def calcular_impuesto_decimo_tercero(
    decimo_tercero: Decimal,
    sueldo_mensual: Decimal,
    tasa_promedio: Optional[Decimal] = None,
) -> Decimal:
    """
    Calcula la retención de IR sobre el décimo tercero.

    El décimo tercero se grava con la tasa promedio del año.

    Args:
        decimo_tercero: Monto del décimo tercero
        sueldo_mensual: Sueldo mensual para calcular tasa promedio
        tasa_promedio: Tasa promedio calculada (si ya existe)

    Returns:
        Retención de IR sobre el décimo tercero
    """
    if tasa_promedio is None:
        # Calcular tasa promedio basada en sueldo mensual
        impuesto_anual = calcular_retencion_mensual(sueldo_mensual) * 12
        ingresos_anuales = sueldo_mensual * 12

        if ingresos_anuales > 0:
            tasa_promedio = (impuesto_anual / ingresos_anuales) * 100
        else:
            tasa_promedio = Decimal("0.00")

    retencion = (decimo_tercero * tasa_promedio / Decimal("100")).quantize(Decimal("0.01"))
    return retencion


def calcular_impuesto_decimo_cuarto(
    decimo_cuarto: Decimal,
) -> Decimal:
    """
    Calcula la retención de IR sobre el décimo cuarto.

    El décimo cuarto NO está sujeto a retención de IR por ser
    una bonificación básica no gravada.

    Returns:
        Decimal("0.00") - no tiene retención
    """
    return Decimal("0.00")


def calcular_impuesto_vacaciones(
    vacaciones_monto: Decimal,
    tasa_promedio: Decimal,
) -> Decimal:
    """
    Calcula la retención de IR sobre vacaciones.

    Args:
        vacaciones_monto: Monto de vacaciones a pagar
        tasa_promedio: Tasa promedio del empleado

    Returns:
        Retención de IR sobre vacaciones
    """
    retencion = (vacaciones_monto * tasa_promedio / Decimal("100")).quantize(Decimal("0.01"))
    return retencion


def calcular_impuesto_liquidacion(
    base_imponible_liquidacion: Decimal,
    anios_servicio: int,
) -> Decimal:
    """
    Calcula el Impuesto a la Renta en liquidación laboral.

    En la liquidación, los ingresos se consideran "ingresos extraordinarios"
    y se gravan de manera proporcional al tiempo trabajado.

    Args:
        base_imponible_liquidacion: Base imponible de la liquidación
        anios_servicio: Años de servicio del empleado

    Returns:
        Impuesto a la Renta sobre liquidación
    """
    if base_imponible_liquidacion <= 0:
        return Decimal("0.00")

    # Calcular impuesto como ingreso anual proporcional
    # (simplificación: aplicar tabla directamente)
    impuesto = calcular_impuesto_renta_anual(base_imponible_liquidacion)

    # Ajustar proporcionalmente por años de servicio
    # (los primeros $12,870 anuales no se gravan)
    if anios_servicio < 1:
        # Proporcional para menos de un año
        proporcion = Decimal(str(anios_servicio)) if anios_servicio > 0 else Decimal("0.5")
        impuesto = (impuesto * proporcion).quantize(Decimal("0.01"))

    return impuesto


def obtener_tramo_ir(base_imponible: Decimal, tabla_ir: Optional[list] = None) -> dict:
    """
    Obtiene información del tramo de IR correspondiente.

    Args:
        base_imponible: Base imponible anual
        tabla_ir: Tabla de IR a usar

    Returns:
        Diccionario con información del tramo
    """
    tabla = tabla_ir or TABLA_IR_2024

    for i, tramo in enumerate(tabla):
        if tramo.limite_superior is None:
            if base_imponible >= tramo.limite_inferior:
                return {
                    "tramo": i + 1,
                    "limite_inferior": tramo.limite_inferior,
                    "limite_superior": "Sin límite",
                    "porcentaje": tramo.porcentaje,
                    "fraccion_fija": tramo.fraccion_fija,
                }
        elif tramo.limite_inferior <= base_imponible <= tramo.limite_superior:
            return {
                "tramo": i + 1,
                "limite_inferior": tramo.limite_inferior,
                "limite_superior": tramo.limite_superior,
                "porcentaje": tramo.porcentaje,
                "fraccion_fija": tramo.fraccion_fija,
            }

    return {
        "tramo": 1,
        "limite_inferior": Decimal("0.00"),
        "limite_superior": tabla[0].limite_superior,
        "porcentaje": Decimal("0.00"),
        "fraccion_fija": Decimal("0.00"),
    }


def generar_reporte_ir_empleado(
    empleado_nombre: str,
    sueldo_mensual: Decimal,
    ingresos_anuales: Decimal,
    deducciones: Decimal,
    cargas_familiares: int,
) -> dict:
    """
    Genera reporte completo de Impuesto a la Renta para un empleado.

    Args:
        empleado_nombre: Nombre del empleado
        sueldo_mensual: Sueldo mensual
        ingresos_anuales: Ingresos anuales proyectados
        deducciones: Deducciones personales anuales
        cargas_familiares: Número de cargas familiares

    Returns:
        Diccionario con reporte completo de IR
    """
    # Calcular base imponible
    base_imponible = calcular_base_imponible(ingresos_anuales, deducciones, cargas_familiares)

    # Calcular impuesto anual
    impuesto_anual = calcular_impuesto_renta_anual(base_imponible)

    # Calcular retención mensual
    retencion_mensual = (impuesto_anual / Decimal("12")).quantize(Decimal("0.01"))

    # Obtener tramo
    tramo = obtener_tramo_ir(base_imponible)

    # Calcular tasa efectiva
    tasa_efectiva = (
        (impuesto_anual / ingresos_anuales) * 100 if ingresos_anuales > 0 else Decimal("0.00")
    )

    return {
        "empleado": empleado_nombre,
        "sueldo_mensual": sueldo_mensual,
        "ingresos_anuales": ingresos_anuales,
        "deducciones_totales": deducciones,
        "cargas_familiares": cargas_familiares,
        "base_imponible": base_imponible,
        "tramo_ir": tramo["tramo"],
        "porcentaje_marginal": tramo["porcentaje"],
        "impuesto_anual": impuesto_anual,
        "retencion_mensual": retencion_mensual,
        "tasa_efectiva": tasa_efectiva.quantize(Decimal("0.01")),
        "ingreso_neto_anual": (ingresos_anuales - impuesto_anual).quantize(Decimal("0.01")),
    }