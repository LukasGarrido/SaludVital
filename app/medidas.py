"""
Funciones de cálculo de medidas y formateo para el dashboard de SaludVital.
"""
from __future__ import annotations
import pandas as pd

def format_clp(value: float | int) -> str:
    if pd.isna(value):
        return "—"
    try:
        val_int = int(round(value))
        # Formato con punto de miles: $1.671.000
        formatted = f"{val_int:,}".replace(",", ".")
        return f"${formatted}"
    except Exception:
        return "—"

def format_pct(value: float) -> str:
    if pd.isna(value):
        return "—"
    try:
        return f"{value * 100:.1f} %".replace(".", ",")
    except Exception:
        return "—"

def format_num(value: int | float) -> str:
    if pd.isna(value):
        return "—"
    try:
        val_int = int(round(value))
        return f"{val_int:,}".replace(",", ".")
    except Exception:
        return "—"

def calcular_medidas(df_reservas: pd.DataFrame, df_detalle: pd.DataFrame) -> dict:
    """
    Calcula todas las medidas especificadas sobre los hechos filtrados.
    """
    total_reservas = len(df_reservas)
    
    # Conteo por EstadoReserva
    estados = df_reservas["EstadoReserva"].value_counts().to_dict() if "EstadoReserva" in df_reservas.columns else {}
    atendidas = estados.get("Atendida", 0)
    no_asistio = estados.get("No asistió", 0)
    canceladas = estados.get("Cancelada", 0)
    pendientes = estados.get("Pendiente", 0)
    
    resueltas = atendidas + no_asistio + canceladas
    
    # Atenciones Realizadas (AtencionID distintos y no vacíos en HechoReservas)
    if "AtencionID" in df_reservas.columns and total_reservas > 0:
        valid_atenciones = df_reservas["AtencionID"].dropna()
        valid_atenciones = valid_atenciones[valid_atenciones != ""]
        atenciones_realizadas = valid_atenciones.nunique()
    else:
        atenciones_realizadas = 0
        
    # Tasas
    tasa_atencion = atendidas / resueltas if resueltas > 0 else float('nan')
    den_inasistencia = atendidas + no_asistio
    tasa_inasistencia = no_asistio / den_inasistencia if den_inasistencia > 0 else float('nan')
    tasa_cancelacion = canceladas / resueltas if resueltas > 0 else float('nan')
    
    # Pacientes Distintos en HechoReservas
    pacientes_distintos = df_reservas["PacienteID"].nunique() if "PacienteID" in df_reservas.columns and len(df_reservas) > 0 else 0
    
    # Ingresos (suma de Importe en HechoDetalle)
    ingresos = df_detalle["Importe"].sum() if "Importe" in df_detalle.columns and len(df_detalle) > 0 else 0.0
    
    # Atenciones distintas en HechoDetalle para ingreso promedio
    if "AtencionID" in df_detalle.columns and len(df_detalle) > 0:
        det_atenciones = df_detalle["AtencionID"].dropna()
        det_atenciones = det_atenciones[det_atenciones != ""]
        distinct_det_atenciones = det_atenciones.nunique()
    else:
        distinct_det_atenciones = 0
        
    ingreso_promedio = ingresos / distinct_det_atenciones if distinct_det_atenciones > 0 else float('nan')
    
    # Prestaciones Realizadas (suma de Cantidad en HechoDetalle)
    prestaciones_realizadas = df_detalle["Cantidad"].sum() if "Cantidad" in df_detalle.columns and len(df_detalle) > 0 else 0
    
    return {
        "TotalReservas": total_reservas,
        "Atendidas": atendidas,
        "NoAsistio": no_asistio,
        "Canceladas": canceladas,
        "Pendientes": pendientes,
        "Resueltas": resueltas,
        "AtencionesRealizadas": atenciones_realizadas,
        "TasaAtencion": tasa_atencion,
        "TasaInasistencia": tasa_inasistencia,
        "TasaCancelacion": tasa_cancelacion,
        "PacientesDistintos": pacientes_distintos,
        "Ingresos": ingresos,
        "IngresoPromedio": ingreso_promedio,
        "PrestacionesRealizadas": prestaciones_realizadas,
    }

def ejecutar_pruebas_aceptacion(df_reservas: pd.DataFrame, df_detalle: pd.DataFrame) -> list[dict]:
    """
    Ejecuta las pruebas de aceptación sobre los datos sin filtros.
    """
    m = calcular_medidas(df_reservas, df_detalle)
    
    # Ingresos por mes (enero, febrero)
    df_detalle_temp = df_detalle.copy()
    if "FechaAtencion" in df_detalle_temp.columns:
        df_detalle_temp["FechaAtencion"] = pd.to_datetime(df_detalle_temp["FechaAtencion"])
        ingresos_enero = df_detalle_temp[df_detalle_temp["FechaAtencion"].dt.month == 1]["Importe"].sum()
        ingresos_febrero = df_detalle_temp[df_detalle_temp["FechaAtencion"].dt.month == 2]["Importe"].sum()
    else:
        ingresos_enero = 0
        ingresos_febrero = 0

    # Reservas por mes (enero, febrero)
    df_reservas_temp = df_reservas.copy()
    if "FechaReserva" in df_reservas_temp.columns:
        df_reservas_temp["FechaReserva"] = pd.to_datetime(df_reservas_temp["FechaReserva"])
        res_enero = len(df_reservas_temp[df_reservas_temp["FechaReserva"].dt.month == 1])
        res_febrero = len(df_reservas_temp[df_reservas_temp["FechaReserva"].dt.month == 2])
    else:
        res_enero = 0
        res_febrero = 0

    pruebas = [
        {
            "indicador": "Total Reservas",
            "esperado": 75,
            "obtenido": m["TotalReservas"],
            "ok": m["TotalReservas"] == 75
        },
        {
            "indicador": "Reservas Atendidas",
            "esperado": 48,
            "obtenido": m["Atendidas"],
            "ok": m["Atendidas"] == 48
        },
        {
            "indicador": "Reservas No Asistió",
            "esperado": 12,
            "obtenido": m["NoAsistio"],
            "ok": m["NoAsistio"] == 12
        },
        {
            "indicador": "Reservas Canceladas",
            "esperado": 10,
            "obtenido": m["Canceladas"],
            "ok": m["Canceladas"] == 10
        },
        {
            "indicador": "Reservas Pendientes",
            "esperado": 5,
            "obtenido": m["Pendientes"],
            "ok": m["Pendientes"] == 5
        },
        {
            "indicador": "Tasa de Atención",
            "esperado": "68,6 %",
            "obtenido": format_pct(m["TasaAtencion"]),
            "ok": abs(m["TasaAtencion"] - 0.6857) < 0.002 or format_pct(m["TasaAtencion"]) == "68,6 %"
        },
        {
            "indicador": "Tasa de Inasistencia",
            "esperado": "20,0 %",
            "obtenido": format_pct(m["TasaInasistencia"]),
            "ok": abs(m["TasaInasistencia"] - 0.20) < 0.002
        },
        {
            "indicador": "Tasa de Cancelación",
            "esperado": "14,3 %",
            "obtenido": format_pct(m["TasaCancelacion"]),
            "ok": abs(m["TasaCancelacion"] - 0.1428) < 0.002 or format_pct(m["TasaCancelacion"]) == "14,3 %"
        },
        {
            "indicador": "Atenciones Realizadas",
            "esperado": 46,
            "obtenido": m["AtencionesRealizadas"],
            "ok": m["AtencionesRealizadas"] == 46
        },
        {
            "indicador": "Pacientes Distintos",
            "esperado": 44,
            "obtenido": m["PacientesDistintos"],
            "ok": m["PacientesDistintos"] == 44
        },
        {
            "indicador": "Ingresos Totales",
            "esperado": "$1.671.000",
            "obtenido": format_clp(m["Ingresos"]),
            "ok": m["Ingresos"] == 1671000
        },
        {
            "indicador": "Ingresos Enero",
            "esperado": "$745.000",
            "obtenido": format_clp(ingresos_enero),
            "ok": ingresos_enero == 745000
        },
        {
            "indicador": "Ingresos Febrero",
            "esperado": "$926.000",
            "obtenido": format_clp(ingresos_febrero),
            "ok": ingresos_febrero == 926000
        },
        {
            "indicador": "Ingreso Promedio por Atención",
            "esperado": "$40.756",
            "obtenido": format_clp(m["IngresoPromedio"]),
            "ok": round(m["IngresoPromedio"]) == 40756
        },
        {
            "indicador": "Reservas Enero",
            "esperado": 28,
            "obtenido": res_enero,
            "ok": res_enero == 28
        },
        {
            "indicador": "Reservas Febrero",
            "esperado": 47,
            "obtenido": res_febrero,
            "ok": res_febrero == 47
        }
    ]
    return pruebas
