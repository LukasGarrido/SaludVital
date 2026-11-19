"""
Aplicación principal en Streamlit para el dashboard de SaludVital (Réplica Exacta Power BI).
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

try:
    from app.data import prepare_data
    from app.medidas import calcular_medidas, ejecutar_pruebas_aceptacion, format_clp, format_pct, format_num
    from app.styles import apply_theme, page_header, sidebar_brand, sidebar_section, chip_filter
except ImportError:
    from data import prepare_data
    from medidas import calcular_medidas, ejecutar_pruebas_aceptacion, format_clp, format_pct, format_num
    from styles import apply_theme, page_header, sidebar_brand, sidebar_section, chip_filter

# Configuración de la página
st.set_page_config(
    page_title="SaludVital - Centro Médico Ambulatorio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores corporativa
COLOR_ISAPRE_PRIMARY = "#E05A6D"
COLOR_FONASA = "#4FB3A8"
COLOR_BARS = "#E05A6D"
PALETTE = ["#E05A6D", "#4FB3A8", "#3B82F6", "#F59E0B", "#10B981", "#8B5CF6", "#EC4899"]

# Estilos (CSS y formato de gráficos) definidos en styles.py
apply_theme()

NOTA_VISIBLE = (
    "Datos simulados (no corresponden a la operación real de SaludVital). "
    "Cobertura: reservas del 05-01-2026 al 28-02-2026 (alrededor de 2 meses), lo que no permite evaluar estacionalidad. "
    "Los ingresos son valorizados, no cobrados. Canal y bloque horario existen solo desde el 04-02-2026 (51 % de las reservas), "
    "por lo que horas perdidas y utilización cubren ese subconjunto. Con menos de 10 reservas por canal o especialidad, "
    "las diferencias son indicativas. 34 filas fueron rechazadas por calidad de datos."
)

def main():
    data_dict = prepare_data()
    if data_dict is None:
        st.stop()
        
    dim_fecha = data_dict["DimFecha"]
    dim_paciente = data_dict["DimPaciente"]
    dim_medico = data_dict["DimMedico"]
    dim_prestacion = data_dict["DimPrestacion"]
    hecho_reservas = data_dict["HechoReservas"]
    hecho_detalle = data_dict["HechoDetalle"]

    sidebar_brand()
    st.sidebar.markdown("---")
    
    pagina = st.sidebar.radio(
        "Navegación",
        ["Resumen", "Visión ejecutiva", "Gestión médica", "Pacientes", "Pruebas de aceptación"]
    )
    
    st.sidebar.markdown("---")
    
    sidebar_section("Filtros globales")

    min_res_date = date(2026, 1, 5)
    max_res_date = date(2026, 2, 28)

    comunas_disp = sorted(dim_paciente["Comuna"].dropna().unique().tolist()) if "Comuna" in dim_paciente.columns else []
    sexos_disp = sorted(dim_paciente["Sexo"].dropna().unique().tolist()) if "Sexo" in dim_paciente.columns else []

    if "filtro_fechas" not in st.session_state:
        st.session_state.filtro_fechas = (min_res_date, max_res_date)
    if "filtro_comuna" not in st.session_state:
        st.session_state.filtro_comuna = comunas_disp
    if "filtro_sexo" not in st.session_state:
        st.session_state.filtro_sexo = sexos_disp

    if st.sidebar.button("Limpiar filtros"):
        st.session_state.filtro_fechas = (min_res_date, max_res_date)
        st.session_state.filtro_comuna = comunas_disp
        st.session_state.filtro_sexo = sexos_disp
        st.rerun()

    rango_fechas = st.sidebar.date_input(
        "Rango de fechas",
        min_value=date(2026, 1, 1),
        max_value=date(2026, 12, 31),
        key="filtro_fechas"
    )

    sel_comuna = chip_filter("Comuna", comunas_disp, key="filtro_comuna")
    sel_sexo = chip_filter("Sexo", sexos_disp, key="filtro_sexo")

    # Filtrado de hechos
    df_res_filtered = hecho_reservas.copy()
    df_det_filtered = hecho_detalle.copy()

    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        start_date, end_date = rango_fechas
        if start_date:
            df_res_filtered = df_res_filtered[df_res_filtered["FechaReserva"] >= start_date]
            df_det_filtered = df_det_filtered[df_det_filtered["FechaAtencion"] >= start_date]
        if end_date:
            df_res_filtered = df_res_filtered[df_res_filtered["FechaReserva"] <= end_date]
            df_det_filtered = df_det_filtered[df_det_filtered["FechaAtencion"] <= end_date]

    if sel_comuna and "Comuna" in df_res_filtered.columns:
        df_res_filtered = df_res_filtered[df_res_filtered["Comuna"].isin(sel_comuna)]
    if sel_comuna and "Comuna" in df_det_filtered.columns:
        df_det_filtered = df_det_filtered[df_det_filtered["Comuna"].isin(sel_comuna)]

    if sel_sexo and "Sexo" in df_res_filtered.columns:
        df_res_filtered = df_res_filtered[df_res_filtered["Sexo"].isin(sel_sexo)]
    if sel_sexo and "Sexo" in df_det_filtered.columns:
        df_det_filtered = df_det_filtered[df_det_filtered["Sexo"].isin(sel_sexo)]

    # Pacientes cartera (filtrado por comuna y sexo, sin fecha)
    df_pac_cartera = dim_paciente.copy()
    if sel_comuna and "Comuna" in df_pac_cartera.columns:
        df_pac_cartera = df_pac_cartera[df_pac_cartera["Comuna"].isin(sel_comuna)]
    if sel_sexo and "Sexo" in df_pac_cartera.columns:
        df_pac_cartera = df_pac_cartera[df_pac_cartera["Sexo"].isin(sel_sexo)]

    medidas = calcular_medidas(df_res_filtered, df_det_filtered, df_pac_cartera)

    # ----------------------------------------------------
    # PÁGINA 1: RESUMEN
    # ----------------------------------------------------
    if pagina == "Resumen":
        page_header("Resumen", "Cuadro de mando ejecutivo y recomendaciones operacionales.")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total de reservas", format_num(medidas["TotalReservas"]))
        with c2:
            st.metric("Tasa de atención", format_pct(medidas["TasaAtencion"]))
        with c3:
            st.metric("Tasa de inasistencia", format_pct(medidas["TasaInasistencia"]))
        with c4:
            st.metric("Ingreso valorizado", format_clp(medidas["Ingresos"]))

        st.markdown("---")

        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("CONCLUSIONES")
            st.markdown("""
            - De 70 reservas resueltas, 48 terminaron en atención (68,6 %). La inasistencia es 20,0 % y la cancelación 14,3 %.
            - La inasistencia subió de 16,7 % en enero a 22,2 % en febrero. Con solo 2 meses de datos no se puede confirmar una tendencia.
            - Se perdieron 5,0 horas por inasistencia, todas en febrero y solo en reservas con bloque horario (51 % del total).
            - El Dr. Rodrigo Soto concentra 4 inasistencias en 6 reservas.
            - Cardiología y Dermatología concentran la mayor demanda (11 reservas cada una). Dermatología lidera el ingreso valorizado ($363.000).
            - Concepción concentra la mayor cantidad de atenciones (19). FONASA reúne 43 reservas e Isapre 32.
            - 27 de los 44 pacientes tienen una sola reserva.
            """)

        with col_r:
            st.subheader("RECOMENDACIONES OPERACIONALES")
            st.markdown("""
            - Enviar recordatorios de cita (llamada o mensaje) 24 a 48 horas antes, priorizando los canales con más inasistencia (Teléfono y App) y las agendas más afectadas.
            - Registrar canal y bloque horario en todas las reservas: hoy solo el 51 % los tiene.
            - Cerrar las reservas pendientes de febrero con un seguimiento diario de recepción.
            - Registrar las atenciones faltantes de 2 reservas atendidas y completar el valor unitario de 5 atenciones sin tarifa.
            - Revisar las tarifas: 12 de 41 detalles tienen un valor distinto de la tarifa maestra.
            - Contactar a los pacientes con una sola reserva para favorecer su retorno.
            - Ampliar el período de datos antes de decidir cambios de dotación o de agenda.
            """)

        st.markdown("---")
        st.info(NOTA_VISIBLE)

    # ----------------------------------------------------
    # PÁGINA 2: VISIÓN EJECUTIVA
    # ----------------------------------------------------
    elif pagina == "Visión ejecutiva":
        page_header("Visión ejecutiva", "Evolución mensual, distribución por estados, especialidades e ingresos.")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.metric("Total de reservas", format_num(medidas["TotalReservas"]))
        with c2:
            st.metric("Atenciones registradas", format_num(medidas["AtencionesRealizadas"]))
        with c3:
            st.metric("Tasa de atención", format_pct(medidas["TasaAtencion"]))
        with c4:
            st.metric("Tasa de inasistencia", format_pct(medidas["TasaInasistencia"]))
        with c5:
            st.metric("Ingreso valorizado", format_clp(medidas["Ingresos"]))
        with c6:
            st.metric("Ingreso promedio / at.", format_clp(medidas["IngresoPromedio"]))

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Reservas por estado")
            if "EstadoReserva" in df_res_filtered.columns and not df_res_filtered.empty:
                df_estado = df_res_filtered.groupby("EstadoReserva").size().reset_index(name="TotalReservas")
                fig_est = px.pie(
                    df_estado,
                    names="EstadoReserva",
                    values="TotalReservas",
                    hole=0.4,
                    color_discrete_sequence=PALETTE
                )
                fig_est.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_est, use_container_width=True)
            else:
                st.info("Sin datos de estado.")

        with col2:
            st.subheader("Reservas por mes")
            if "FechaReserva" in df_res_filtered.columns and not df_res_filtered.empty:
                df_res_m = df_res_filtered.copy()
                df_res_m["MesNum"] = pd.to_datetime(df_res_m["FechaReserva"]).dt.month
                df_res_m["Mes"] = pd.to_datetime(df_res_m["FechaReserva"]).dt.strftime("%B").map({
                    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
                    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
                    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
                }).fillna(df_res_m["MesNum"].astype(str))
                df_mes = df_res_m.groupby(["MesNum", "Mes"]).size().reset_index(name="TotalReservas").sort_values("MesNum")
                
                fig_mes = px.bar(
                    df_mes,
                    x="Mes",
                    y="TotalReservas",
                    text="TotalReservas",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_mes.update_traces(textposition="outside")
                st.plotly_chart(fig_mes, use_container_width=True)
            else:
                st.info("Sin datos de fecha de reserva.")

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Reservas por especialidad (del médico)")
            if "Especialidad" in df_res_filtered.columns and not df_res_filtered.empty:
                df_esp = df_res_filtered.groupby("Especialidad").size().reset_index(name="TotalReservas")
                df_esp = df_esp.sort_values("TotalReservas", ascending=True)
                fig_esp = px.bar(
                    df_esp,
                    x="TotalReservas",
                    y="Especialidad",
                    orientation="h",
                    text="TotalReservas",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_esp.update_traces(textposition="outside")
                st.plotly_chart(fig_esp, use_container_width=True)
            else:
                st.info("Sin datos de especialidad.")

        with col4:
            st.subheader("Ingreso valorizado por mes")
            if "FechaAtencion" in df_det_filtered.columns and not df_det_filtered.empty:
                df_det_m = df_det_filtered.copy()
                df_det_m["MesNum"] = pd.to_datetime(df_det_m["FechaAtencion"]).dt.month
                df_det_m["Mes"] = pd.to_datetime(df_det_m["FechaAtencion"]).dt.strftime("%B").map({
                    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
                    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
                    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
                }).fillna(df_det_m["MesNum"].astype(str))
                df_ing_mes = df_det_m.groupby(["MesNum", "Mes"])["Importe"].sum().reset_index().sort_values("MesNum")
                df_ing_mes["ImporteStr"] = df_ing_mes["Importe"].apply(format_clp)

                fig_ing = px.bar(
                    df_ing_mes,
                    x="Mes",
                    y="Importe",
                    text="ImporteStr",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_ing.update_traces(textposition="outside")
                st.plotly_chart(fig_ing, use_container_width=True)
            else:
                st.info("Sin datos de ingresos mensuales.")

        st.subheader("Tasas por mes")
        if not df_res_filtered.empty and "FechaReserva" in df_res_filtered.columns:
            df_res_t = df_res_filtered.copy()
            df_res_t["MesNum"] = pd.to_datetime(df_res_t["FechaReserva"]).dt.month
            df_res_t["Mes"] = pd.to_datetime(df_res_t["FechaReserva"]).dt.strftime("%B").map({
                "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
                "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
                "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
            }).fillna(df_res_t["MesNum"].astype(str))
            
            tasas_mes_rows = []
            for (mnum, mname), group in df_res_t.groupby(["MesNum", "Mes"]):
                m_sub = calcular_medidas(group, df_det_filtered[pd.to_datetime(df_det_filtered["FechaAtencion"]).dt.month == mnum] if "FechaAtencion" in df_det_filtered.columns else df_det_filtered)
                tasas_mes_rows.append({
                    "Mes": mname,
                    "Tasa de Atención": format_pct(m_sub["TasaAtencion"]),
                    "Tasa de Inasistencia": format_pct(m_sub["TasaInasistencia"]),
                    "Tasa de Cancelación": format_pct(m_sub["TasaCancelacion"])
                })
            df_tasas_mes = pd.DataFrame(tasas_mes_rows)
            st.dataframe(df_tasas_mes, use_container_width=True)
        else:
            st.info("Sin datos para calcular tasas por mes.")

        st.markdown("---")
        st.info(NOTA_VISIBLE)

    # ----------------------------------------------------
    # PÁGINA 3: GESTIÓN MÉDICA
    # ----------------------------------------------------
    elif pagina == "Gestión médica":
        page_header("Gestión médica", "Desempeño por profesional, estados de reserva y horas perdidas.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Reservas atendidas por médico")
            if "Medico" in df_res_filtered.columns and not df_res_filtered.empty:
                df_med_at = df_res_filtered[df_res_filtered["EstadoReserva"] == "Atendida"].groupby("Medico").size().reset_index(name="ReservasAtendidas")
                df_med_at = df_med_at.sort_values("ReservasAtendidas", ascending=True)
                fig_med_at = px.bar(
                    df_med_at,
                    x="ReservasAtendidas",
                    y="Medico",
                    orientation="h",
                    text="ReservasAtendidas",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_med_at.update_traces(textposition="outside")
                st.plotly_chart(fig_med_at, use_container_width=True)
            else:
                st.info("Sin datos.")

        with col2:
            st.subheader("Reservas por estado y médico")
            if "Medico" in df_res_filtered.columns and "EstadoReserva" in df_res_filtered.columns and not df_res_filtered.empty:
                df_med_est = df_res_filtered.groupby(["Medico", "EstadoReserva"]).size().reset_index(name="Total")
                fig_med_est = px.bar(
                    df_med_est,
                    x="Total",
                    y="Medico",
                    color="EstadoReserva",
                    orientation="h",
                    color_discrete_sequence=PALETTE
                )
                st.plotly_chart(fig_med_est, use_container_width=True)
            else:
                st.info("Sin datos.")

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Tasa de inasistencia por especialidad")
            if "Especialidad" in df_res_filtered.columns and "EstadoReserva" in df_res_filtered.columns and not df_res_filtered.empty:
                esp_list = []
                for esp, grp in df_res_filtered.groupby("Especialidad"):
                    m_esp = calcular_medidas(grp, pd.DataFrame())
                    esp_list.append({"Especialidad": esp, "TasaInasistencia": m_esp["TasaInasistencia"] * 100})
                df_esp_inas = pd.DataFrame(esp_list).sort_values("TasaInasistencia", ascending=True)
                df_esp_inas["TasaStr"] = df_esp_inas["TasaInasistencia"].apply(lambda x: f"{x:.1f} %".replace(".", ","))
                
                fig_esp_in = px.bar(
                    df_esp_inas,
                    x="TasaInasistencia",
                    y="Especialidad",
                    orientation="h",
                    text="TasaStr",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_esp_in.update_traces(textposition="outside")
                st.plotly_chart(fig_esp_in, use_container_width=True)
            else:
                st.info("Sin datos.")

        with col4:
            st.subheader("Horas perdidas por inasistencia (por mes)")
            if "FechaReserva" in df_res_filtered.columns and "BloqueMinutos" in df_res_filtered.columns and not df_res_filtered.empty:
                df_hp = df_res_filtered.copy()
                df_hp["MesNum"] = pd.to_datetime(df_hp["FechaReserva"]).dt.month
                df_hp["Mes"] = pd.to_datetime(df_hp["FechaReserva"]).dt.strftime("%B").map({
                    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
                    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
                    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
                }).fillna(df_hp["MesNum"].astype(str))
                
                hp_rows = []
                for (mnum, mname), grp in df_hp.groupby(["MesNum", "Mes"]):
                    m_hp = calcular_medidas(grp, pd.DataFrame())
                    hp_rows.append({"Mes": mname, "MesNum": mnum, "HorasPerdidas": round(m_hp["HorasPerdidas"], 1)})
                df_hp_res = pd.DataFrame(hp_rows).sort_values("MesNum")
                df_hp_res["HpStr"] = df_hp_res["HorasPerdidas"].apply(lambda x: f"{x:.1f}")

                fig_hp = px.bar(
                    df_hp_res,
                    x="Mes",
                    y="HorasPerdidas",
                    text="HpStr",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_hp.update_traces(textposition="outside")
                st.plotly_chart(fig_hp, use_container_width=True)
            else:
                st.info("Sin datos.")

        st.subheader("Horas perdidas por canal (solo reservas con bloque)")
        if "Canal" in df_res_filtered.columns and "BloqueMinutos" in df_res_filtered.columns and not df_res_filtered.empty:
            df_can = df_res_filtered[df_res_filtered["EstadoReserva"] == "No asistió"]
            df_can_hp = df_can.groupby("Canal")["BloqueMinutos"].sum().reset_index(name="Minutos")
            df_can_hp["HorasPerdidas"] = df_can_hp["Minutos"] / 60.0
            df_can_hp = df_can_hp.sort_values("HorasPerdidas", ascending=True)
            df_can_hp["HpStr"] = df_can_hp["HorasPerdidas"].apply(lambda x: f"{x:.1f}")

            fig_can = px.bar(
                df_can_hp,
                x="HorasPerdidas",
                y="Canal",
                orientation="h",
                text="HpStr",
                color_discrete_sequence=[COLOR_BARS]
            )
            fig_can.update_traces(textposition="outside")
            st.plotly_chart(fig_can, use_container_width=True)
        else:
            st.info("Sin datos de canal.")

        st.subheader("Desempeño por médico")
        if "Medico" in df_res_filtered.columns and not df_res_filtered.empty:
            med_rows = []
            for medico, grp_m in df_res_filtered.groupby("Medico"):
                m_sub = calcular_medidas(grp_m, df_det_filtered[df_det_filtered["MedicoID"].isin(grp_m["MedicoID"])] if "MedicoID" in df_det_filtered.columns else pd.DataFrame())
                med_id = grp_m["MedicoID"].iloc[0] if "MedicoID" in grp_m.columns else None
                ing_med = df_det_filtered[df_det_filtered["MedicoID"] == med_id]["Importe"].sum() if med_id and "MedicoID" in df_det_filtered.columns else 0.0
                det_med = df_det_filtered[df_det_filtered["MedicoID"] == med_id] if med_id and "MedicoID" in df_det_filtered.columns else pd.DataFrame()
                dist_at_med = det_med["AtencionID"].nunique() if "AtencionID" in det_med.columns and not det_med.empty else 0
                prom_med = ing_med / dist_at_med if dist_at_med > 0 else 0.0

                med_rows.append({
                    "Médico": medico,
                    "Total Reservas": m_sub["TotalReservas"],
                    "Reservas Atendidas": m_sub["Atendidas"],
                    "Reservas No Asistió": m_sub["NoAsistio"],
                    "Reservas Canceladas": m_sub["Canceladas"],
                    "Reservas Pendientes": m_sub["Pendientes"],
                    "Tasa de Atención": m_sub["TasaAtencion"],
                    "Ingresos": ing_med,
                    "Ingreso Promedio por Atención": prom_med
                })
            df_desempeno = pd.DataFrame(med_rows).sort_values("Total Reservas", ascending=False)
            
            def color_tasa(val):
                if pd.isna(val):
                    return ""
                return 'color: #EF4444; font-weight: bold;' if val < 0.5 else 'color: #10B981; font-weight: bold;'

            format_dict = {
                "Tasa de Atención": lambda x: format_pct(x) if pd.notna(x) else "—",
                "Ingresos": format_clp,
                "Ingreso Promedio por Atención": format_clp
            }
            if hasattr(df_desempeno.style, "map"):
                styled_df = df_desempeno.style.map(color_tasa, subset=["Tasa de Atención"])
            elif hasattr(df_desempeno.style, "applymap"):
                styled_df = df_desempeno.style.applymap(color_tasa, subset=["Tasa de Atención"])
            else:
                styled_df = df_desempeno.style.apply(color_tasa, subset=["Tasa de Atención"])
            st.dataframe(styled_df.format(format_dict), use_container_width=True)
        else:
            st.info("Sin datos de médico.")

        st.markdown("---")
        st.info(NOTA_VISIBLE)

    # ----------------------------------------------------
    # PÁGINA 4: PACIENTES
    # ----------------------------------------------------
    elif pagina == "Pacientes":
        page_header("Pacientes", "Análisis demográfico, comunas, previsión y frecuencia de uso.")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Pacientes con reservas", format_num(medidas["PacientesDistintos"]))
        with c2:
            st.metric("Reservas por paciente", f"{medidas['ReservasPorPaciente']:.1f}".replace(".", ","))

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Reservas atendidas por comuna")
            if "Comuna" in df_res_filtered.columns and not df_res_filtered.empty:
                df_com = df_res_filtered[df_res_filtered["EstadoReserva"] == "Atendida"].groupby("Comuna").size().reset_index(name="ReservasAtendidas")
                df_com = df_com.sort_values("ReservasAtendidas", ascending=True)
                fig_com = px.bar(
                    df_com,
                    x="ReservasAtendidas",
                    y="Comuna",
                    orientation="h",
                    text="ReservasAtendidas",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_com.update_traces(textposition="outside")
                st.plotly_chart(fig_com, use_container_width=True)
            else:
                st.info("Sin datos de comuna.")

        with col2:
            st.subheader("Reservas por previsión")
            if "Prevision" in df_res_filtered.columns and not df_res_filtered.empty:
                df_prev_res = df_res_filtered.groupby("Prevision").size().reset_index(name="TotalReservas")
                fig_pr = px.pie(
                    df_prev_res,
                    names="Prevision",
                    values="TotalReservas",
                    hole=0.4,
                    color_discrete_map={"FONASA": COLOR_FONASA, "Isapre": COLOR_ISAPRE_PRIMARY}
                )
                fig_pr.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_pr, use_container_width=True)
            else:
                st.info("Sin datos de previsión.")

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Ingresos por previsión (valorizado)")
            if "Prevision" in df_det_filtered.columns and not df_det_filtered.empty:
                df_prev_ing = df_det_filtered.groupby("Prevision")["Importe"].sum().reset_index()
                fig_pi = px.pie(
                    df_prev_ing,
                    names="Prevision",
                    values="Importe",
                    hole=0.4,
                    color_discrete_map={"FONASA": COLOR_FONASA, "Isapre": COLOR_ISAPRE_PRIMARY}
                )
                fig_pi.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_pi, use_container_width=True)
            else:
                st.info("Sin datos de ingresos por previsión.")

        with col4:
            st.subheader("Frecuencia de uso (reservas por paciente)")
            # Responde a comuna y sexo, pero NO al filtro de fecha
            df_cartera_freq = df_pac_cartera.copy()
            if "Tramo Frecuencia" in df_cartera_freq.columns:
                orden_tramo_map = {"Sin reservas": 0, "1 reserva": 1, "2 a 3 reservas": 2, "4 o más": 3}
                df_freq = df_cartera_freq.groupby(["Tramo Frecuencia", "Orden Tramo"]).size().reset_index(name="Pacientes")
                df_freq = df_freq.sort_values("Orden Tramo")
                
                fig_freq = px.bar(
                    df_freq,
                    x="Tramo Frecuencia",
                    y="Pacientes",
                    text="Pacientes",
                    color_discrete_sequence=[COLOR_BARS]
                )
                fig_freq.update_traces(textposition="outside")
                st.plotly_chart(fig_freq, use_container_width=True)
            else:
                st.info("Sin datos de frecuencia.")

        st.subheader("Pacientes distintos por mes")
        if "FechaReserva" in df_res_filtered.columns and not df_res_filtered.empty:
            df_pac_m = df_res_filtered.copy()
            df_pac_m["MesNum"] = pd.to_datetime(df_pac_m["FechaReserva"]).dt.month
            df_pac_m["Mes"] = pd.to_datetime(df_pac_m["FechaReserva"]).dt.strftime("%B").map({
                "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
                "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
                "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
            }).fillna(df_pac_m["MesNum"].astype(str))
            
            df_p_mes = df_pac_m.groupby(["MesNum", "Mes"])["PacienteID"].nunique().reset_index(name="PacientesDistintos").sort_values("MesNum")
            
            fig_p_mes = px.bar(
                df_p_mes,
                x="Mes",
                y="PacientesDistintos",
                text="PacientesDistintos",
                color_discrete_sequence=[COLOR_BARS]
            )
            fig_p_mes.update_traces(textposition="outside")
            st.plotly_chart(fig_p_mes, use_container_width=True)
        else:
            st.info("Sin datos.")

        st.subheader("Pacientes con 2 o más inasistencias (solo IDs)")
        if "PacienteID" in df_res_filtered.columns and "EstadoReserva" in df_res_filtered.columns and not df_res_filtered.empty:
            df_inas = df_res_filtered[df_res_filtered["EstadoReserva"] == "No asistió"].groupby("PacienteID").size().reset_index(name="Reservas No Asistió")
            df_inas = df_inas[df_inas["Reservas No Asistió"] >= 2]
            if not df_inas.empty:
                st.dataframe(df_inas, use_container_width=True)
            else:
                st.info("Sin pacientes con 2 o más inasistencias.")
        else:
            st.info("Sin datos.")

        st.markdown("---")
        st.info(NOTA_VISIBLE)

    # ----------------------------------------------------
    # PÁGINA 5: PRUEBAS DE ACEPTACIÓN
    # ----------------------------------------------------
    elif pagina == "Pruebas de aceptación":
        page_header("Pruebas de Aceptación", "Validación automática de los 16 indicadores clave del modelo dimensional y financiero.")

        pruebas = ejecutar_pruebas_aceptacion(hecho_reservas, hecho_detalle)
        df_pruebas = pd.DataFrame(pruebas)

        def style_ok(val):
            return 'color: #10B981; font-weight: bold;' if val else 'color: #EF4444; font-weight: bold;'

        if hasattr(df_pruebas.style, "map"):
            styled_pruebas = df_pruebas.style.map(style_ok, subset=["ok"])
        elif hasattr(df_pruebas.style, "applymap"):
            styled_pruebas = df_pruebas.style.applymap(style_ok, subset=["ok"])
        else:
            styled_pruebas = df_pruebas.style.apply(style_ok, subset=["ok"])
        st.dataframe(styled_pruebas, use_container_width=True)
        
        ok_count = sum(1 for p in pruebas if p["ok"])
        total_count = len(pruebas)
        if ok_count == total_count:
            st.success(f"¡Todas las pruebas de aceptación pasaron exitosamente ({ok_count}/{total_count})!")
        else:
            st.warning(f"Se pasaron {ok_count} de {total_count} pruebas.")

if __name__ == "__main__":
    main()
