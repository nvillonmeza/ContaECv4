"""
ContaEC - Cálculos Automáticos de Nómina
Cálculos automáticamente: Décimo Tercero, Décimo Cuarto, Fondo Reserva,
Vacaciones, Horas Extras, Utilidades conforme a legislación ecuatoriana
"""
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from app.core.hr_constants import (
    CENACES_RATE,
    DECIMO_CUARTO_SALARIO_BASICO,
    DECIMO_TERCERO_MONTHS,
    FONDO_RESERVA_ANIOS_MIN,
    FONDO_RESERVA_RATE,
    HORA_EXTRA_DIURNA_MULT,
    HORA_EXTRA_DOMINICAL_MULT,
    HORA_EXTRA_NOCTURNA_MULT,
    HORAS_MENSUAL_DEFAULT,
    IESS_PERSONAL_RATE,
    IESS_PATRONAL_RATE,
    IESS_RIESGOS_RATE,
    SALARIO_BASICO_UNIFICADO_2024,
    SECAP_RATE,
    VACACIONES_DIAS_ANIO,
    VACACIONES_PROVISION_RATE,
)


@dataclass
class ResultadoCalculo:
    """Resultado de cálculos de nómina"""
    valor: Decimal
    descripcion: str
    base_calculo: Optional[Decimal] = None
    porcentaje: Optional[Decimal] = None
    dias_aplicados: Optional[int] = None


# ==========================================
# Décimo Tercero (Art. 95 Código del Trabajo)
# ==========================================

def calcular_decimo_tercero(
    sueldo_mensual: Decimal,
    meses_trabajados: int,
    ingresos_adicionales: Optional[Decimal] = None,
) -> ResultadoCalculo:
    """
    Calcula el décimo tercero (bono navideño).

    Conforme al Art. 95 del Código del Trabajo:
    - Equivale a 1/12 de la remuneración mensual por cada mes completo
    - Pago máximo el 24 de diciembre
    - Incluye sueldo base + ingresos adicionales (horas extras, bonos, etc.)

    Args:
        sueldo_mensual: Sueldo base mensual del empleado
        meses_trabajados: Meses completos trabajados en el año (1-12)
        ingresos_adicionales: Ingresos adicionales gravados (opcional)

    Returns:
        ResultadoCalculo con el valor del décimo tercero
    """
    base_gravada = sueldo_mensual + (ingresos_adicionales or Decimal("0.00"))
    valor_mensual = base_gravada / Decimal(str(DECIMO_TERCERO_MONTHS))
    valor_total = (valor_mensual * Decimal(str(meses_trabajados))).quantize(Decimal("0.01"))

    return ResultadoCalculo(
        valor=valor_total,
        descripcion="Décimo Tercero (Bonificación Navideña)",
        base_calculo=base_gravada,
        porcentaje=Decimal("8.33"),  # 1/12 ≈ 8.33%
        dias_aplicados=meses_trabajados,
    )


def calcular_decimo_tercero_mensualizado(
    sueldo_mensual: Decimal,
) -> Decimal:
    """
    Calcula la provisión mensual del décimo tercero.

    Se usa para calcular el valor que se provisiona cada mes
    en el rol de pago (1/12 del sueldo).

    Returns:
        Provisión mensual del décimo tercero
    """
    return (sueldo_mensual / Decimal(str(DECIMO_TERCERO_MONTHS))).quantize(Decimal("0.01"))


# ==========================================
# Décimo Cuarto (Art. 97 Código del Trabajo)
# ==========================================

def calcular_decimo_cuarto(
    meses_trabajados: int,
    anio: Optional[int] = None,
    salario_basico: Optional[Decimal] = None,
) -> ResultadoCalculo:
    """
    Calcula el décimo cuarto (bono escolar).

    Conforme al Art. 97 del Código del Trabajo:
    - Equivale a 1/12 del salario básico unificado vigente
    - Pago: agosto (Sierra/Amazonía) o marzo (Costa/Galápagos)
    - Proporcional a meses completos trabajados

    Args:
        meses_trabajados: Meses completos trabajados (1-12)
        anio: Año de cálculo (para usar SBU vigente)
        salario_basico: Salario básico unificado (usa 2024 por defecto)

    Returns:
        ResultadoCalculo con el valor del décimo cuarto
    """
    sbu = salario_basico or DECIMO_CUARTO_SALARIO_BASICO
    valor_mensual = sbu / Decimal(str(DECIMO_TERCERO_MONTHS))
    valor_total = (valor_mensual * Decimal(str(meses_trabajados))).quantize(Decimal("0.01"))

    return ResultadoCalculo(
        valor=valor_total,
        descripcion="Décimo Cuarto (Bonificación Escolar)",
        base_calculo=sbu,
        porcentaje=Decimal("8.33"),
        dias_aplicados=meses_trabajados,
    )


def calcular_decimo_cuarto_mensualizado(
    salario_basico: Optional[Decimal] = None,
) -> Decimal:
    """
    Calcula la provisión mensual del décimo cuarto.

    Returns:
        Provisión mensual del décimo cuarto
    """
    sbu = salario_basico or DECIMO_CUARTO_SALARIO_BASICO
    return (sbu / Decimal(str(DECIMO_TERCERO_MONTHS))).quantize(Decimal("0.01"))


# ==========================================
# Fondo de Reserva (Art. 188 Ley de Seguridad Social)
# ==========================================

def calcular_fondo_reserva(
    sueldo_mensual: Decimal,
    anios_servicio: int,
    meses_aplicacion: int = 12,
    tiene_derecho: Optional[bool] = None,
) -> ResultadoCalculo:
    """
    Calcula el fondo de reserva.

    Conforme al Art. 188 de la Ley de Seguridad Social:
    - 8.33% de la remuneración mensual (1/12 del sueldo)
    - Requiere más de 1 año de trabajo
    - Se paga proporcionalmente al año siguiente (agosto/marzo)

    Args:
        sueldo_mensual: Sueldo mensual del empleado
        anios_servicio: Años completos de servicio
        meses_aplicacion: Meses de aplicación en el período
        tiene_derecho: Override manual del derecho (default: anios >= 1)

    Returns:
        ResultadoCalculo con el valor del fondo de reserva
    """
    if tiene_derecho is None:
        tiene_derecho = anios_servicio >= FONDO_RESERVA_ANIOS_MIN

    if not tiene_derecho:
        return ResultadoCalculo(
            valor=Decimal("0.00"),
            descripcion="Fondo de Reserva (no cumple 1 año)",
            base_calculo=sueldo_mensual,
            porcentaje=FONDO_RESERVA_RATE,
        )

    valor_mensual = (sueldo_mensual * FONDO_RESERVA_RATE / Decimal("100")).quantize(Decimal("0.01"))
    valor_proporcional = (valor_mensual * Decimal(str(meses_aplicacion)) / Decimal("12")).quantize(
        Decimal("0.01")
    )

    return ResultadoCalculo(
        valor=valor_proporcional,
        descripcion="Fondo de Reserva (8.33%)",
        base_calculo=sueldo_mensual,
        porcentaje=FONDO_RESERVA_RATE,
        dias_aplicados=meses_aplicacion,
    )


def calcular_fondo_reserva_mensual(
    sueldo_mensual: Decimal,
    tiene_derecho: bool = True,
) -> Decimal:
    """
    Calcula la provisión mensual del fondo de reserva.

    Returns:
        Provisión mensual del fondo de reserva
    """
    if not tiene_derecho:
        return Decimal("0.00")
    return (sueldo_mensual * FONDO_RESERVA_RATE / Decimal("100")).quantize(Decimal("0.01"))


# ==========================================
# Vacaciones (Art. 109-113 Código del Trabajo)
# ==========================================

def calcular_vacaciones_dias(
    anios_servicio: int,
    dias_pendientes_periodo: Decimal = Decimal("0.00"),
) -> int:
    """
    Calcula días de vacaciones por año de servicio.

    Conforme al Art. 109 del Código del Trabajo:
    - 15 días por cada año completo de trabajo
    - 1 día adicional por cada año adicional (a partir del 2do año)
    - Máximo acumulable sin tomar: 30 días (Art. 110)

    Args:
        anios_servicio: Años completos de servicio
        dias_pendientes_periodo: Días pendientes del período actual

    Returns:
        Total de días de vacaciones disponibles
    """
    if anios_servicio == 0:
        return 0

    # Año base: 15 días
    dias_base = VACACIONES_DIAS_ANIO

    # Días adicionales: +1 por cada año adicional (año 2+, máximo 15 adicionales = 30 total)
    dias_adicionales = max(0, anios_servicio - 1)
    dias_totales = min(dias_base + dias_adicionales, 30)

    return dias_totales + int(dias_pendientes_periodo)


def calcular_vacaciones_valor(
    sueldo_mensual: Decimal,
    dias_vacaciones: int,
    dias_trabajados_periodo: Optional[int] = None,
) -> ResultadoCalculo:
    """
    Calcula el valor monetario de las vacaciones.

    Se calcula sobre la base del sueldo mensual proporcional
    a los días de vacaciones tomados.

    Args:
        sueldo_mensual: Sueldo mensual del empleado
        dias_vacaciones: Días de vacaciones a monetizar
        dias_trabajados_periodo: Días trabajados en el período (para provisión)

    Returns:
        ResultadoCalculo con el valor de vacaciones
    """
    sueldo_diario = (sueldo_mensual / Decimal("30")).quantize(Decimal("0.01"))
    valor_vacaciones = (sueldo_diario * Decimal(str(dias_vacaciones))).quantize(Decimal("0.01"))

    return ResultadoCalculo(
        valor=valor_vacaciones,
        descripcion=f"Vacaciones ({dias_vacaciones} días)",
        base_calculo=sueldo_diario,
        dias_aplicados=dias_vacaciones,
    )


def calcular_vacaciones_provision_mensual(
    sueldo_mensual: Decimal,
) -> Decimal:
    """
    Calcula la provisión mensual de vacaciones.

    Se provisiona 15/360 (aprox 4.17%) del sueldo mensual.

    Returns:
        Provisión mensual de vacaciones
    """
    return (sueldo_mensual * VACACIONES_PROVISION_RATE / Decimal("360")).quantize(Decimal("0.01"))


# ==========================================
# Horas Extras (Art. 47, 50-53 Código del Trabajo)
# ==========================================

def calcular_valor_hora_normal(
    sueldo_mensual: Decimal,
    horas_semanal: Decimal = HORAS_MENSUAL_DEFAULT,
) -> Decimal:
    """
    Calcula el valor de la hora normal de trabajo.

    Args:
        sueldo_mensual: Sueldo mensual del empleado
        horas_semanal: Horas de trabajo semanal (default 40)

    Returns:
        Valor de la hora normal
    """
    horas_mensual = horas_semanal * Decimal("4")  # 4 semanas por mes
    return (sueldo_mensual / horas_mensual).quantize(Decimal("0.01"))


def calcular_horas_extras(
    sueldo_mensual: Decimal,
    horas_extras_diurnas: Decimal = Decimal("0.00"),
    horas_extras_nocturnas: Decimal = Decimal("0.00"),
    horas_extras_dominicales: Decimal = Decimal("0.00"),
    horas_semanal: Decimal = HORAS_MENSUAL_DEFAULT,
) -> dict:
    """
    Calcula el valor de horas extras trabajadas.

    Conforme al Código del Trabajo:
    - Horas diurnas: recargo 25% sobre hora normal
    - Horas nocturnas: recargo 50% sobre hora normal (22:00-06:00)
    - Horas dominicales/festivas: recargo 100% sobre hora normal

    Args:
        sueldo_mensual: Sueldo base mensual
        horas_extras_diurnas: Horas extras diurnas trabajadas
        horas_extras_nocturnas: Horas extras nocturnas trabajadas
        horas_extras_dominicales: Horas extras dominicales/festivas

    Returns:
        Diccionario con desglose de valores
    """
    valor_hora = calcular_valor_hora_normal(sueldo_mensual, horas_semanal)

    # Horas diurnas: 25% recargo
    valor_hora_diurna = (valor_hora * HORA_EXTRA_DIURNA_MULT).quantize(Decimal("0.01"))
    total_diurnas = (valor_hora_diurna * horas_extras_diurnas).quantize(Decimal("0.01"))

    # Horas nocturnas: 50% recargo
    valor_hora_nocturna = (valor_hora * HORA_EXTRA_NOCTURNA_MULT).quantize(Decimal("0.01"))
    total_nocturnas = (valor_hora_nocturna * horas_extras_nocturnas).quantize(Decimal("0.01"))

    # Horas dominicales: 100% recargo
    valor_hora_dominical = (valor_hora * HORA_EXTRA_DOMINICAL_MULT).quantize(Decimal("0.01"))
    total_dominicales = (valor_hora_dominical * horas_extras_dominicales).quantize(Decimal("0.01"))

    return {
        "valor_hora_normal": valor_hora,
        "valor_hora_diurna": valor_hora_diurna,
        "total_diurnas": total_diurnas,
        "horas_diurnas": horas_extras_diurnas,
        "valor_hora_nocturna": valor_hora_nocturna,
        "total_nocturnas": total_nocturnas,
        "horas_nocturnas": horas_extras_nocturnas,
        "valor_hora_dominical": valor_hora_dominical,
        "total_dominicales": total_dominicales,
        "horas_dominicales": horas_extras_dominicales,
        "total_horas_extras": (total_diurnas + total_nocturnas + total_dominicales).quantize(
            Decimal("0.01")
        ),
    }


# ==========================================
# Aportes IESS
# ==========================================

def calcular_aportes_iess(
    total_ingresos_gravados: Decimal,
    es_empleador: bool = False,
) -> dict:
    """
    Calcula aportes al IESS sobre ingresos gravados.

    Tasas vigentes:
    - Aporte personal: 9.35% (empleado)
    - Aporte patronal: 12.15% (empleador)
    - Riesgos del trabajo: 0.5% (empleador)
    - SECAP: 0.2% (empleador)
    - CENACES: 0.1% (empleador)
    Total empleador: 12.95%

    Args:
        total_ingresos_gravados: Total de ingresos sujetos a aporte
        es_empleador: Si True calcula aporte patronal, si False calcula personal

    Returns:
        Diccionario con detalles de aportes
    """
    if es_empleador:
        iess_patronal = (total_ingresos_gravados * IESS_PATRONAL_RATE / Decimal("100")).quantize(
            Decimal("0.01")
        )
        riesgos = (total_ingresos_gravados * IESS_RIESGOS_RATE / Decimal("100")).quantize(
            Decimal("0.01")
        )
        secap = (total_ingresos_gravados * SECAP_RATE / Decimal("100")).quantize(Decimal("0.01"))
        cenaces = (total_ingresos_gravados * CENACES_RATE / Decimal("100")).quantize(Decimal("0.01"))

        return {
            "iess_patronal": iess_patronal,
            "riesgos_trabajo": riesgos,
            "secap": secap,
            "cenaces": cenaces,
            "total_aportes_empleador": (iess_patronal + riesgos + secap + cenaces).quantize(
                Decimal("0.01")
            ),
        }
    else:
        iess_personal = (
            total_ingresos_gravados * IESS_PERSONAL_RATE / Decimal("100")
        ).quantize(Decimal("0.01"))

        return {
            "iess_personal": iess_personal,
            "total_aportes_empleado": iess_personal,
        }


# ==========================================
# Utilidades (Participación de Trabajadores)
# ==========================================

def calcular_utilidades_empleado(
    total_utilidades_trabajadores: Decimal,
    numero_trabajadores: int,
    dias_trabajados_empleado: int,
    sueldo_acumulado_empleado: Decimal,
    suma_dias_trabajados: int,
    suma_sueldos_acumulados: Decimal,
) -> dict:
    """
    Calcula la participación de utilidades por empleado.

    Conforme al Art. 97 de la Ley de Compañías:
    - 15% de utilidades netas para trabajadores
    - 50% se distribuye por igual (parte individual)
    - 50% se distribuye proporcional a cargas familiares (simplificado: sueldos)

    Args:
        total_utilidades_trabajadores: 15% de utilidades para distribución
        numero_trabajadores: Número total de trabajadores
        dias_trabajados_empleado: Días trabajados por el empleado
        sueldo_acumulado_empleado: Sueldo acumulado anual del empleado
        suma_dias_trabajados: Suma de días de todos los empleados
        suma_sueldos_acumulados: Suma de sueldos acumulados de todos

    Returns:
        Diccionario con participación individual y desglose
    """
    # Parte individual (50% distribuido por igual)
    parte_individual = (
        total_utilidades_trabajadores * Decimal("0.50") / Decimal(str(numero_trabajadores))
    ).quantize(Decimal("0.01"))

    # Parte proporcional (50% distribuido por sueldos/días)
    proporcion_dias = Decimal(str(dias_trabajados_empleado)) / Decimal(str(suma_dias_trabajados))
    parte_dias = (
        total_utilidades_trabajadores * Decimal("0.50") * proporcion_dias
    ).quantize(Decimal("0.01"))

    proporcion_sueldo = sueldo_acumulado_empleado / suma_sueldos_acumulados
    parte_sueldo = (
        total_utilidades_trabajadores * Decimal("0.50") * proporcion_sueldo
    ).quantize(Decimal("0.01"))

    # Total utilidades (fase simplificada: solo días)
    total_utilidades_empleado = parte_dias

    return {
        "parte_individual": parte_individual,
        "parte_dias": parte_dias,
        "parte_sueldo": parte_sueldo,
        "total_utilidades": total_utilidades_empleado,
        "porcentaje_participacion": (
            (Decimal(str(dias_trabajados_empleado)) / Decimal(str(suma_dias_trabajados))) * 100
        ).quantize(Decimal("0.01")),
    }


# ==========================================
# Liquidación Laboral
# ==========================================

def calcular_liquidacion_simple(
    sueldo_mensual: Decimal,
    anios_servicio: int,
    meses_ultimo_anio: int,
    dias_vacaciones_pendientes: int,
    tiene_fondo_reserva_pendiente: bool = True,
) -> dict:
    """
    Calcula liquidación laboral simplificada.

    Incluye:
    - Sueldo pendiente (días trabajados del mes)
    - Décimo tercero proporcional
    - Décimo cuarto proporcional
    - Vacaciones pendientes
    - Fondo de reserva pendiente (si aplica)

    Args:
        sueldo_mensual: Sueldo mensual del empleado
        anios_servicio: Años completos de servicio
        meses_ultimo_anio: Meses trabajados en el último año
        dias_vacaciones_pendientes: Días de vacaciones pendientes
        tiene_fondo_reserva_pendiente: Si tiene fondo de reserva pendiente

    Returns:
        Diccionario con detalle de liquidación
    """
    # Décimo tercero proporcional
    decimo_tercero = calcular_decimo_tercero(sueldo_mensual, meses_ultimo_anio).valor

    # Décimo cuarto proporcional
    decimo_cuarto = calcular_decimo_cuarto(meses_ultimo_anio).valor

    # Vacaciones pendientes
    vacaciones = calcular_vacaciones_valor(sueldo_mensual, dias_vacaciones_pendientes).valor

    # Fondo de reserva
    fondo_reserva = Decimal("0.00")
    if tiene_fondo_reserva_pendiente and anios_servicio >= FONDO_RESERVA_ANIOS_MIN:
        fondo_reserva = calcular_fondo_reserva(
            sueldo_mensual, anios_servicio, meses_ultimo_anio
        ).valor

    total_liquidacion = (
        decimo_tercero + decimo_cuarto + vacaciones + fondo_reserva
    ).quantize(Decimal("0.01"))

    return {
        "decimo_tercero": decimo_tercero,
        "decimo_cuarto": decimo_cuarto,
        "vacaciones": vacaciones,
        "fondo_reserva": fondo_reserva,
        "total_liquidacion": total_liquidacion,
    }