"""
Exporta el modelo dimensional enriquecido (el mismo que usa el dashboard de
Streamlit) a un único JSON que consume el dashboard Astro.

Uso (desde la raíz del repositorio):
    python web/scripts/export_data.py
"""
from __future__ import annotations
import json
import logging
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
logging.disable(logging.CRITICAL)  # silencia avisos de streamlit en modo script

import pandas as pd  # noqa: E402
from app.data import prepare_data  # noqa: E402

OUT = ROOT / "web" / "src" / "data" / "dataset.json"

# Columnas necesarias por tabla (el resto del modelo no se usa en el panel)
COLUMNS = {
    "reservas": [
        "ReservaID", "FechaReserva", "PacienteID", "MedicoID", "EstadoReserva", "AtencionID",
        "Canal", "BloqueMinutos", "Comuna", "Prevision", "Sexo", "Medico", "Especialidad",
    ],
    "detalle": [
        "DetalleID", "AtencionID", "ReservaID", "FechaAtencion", "PacienteID", "MedicoID",
        "Cantidad", "ValorUnitario", "Importe", "Comuna", "Prevision", "Sexo", "Medico",
        "Especialidad", "Prestacion",
    ],
    "pacientes": [
        "PacienteID", "Comuna", "Sexo", "Reservas del Paciente", "Tramo Frecuencia", "Orden Tramo",
    ],
}


def to_records(df: pd.DataFrame, cols: list[str]) -> list[dict]:
    df = df[[c for c in cols if c in df.columns]].copy()
    for c in df.columns:
        if df[c].map(lambda v: isinstance(v, date)).any():
            df[c] = df[c].map(lambda v: v.isoformat() if isinstance(v, date) else None)
    df = df.astype(object).where(df.notna(), None)
    return json.loads(df.to_json(orient="records", force_ascii=False))


def main() -> None:
    data = prepare_data()
    if data is None:
        raise SystemExit("No se pudo cargar el modelo dimensional (data/modelo).")
    dataset = {
        "reservas": to_records(data["HechoReservas"], COLUMNS["reservas"]),
        "detalle": to_records(data["HechoDetalle"], COLUMNS["detalle"]),
        "pacientes": to_records(data["DimPaciente"], COLUMNS["pacientes"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: len(v) for k, v in dataset.items()}, "->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
