"""
Carga de datos y modelado en estrella para el dashboard de SaludVital.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path

DATA_PATHS = [
    Path("data/modelo"),
    Path("data"),
]

def find_file(filename: str) -> Path | None:
    for base in DATA_PATHS:
        p = base / filename
        if p.exists():
            return p
    return None

@st.cache_data
def load_table(filename: str) -> pd.DataFrame | None:
    p = find_file(filename)
    if p and p.exists():
        return pd.read_csv(p)
    return None

def get_data_or_uploader():
    """
    Carga las 6 tablas requeridas. Si alguna falta, permite subirla vía st.file_uploader.
    """
    tables = {
        "DimFecha.csv": "DimFecha",
        "DimPaciente.csv": "DimPaciente",
        "DimMedico.csv": "DimMedico",
        "DimPrestacion.csv": "DimPrestacion",
        "HechoReservas.csv": "HechoReservas",
        "HechoDetalle.csv": "HechoDetalle"
    }
    
    loaded = {}
    missing = []
    
    for filename, key in tables.items():
        df = load_table(filename)
        if df is not None:
            loaded[key] = df
        else:
            missing.append((filename, key))
            
    if missing:
        st.warning(f"No se encontraron algunos archivos CSV automáticamente en data/ o data/modelo/. Por favor cargue los archivos faltantes.")
        for filename, key in missing:
            uploaded_file = st.file_uploader(f"Cargar {filename}", type="csv", key=f"upload_{key}")
            if uploaded_file is not None:
                loaded[key] = pd.read_csv(uploaded_file)
            else:
                return None
                
    return loaded

def prepare_data():
    data = get_data_or_uploader()
    if data is None:
        return None
        
    dim_fecha = data["DimFecha"]
    dim_paciente = data["DimPaciente"].copy()
    dim_medico = data["DimMedico"]
    dim_prestacion = data["DimPrestacion"]
    hecho_reservas = data["HechoReservas"].copy()
    hecho_detalle = data["HechoDetalle"].copy()
    
    # Conversión de fechas
    if "FechaReserva" in hecho_reservas.columns:
        hecho_reservas["FechaReserva"] = pd.to_datetime(hecho_reservas["FechaReserva"]).dt.date
    if "FechaAtencion" in hecho_detalle.columns:
        hecho_detalle["FechaAtencion"] = pd.to_datetime(hecho_detalle["FechaAtencion"]).dt.date
    if "Date" in dim_fecha.columns:
        dim_fecha["Date"] = pd.to_datetime(dim_fecha["Date"]).dt.date

    # Columnas calculadas en DimPaciente (sobre HechoReservas SIN filtros)
    if "PacienteID" in hecho_reservas.columns and "PacienteID" in dim_paciente.columns:
        conteo_reservas = hecho_reservas.groupby("PacienteID").size().reset_index(name="Reservas del Paciente")
        dim_paciente = dim_paciente.merge(conteo_reservas, on="PacienteID", how="left")
        dim_paciente["Reservas del Paciente"] = dim_paciente["Reservas del Paciente"].fillna(0).astype(int)
        
        def asignar_tramo(n):
            if n == 0:
                return "Sin reservas"
            elif n == 1:
                return "1 reserva"
            elif 2 <= n <= 3:
                return "2 a 3 reservas"
            else:
                return "4 o más"

        def asignar_orden_tramo(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            elif 2 <= n <= 3:
                return 2
            else:
                return 3

        dim_paciente["Tramo Frecuencia"] = dim_paciente["Reservas del Paciente"].apply(asignar_tramo)
        dim_paciente["Orden Tramo"] = dim_paciente["Reservas del Paciente"].apply(asignar_orden_tramo)

    # Enriquecimiento de HechoReservas con dimensiones (many-to-one)
    # DimPaciente
    if "PacienteID" in hecho_reservas.columns and "PacienteID" in dim_paciente.columns:
        n_before = len(hecho_reservas)
        cols_to_use = [c for c in dim_paciente.columns if c not in hecho_reservas.columns or c == "PacienteID"]
        hecho_reservas = hecho_reservas.merge(dim_paciente[cols_to_use], on="PacienteID", how="left", suffixes=("", "_dim"))
        assert len(hecho_reservas) == n_before, "Fan-out detectado al unir HechoReservas con DimPaciente"
        
    # DimMedico
    if "MedicoID" in hecho_reservas.columns and "MedicoID" in dim_medico.columns:
        n_before = len(hecho_reservas)
        cols_to_use = [c for c in dim_medico.columns if c not in hecho_reservas.columns or c == "MedicoID"]
        hecho_reservas = hecho_reservas.merge(dim_medico[cols_to_use], on="MedicoID", how="left", suffixes=("", "_dim"))
        assert len(hecho_reservas) == n_before, "Fan-out detectado al unir HechoReservas con DimMedico"

    # Enriquecimiento de HechoDetalle con dimensiones (many-to-one)
    if "PacienteID" in hecho_detalle.columns and "PacienteID" in dim_paciente.columns:
        n_before = len(hecho_detalle)
        cols_to_use = [c for c in dim_paciente.columns if c not in hecho_detalle.columns or c == "PacienteID"]
        hecho_detalle = hecho_detalle.merge(dim_paciente[cols_to_use], on="PacienteID", how="left", suffixes=("", "_dim"))
        assert len(hecho_detalle) == n_before, "Fan-out detectado al unir HechoDetalle con DimPaciente"

    if "MedicoID" in hecho_detalle.columns and "MedicoID" in dim_medico.columns:
        n_before = len(hecho_detalle)
        cols_to_use = [c for c in dim_medico.columns if c not in hecho_detalle.columns or c == "MedicoID"]
        hecho_detalle = hecho_detalle.merge(dim_medico[cols_to_use], on="MedicoID", how="left", suffixes=("", "_dim"))
        assert len(hecho_detalle) == n_before, "Fan-out detectado al unir HechoDetalle con DimMedico"

    if "PrestacionID" in hecho_detalle.columns and "PrestacionID" in dim_prestacion.columns:
        n_before = len(hecho_detalle)
        cols_to_use = [c for c in dim_prestacion.columns if c not in hecho_detalle.columns or c == "PrestacionID"]
        hecho_detalle = hecho_detalle.merge(dim_prestacion[cols_to_use], on="PrestacionID", how="left", suffixes=("", "_dim"))
        assert len(hecho_detalle) == n_before, "Fan-out detectado al unir HechoDetalle con DimPrestacion"

    return {
        "DimFecha": dim_fecha,
        "DimPaciente": dim_paciente,
        "DimMedico": dim_medico,
        "DimPrestacion": dim_prestacion,
        "HechoReservas": hecho_reservas,
        "HechoDetalle": hecho_detalle
    }
