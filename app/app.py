"""
Aplicación principal en Streamlit para el dashboard de SaludVital.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px

from data import prepare_data
from medidas import calcular_medidas, format_clp, format_pct, format_num, ejecutar_pruebas_aceptacion

# Configuración de la página
st.set_page_config(
    page_title="SaludVital - Centro Médico Ambulatorio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo y paleta consistente
COLOR_PRIMARY = "#1f77b4"
PALETTE = px.colors.qualitative.Bold

# Estilos CSS avanzados para filtros y panel dinámico en Modo Oscuro Total
st.markdown("""
<style>
    /* Panel lateral y filtros tipo selector / tarjeta en modo oscuro */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    .filter-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .filter-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 2px solid #334155;
        padding-bottom: 8px;
    }
    /* Estilización de multiselect y selectores oscuros */
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #0f172a;
        border-radius: 8px;
        border-color: #334155;
    }
    .stDateInput input {
        border-radius: 8px;
        border-color: #334155;
        background-color: #0f172a;
        color: #f8fafc;
    }
    /* Botones tipo selector oscuros */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #334155;
        background-color: #1e293b;
        color: #f8fafc;
        transition: all 0.2s ease-in-out;
    }
    .stButton button:hover {
        border-color: #38bdf8;
        color: #38bdf8;
        background-color: #0f172a;
        box-shadow: 0 2px 4px rgba(56, 189, 248, 0.15);
    }
</style>
""", unsafe_allow_html=True)

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

    st.sidebar.title("SaludVital")
    st.sidebar.markdown("Centro Médico Ambulatorio")
    st.sidebar.markdown("---")
    
    pagina = st.sidebar.radio(
        "Navegación",
        ["Resumen de reservas", "Ingresos y prestaciones", "Pruebas de aceptación"]
    )
    
    st.sidebar.markdown("---")
    
    # Contenedor HTML dinámico para los filtros estilo tarjeta / selector
    st.sidebar.markdown('<div class="filter-card">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="filter-header">Filtros Globales</div>', unsafe_allow_html=True)

    min_res_date = hecho_reservas["FechaReserva"].min() if not hecho_reservas.empty else pd.to_datetime("2026-01-05").date()
    max_res_date = hecho_reservas["FechaReserva"].max() if not hecho_reservas.empty else pd.to_datetime("2026-03-31").date()

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
        value=st.session_state.filtro_fechas,
        min_value=min_res_date,
        max_value=max_res_date
    )
    st.session_state.filtro_fechas = rango_fechas

    sel_comuna = st.sidebar.multiselect(
        "Comuna",
        options=comunas_disp,
        default=st.session_state.filtro_comuna
    )
    st.session_state.filtro_comuna = sel_comuna

    sel_sexo = st.sidebar.multiselect(
        "Sexo",
        options=sexos_disp,
        default=st.session_state.filtro_sexo
    )
    st.session_state.filtro_sexo = sel_sexo
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.session_state.filtro_sexo = sel_sexo

    st.sidebar.markdown("---")
    st.sidebar.caption("Pie de página: Datos simulados")

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
    elif isinstance(rango_fechas, date):
        df_res_filtered = df_res_filtered[df_res_filtered["FechaReserva"] == rango_fechas]
        df_det_filtered = df_det_filtered[df_det_filtered["FechaAtencion"] == rango_fechas]

    if sel_comuna and "Comuna" in df_res_filtered.columns:
        df_res_filtered = df_res_filtered[df_res_filtered["Comuna"].isin(sel_comuna)]
    if sel_comuna and "Comuna" in df_det_filtered.columns:
        df_det_filtered = df_det_filtered[df_det_filtered["Comuna"].isin(sel_comuna)]

    if sel_sexo and "Sexo" in df_res_filtered.columns:
        df_res_filtered = df_res_filtered[df_res_filtered["Sexo"].isin(sel_sexo)]
    if sel_sexo and "Sexo" in df_det_filtered.columns:
        df_det_filtered = df_det_filtered[df_det_filtered["Sexo"].isin(sel_sexo)]

    medidas = calcular_medidas(df_res_filtered, df_det_filtered)

    if pagina == "Resumen de reservas":
        st.title("Resumen de Reservas")
        st.markdown("Tablero de control de reservas y atenciones del centro médico ambulatorio.")

        if df_res_filtered.empty:
            st.info("Sin datos para los filtros seleccionados")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Reservas", format_num(medidas["TotalReservas"]))
            with col2:
                st.metric("Atenciones Realizadas", format_num(medidas["AtencionesRealizadas"]))
            with col3:
                st.metric("Pacientes Distintos", format_num(medidas["PacientesDistintos"]))
            with col4:
                st.metric("Ingresos", format_clp(medidas["Ingresos"]))

            st.markdown("---")

            st.subheader("Reservas por Día")
            df_res_dia = df_res_filtered.groupby("FechaReserva").size().reset_index(name="TotalReservas")
            df_res_dia["FechaReserva"] = pd.to_datetime(df_res_dia["FechaReserva"])
            df_res_dia = df_res_dia.sort_values("FechaReserva")
            
            fig_dia = px.line(
                df_res_dia,
                x="FechaReserva",
                y="TotalReservas",
                labels={"FechaReserva": "Fecha de Reserva", "TotalReservas": "Total Reservas"},
                markers=True,
                color_discrete_sequence=[COLOR_PRIMARY]
            )
            fig_dia.update_layout(xaxis_title="Fecha de Reserva", yaxis_title="Total Reservas", hovermode="x unified")
            st.plotly_chart(fig_dia, use_container_width=True)

            col_l, col_r = st.columns(2)

            with col_l:
                st.subheader("Reservas por Médico")
                if "Medico" in df_res_filtered.columns:
                    df_med = df_res_filtered.groupby("Medico").size().reset_index(name="TotalReservas")
                    df_med = df_med.sort_values("TotalReservas", ascending=True)
                    fig_med = px.bar(
                        df_med,
                        x="TotalReservas",
                        y="Medico",
                        orientation="h",
                        labels={"TotalReservas": "Total Reservas", "Medico": "Médico"},
                        color_discrete_sequence=[COLOR_PRIMARY]
                    )
                    fig_med.update_layout(xaxis_title="Total Reservas", yaxis_title="Médico")
                    st.plotly_chart(fig_med, use_container_width=True)
                else:
                    st.info("Columna de médico no disponible.")

            with col_r:
                st.subheader("Reservas por Previsión")
                if "Prevision" in df_res_filtered.columns:
                    df_prev = df_res_filtered.groupby("Prevision").size().reset_index(name="TotalReservas")
                    fig_prev = px.pie(
                        df_prev,
                        names="Prevision",
                        values="TotalReservas",
                        hole=0.4,
                        color_discrete_sequence=PALETTE
                    )
                    fig_prev.update_traces(textinfo="percent+label")
                    st.plotly_chart(fig_prev, use_container_width=True)
                else:
                    st.info("Columna de previsión no disponible.")

    elif pagina == "Ingresos y prestaciones":
        st.title("Ingresos y Prestaciones")
        st.markdown("Análisis financiero y de prestaciones médicas.")

        if df_det_filtered.empty:
            st.info("Sin datos para los filtros seleccionados")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ingresos", format_clp(medidas["Ingresos"]))
            with col2:
                st.metric("Ingreso Promedio por Atención", format_clp(medidas["IngresoPromedio"]))
            with col3:
                st.metric("Prestaciones Realizadas", format_num(medidas["PrestacionesRealizadas"]))

            st.markdown("---")

            st.info("Nota: Ingreso valorizado (cantidad × valor unitario), no corresponde a cobros efectivos.")

            col_l, col_r = st.columns(2)

            with col_l:
                st.subheader("Ingresos por Especialidad")
                if "Especialidad" in df_det_filtered.columns:
                    df_esp_ing = df_det_filtered.groupby("Especialidad")["Importe"].sum().reset_index()
                    df_esp_ing = df_esp_ing.sort_values("Importe", ascending=True)
                    fig_esp = px.bar(
                        df_esp_ing,
                        x="Importe",
                        y="Especialidad",
                        orientation="h",
                        labels={"Importe": "Ingresos (CLP)", "Especialidad": "Especialidad"},
                        color_discrete_sequence=[COLOR_PRIMARY]
                    )
                    st.plotly_chart(fig_esp, use_container_width=True)
                else:
                    st.info("Especialidad no disponible en detalle.")

            with col_r:
                st.subheader("Top 10 Prestaciones")
                if "Prestacion" in df_det_filtered.columns:
                    df_prest = df_det_filtered.groupby("Prestacion")["Cantidad"].sum().reset_index()
                    df_prest = df_prest.sort_values("Cantidad", ascending=False).head(10)
                    df_prest = df_prest.sort_values("Cantidad", ascending=True)
                    fig_top = px.bar(
                        df_prest,
                        x="Cantidad",
                        y="Prestacion",
                        orientation="h",
                        labels={"Cantidad": "Prestaciones Realizadas", "Prestacion": "Prestación"},
                        color_discrete_sequence=[COLOR_PRIMARY]
                    )
                    st.plotly_chart(fig_top, use_container_width=True)
                else:
                    st.info("Prestación no disponible.")

            col_l2, col_r2 = st.columns(2)

            with col_l2:
                st.subheader("Ingresos por Día")
                if "FechaAtencion" in df_det_filtered.columns:
                    df_det_dia = df_det_filtered.groupby("FechaAtencion")["Importe"].sum().reset_index()
                    df_det_dia["FechaAtencion"] = pd.to_datetime(df_det_dia["FechaAtencion"])
                    df_det_dia = df_det_dia.sort_values("FechaAtencion")
                    fig_det_dia = px.line(
                        df_det_dia,
                        x="FechaAtencion",
                        y="Importe",
                        labels={"FechaAtencion": "Fecha de Atención", "Importe": "Ingresos (CLP)"},
                        markers=True,
                        color_discrete_sequence=[COLOR_PRIMARY]
                    )
                    st.plotly_chart(fig_det_dia, use_container_width=True)
                else:
                    st.info("Fecha de atención no disponible.")

            with col_r2:
                st.subheader("Ingresos por Previsión")
                if "Prevision" in df_det_filtered.columns:
                    df_prev_ing = df_det_filtered.groupby("Prevision")["Importe"].sum().reset_index()
                    fig_prev_ing = px.pie(
                        df_prev_ing,
                        names="Prevision",
                        values="Importe",
                        hole=0.4,
                        color_discrete_sequence=PALETTE
                    )
                    fig_prev_ing.update_traces(textinfo="percent+label")
                    st.plotly_chart(fig_prev_ing, use_container_width=True)
                else:
                    st.info("Previsión no disponible en detalle.")

    elif pagina == "Pruebas de aceptación":
        st.title("Pruebas de Aceptación (Sin Filtros)")
        st.markdown("Verificación automática de los indicadores clave requeridos en la especificación.")

        pruebas = ejecutar_pruebas_aceptacion(hecho_reservas, hecho_detalle)
        df_pruebas = pd.DataFrame(pruebas)

        st.dataframe(df_pruebas, use_container_width=True)

        all_passed = df_pruebas["ok"].all()
        if all_passed:
            st.success("Todas las pruebas de aceptación pasaron exitosamente y coinciden con la documentación oficial.")
        else:
            st.error("Algunas pruebas de aceptación no coinciden con los valores esperados.")

if __name__ == "__main__":
    main()
