#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SaludVital BI - Construcción del modelo dimensional (ETL en Python)
====================================================================

Lee los dos libros de origen (base + adicional), aplica las reglas de
calidad documentadas en docs/documentacion_etl.md y genera el esquema en
estrella listo para Power BI.

Entradas (carpeta data/, solo lectura: nunca se modifican)
    SaludVital_BaseDatos.xlsx          hojas 01_..07_
    SaludVital_DatosAdicionales.xlsx   hojas A01_..A08_ + MAP_ESPECIALIDADES

Salidas (carpeta data/modelo/)
    DimFecha.csv  DimPaciente.csv  DimMedico.csv  DimPrestacion.csv
    HechoReservas.csv  HechoDetalle.csv
    SaludVital_ModeloDimensional.xlsx      (todo en un solo libro)
    control/*.csv                          (bitácora de calidad y controles)

Modelo (todas las relaciones 1:N, dimensión -> hecho, filtro en un sentido)
    DimFecha[Date]          -> HechoReservas[FechaReserva] | HechoDetalle[FechaAtencion]
    DimPaciente[PacienteID] -> HechoReservas[PacienteID]   | HechoDetalle[PacienteID]
    DimMedico[MedicoID]     -> HechoReservas[MedicoID]     | HechoDetalle[MedicoID]
    DimPrestacion[PrestacionID] -> HechoDetalle[PrestacionID]

Decisiones de diseño (ver sección "Modelo dimensional" de la documentación)
    - Dos hechos porque tienen granos distintos (reserva vs. prestación).
    - Sin DimEspecialidad: la especialidad se pliega como atributo en
      DimMedico y DimPrestacion.  Sin DimEstado ni DimCanal: son columnas.
    - Claves naturales (IDs de negocio).  Sin nombre ni fecha de nacimiento
      del paciente en el modelo (privacidad).
    - Cada fila termina en: aceptada | duplicado exacto descartado | rechazo
      con origen y motivo.  Gana la primera ocurrencia (base antes que
      adicional) => el proceso es idempotente.

Uso
    python scripts/modelo_dimensional.py
    python scripts/modelo_dimensional.py --out data/modelo --sin-excel
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------------
# 1. CONFIGURACIÓN
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]          # raíz del repositorio
DATA_DIR = ROOT / "data"
OUT_DIR = DATA_DIR / "modelo"

ARCHIVO_BASE = ["SaludVital_BaseDatos.xlsx"]
ARCHIVO_ADIC = ["SaludVital_DatosAdicionales.xlsx",
                "SaludVital_DatosAdicionales_ETL.xlsx"]   # nombre alternativo

# Cobertura temporal (LEEME del ejercicio: hipótesis de simulación)
FECHA_INI = date(2026, 1, 5)
FECHA_FIN = date(2026, 3, 31)
BASE_FIN = date(2026, 2, 3)          # el período base termina el 03-feb

# Columnas de negocio por entidad (se descartan columnas vacías / residuales)
COLS = {
    "pacientes":      ["PacienteID", "Nombre", "Comuna", "FechaNacimiento", "Prevision", "Sexo"],
    "medicos":        ["MedicoID", "Medico", "EspecialidadID"],
    "especialidades": ["EspecialidadID", "Especialidad"],
    "prestaciones":   ["PrestacionID", "Prestacion", "EspecialidadID", "Valor"],
    "reservas":       ["ReservaID", "FechaReserva", "HoraReserva", "PacienteID", "MedicoID", "EstadoReserva"],
    "atenciones":     ["AtencionID", "ReservaID", "FechaAtencion", "Diagnostico", "Observacion"],
    "detalle":        ["DetalleID", "AtencionID", "PrestacionID", "Cantidad", "ValorUnitario"],
    "canales":        ["ReservaID", "CanalReserva", "BloqueMinutos", "FechaCarga", "MarcaFuente"],
    "map_esp":        ["EspecialidadID", "EtiquetaFuente", "FuenteSistema", "Observacion"],
}
HOJAS_BASE = {"pacientes": "01_PACIENTES", "medicos": "02_MEDICOS", "prestaciones": "04_PRESTACIONES",
              "reservas": "05_RESERVAS", "atenciones": "06_ATENCIONES", "detalle": "07_DETALLE_ATENCION"}
# 03_ESPECIALIDADES de la base es una copia de 02_MEDICOS: se ignora (RN01)
HOJAS_ADIC = {"pacientes": "A01_PACIENTES", "medicos": "A02_MEDICOS", "especialidades": "A03_ESPECIALIDADES",
              "prestaciones": "A04_PRESTACIONES", "reservas": "A05_RESERVAS", "atenciones": "A06_ATENCIONES",
              "detalle": "A07_DETALLE_ATENCION", "canales": "A08_CANALES_BLOQUES",
              "map_esp": "MAP_ESPECIALIDADES"}

# Nombres canónicos E01-E10: PROPUESTA POR APROBAR (la base no los trae; se
# respaldan en MAP_ESPECIALIDADES).  E11 y E12 salen de A03_ESPECIALIDADES.
CANON_ESP = {"E01": "Medicina General", "E02": "Pediatría", "E03": "Traumatología",
             "E04": "Ginecología", "E05": "Cardiología", "E06": "Dermatología",
             "E07": "Neurología", "E08": "Oftalmología", "E09": "Endocrinología",
             "E10": "Kinesiología"}
ALIAS_ESP = {"trauma": "E03"}        # alias respaldado en MAP_ESPECIALIDADES

# Catálogos acordados (clave = texto normalizado sin tildes/mayúsculas/espacios)
ESTADOS = {"atendida": "Atendida", "no asistio": "No asistió",
           "cancelada": "Cancelada", "pendiente": "Pendiente"}
CANALES = {"recepcion": "Recepción", "telefono": "Teléfono",
           "sitio web": "Sitio web", "aplicacion movil": "Aplicación móvil"}
CANAL_SIN_RESOLVER = "Sin resolver"      # etiqueta sin respaldo (WEB, Kiosco)
CANAL_NO_REGISTRADO = "No registrado"    # reserva sin fila de canal aceptada

PATRONES = {  # contratos de ID (DICCIONARIO)
    "paciente": re.compile(r"^P\d{3}$"), "medico": re.compile(r"^M\d{3}$"),
    "especialidad": re.compile(r"^E\d{2}$"), "prestacion": re.compile(r"^PR\d{3}$"),
    "reserva": re.compile(r"^R\d{4}$"), "atencion": re.compile(r"^A\d{4}$"),
    "detalle": re.compile(r"^DA\d{3,4}$"),
}
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
         "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Valores publicados en la documentación (para verificar la reproducción)
ESPERADO = {
    "DimPaciente (filas)": 44, "DimMedico (filas)": 14, "DimPrestacion (filas)": 19,
    "HechoReservas (filas)": 75, "HechoDetalle (filas)": 41, "DimFecha (filas)": 86,
    "Estado Atendida": 48, "Estado No asistió": 12, "Estado Cancelada": 10,
    "Estado Pendiente": 5, "Suma Importe (CLP)": 1_671_000,
    "Rechazos (total)": 34, "Duplicados descartados (total)": 4,
}


# ----------------------------------------------------------------------------
# 2. UTILIDADES DE LIMPIEZA Y PARSEO
# ----------------------------------------------------------------------------
def es_nulo(v) -> bool:
    if v is None:
        return True
    try:
        r = pd.isna(v)
    except (TypeError, ValueError):
        return False
    return bool(r) if not hasattr(r, "__len__") else False


def txt(v):
    """Recorta espacios; el texto vacío pasa a nulo."""
    if es_nulo(v):
        return None
    s = str(v).strip()
    return s or None


def norm(v):
    """Clave de comparación: sin tildes, minúsculas, espacios colapsados."""
    s = txt(v)
    if s is None:
        return None
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def parse_fecha(v):
    """Acepta fecha nativa, ISO (yyyy-mm-dd) y yyyy/mm/dd.  Sin adivinar otros formatos."""
    if es_nulo(v):
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_hora(v):
    if es_nulo(v):
        return None
    if isinstance(v, datetime):
        return v.time().replace(microsecond=0)
    if isinstance(v, time):
        return v.replace(microsecond=0)
    s = str(v).strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            pass
    return None


def parse_num(v):
    """Número o texto numérico ('47000' -> 47000).  Nulo si no es parseable."""
    if es_nulo(v) or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        x = float(v)
    else:
        try:
            x = float(str(v).strip())
        except ValueError:
            return None
    return int(x) if x.is_integer() else x


def mostrar(v) -> str:
    if es_nulo(v):
        return ""
    if isinstance(v, str) and v != v.strip():
        return f"[{v}]"                     # deja visibles los espacios sobrantes
    if isinstance(v, (datetime, pd.Timestamp)):
        return v.strftime("%Y-%m-%d")
    return str(v)


# ----------------------------------------------------------------------------
# 3. BITÁCORA, LECTURA Y REGLAS GENÉRICAS
# ----------------------------------------------------------------------------
class Bitacora:
    """Registra rechazos y duplicados (Fuente, Clave, Campo, Regla, ValorRaw, Motivo)."""

    def __init__(self):
        self.rechazos, self.duplicados = [], []

    def rechazar(self, rec, clave, campo, regla, valor, motivo):
        k = txt(rec.get(clave))
        self.rechazos.append({
            "Fuente": rec["Hoja"], "Clave": k if k else f"fila {rec['Fila_origen']}",
            "Campo": campo, "Regla": regla, "ValorRaw": mostrar(valor),
            "Motivo": motivo, "Fila_origen": rec["Fila_origen"]})

    def duplicado(self, rec, clave, primera_fila):
        self.duplicados.append({
            "Fuente": rec["Hoja"], "Clave": txt(rec.get(clave)) or f"fila {rec['Fila_origen']}",
            "Fila_origen": rec["Fila_origen"], "Duplicado_de_fila": primera_fila})


def leer_hoja(xlsx: Path, hoja: str, columnas: list[str], origen: str):
    """Lee una hoja conservando valores crudos.  Descarta columnas no listadas
    (vacías/residuales) y filas totalmente vacías."""
    df = pd.read_excel(xlsx, sheet_name=hoja, dtype=object)
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        raise KeyError(f"{xlsx.name}:{hoja} no tiene las columnas {faltan}")
    df.insert(0, "Fila_origen", df.index + 2)          # nº de fila en Excel
    df = df[["Fila_origen"] + columnas].copy()
    if df.empty:
        vacias = pd.Series([], dtype=bool)
    else:
        vacias = df[columnas].apply(lambda r: all(txt(x) is None for x in r), axis=1)
    df = df[~vacias].copy()
    df["Hoja"], df["Origen"] = hoja, origen
    return df.reset_index(drop=True), int(vacias.sum())


def quitar_duplicados_exactos(df, columnas, clave, bit=None):
    """Table.Distinct: conserva la primera ocurrencia de filas idénticas en todos los campos."""
    vistos, mantener, ids = {}, [], []
    for rec in df.to_dict("records"):
        firma = tuple(repr(rec[c]) for c in columnas)
        if firma in vistos:
            ids.append(txt(rec[clave]) or f"fila {rec['Fila_origen']}")
            if bit is not None:
                bit.duplicado(rec, clave, vistos[firma])
        else:
            vistos[firma] = rec["Fila_origen"]
            mantener.append(rec)
    return pd.DataFrame(mantener, columns=df.columns), ids


def rechazar_clave_repetida(df, clave, bit, regla="RV-CLAVE-REPETIDA"):
    """Misma clave con contenido distinto: gana la primera, el resto va a cuarentena."""
    vistas, ok = set(), []
    for rec in df.to_dict("records"):
        k = txt(rec[clave])
        if k is not None and k in vistas:
            bit.rechazar(rec, clave, clave, regla, rec[clave],
                         f"{clave} repetida con contenido distinto; se conserva la primera ocurrencia")
        else:
            if k is not None:
                vistas.add(k)
            ok.append(rec)
    return pd.DataFrame(ok, columns=df.columns)


def aplicar_reglas(df, reglas, clave, bit):
    """Cada fila falla en la PRIMERA regla incumplida (una fila = un rechazo)."""
    aceptadas = []
    for rec in df.to_dict("records"):
        for regla, fn in reglas:
            res = fn(rec)
            if res:
                campo, valor, motivo = res
                bit.rechazar(rec, clave, campo, regla, valor, motivo)
                break
        else:
            aceptadas.append(rec)
    return pd.DataFrame(aceptadas, columns=df.columns)


# --- fábricas de reglas: devuelven (id_regla, función(rec) -> (campo, valor, motivo) | None)
def r_patron(campo, clave_patron, regla="RV-ID-PATRON"):
    pat = PATRONES[clave_patron]

    def f(rec):
        v = txt(rec[campo])
        if v is None:
            return campo, rec[campo], f"{campo} nulo"
        if not pat.match(v):
            return campo, rec[campo], f"{campo} no cumple el patrón {pat.pattern}"
    return regla, f


def r_obligatorios(campos, regla="RV-OBLIGATORIO"):
    def f(rec):
        falta = [c for c in campos if txt(rec[c]) is None]
        if falta:
            return ", ".join(falta), None, f"Campos obligatorios nulos: {', '.join(falta)}"
    return regla, f


def r_fk(campo, validos, destino, regla="RV-FK"):
    def f(rec):
        v = txt(rec[campo])
        if v is None:
            return campo, rec[campo], f"{campo} nulo: FK obligatoria"
        if v not in validos:
            return campo, rec[campo], f"{campo}={v} no existe en {destino}"
    return regla, f


def r_parseable(campo, parser, tipo, regla):
    def f(rec):
        if txt(rec[campo]) is not None and parser(rec[campo]) is None:
            return campo, rec[campo], f"{campo} no parseable como {tipo}"
    return regla, f


def r_positivo(campo, etiqueta, regla):
    def f(rec):
        n = parse_num(rec[campo])
        if n is None:
            return campo, rec[campo], f"{campo} nulo o no numérico ({etiqueta})"
        if n <= 0:
            return campo, rec[campo], f"{campo} debe ser mayor que cero"
    return regla, f


def r_catalogo(campo, catalogo, nombre, regla):
    def f(rec):
        v = norm(rec[campo])
        if v is None:
            return campo, rec[campo], f"{campo} nulo"
        if v not in catalogo:
            return campo, rec[campo], f"{campo} fuera del catálogo acordado de {nombre} (no se interpreta)"
    return regla, f


def r_estado_reserva_atendida(estados_por_reserva, regla="RV-ATENCION-SOLO-ATENDIDA"):
    def f(rec):
        e = estados_por_reserva.get(txt(rec["ReservaID"]))
        if e != "Atendida":
            return "ReservaID", rec["ReservaID"], f"La reserva está en estado {e}; solo las Atendidas generan atención"
    return regla, f


def unir_n_a_1(izq, der, on, nombre, ctrl):
    """Equivalente a fn_unir: falla si la clave del lado derecho se repite (sin fan-out)."""
    if der[on].duplicated().any():
        raise ValueError(f"[{nombre}] la clave derecha '{on}' no es única: la combinación duplicaría filas")
    antes = len(izq)
    out = izq.merge(der, on=on, how="left", validate="many_to_one")
    ctrl.append({"Combinacion": nombre, "Antes": antes, "Despues": len(out), "Sin_fan_out": antes == len(out)})
    return out


# ----------------------------------------------------------------------------
# 4. CONSTRUCCIÓN DEL MODELO
# ----------------------------------------------------------------------------
@dataclass
class Resultado:
    tablas: dict
    controles: dict


def _resolver_mapeo_especialidades(map_df):
    filas = []
    for rec in map_df.to_dict("records"):
        eid, etiqueta = txt(rec["EspecialidadID"]), txt(rec["EtiquetaFuente"])
        canon, motivo = None, ""
        if eid is None:
            motivo = "ID faltante"
        elif eid not in CANON_ESP:
            motivo = f"{eid} no existe en maestros"
        elif norm(etiqueta) == norm(CANON_ESP[eid]):
            canon = CANON_ESP[eid]
        elif ALIAS_ESP.get(norm(etiqueta)) == eid:
            canon, motivo = CANON_ESP[eid], "Resuelta por alias respaldado en MAP"
        else:
            motivo = "Etiqueta sin equivalencia evidente"
        filas.append({"Entidad": "Especialidad", "EtiquetaRaw": mostrar(rec["EtiquetaFuente"]),
                      "EspecialidadID": eid, "Canonica": canon, "Resuelta": canon is not None, "Motivo": motivo})
    return pd.DataFrame(filas)


def construir_modelo(base_xlsx: Path, adic_xlsx: Path) -> Resultado:
    bit = Bitacora()
    ctrl_fuentes, ctrl_dim, ctrl_card, ctrl_carga, ctrl_merge = [], [], [], [], []

    def leer(ent, hoja, xlsx, origen):
        df, vac = leer_hoja(xlsx, hoja, COLS[ent], origen)
        ctrl_fuentes.append({"Fuente": hoja, "Archivo": xlsx.name,
                             "Filas_leidas": len(df), "Filas_vacias_omitidas": vac})
        return df

    def cardinalidad(lado, nombre, df, clave):
        n = df[clave].map(txt).nunique()
        ctrl_card.append({"Lado": lado, "Tabla": nombre, "Filas": len(df),
                          "Claves_distintas": n, "Clave_unica": len(df) == n})

    # ---------------- 4.1 Especialidades (RN01/RN02) ----------------
    map_df = leer("map_esp", HOJAS_ADIC["map_esp"], adic_xlsx, "Adicional")
    mapeo_esp = _resolver_mapeo_especialidades(map_df)
    ids_resueltos = set(mapeo_esp.loc[mapeo_esp.Resuelta, "EspecialidadID"])
    esp_base = pd.DataFrame([{"Fila_origen": 0, "EspecialidadID": i, "Especialidad": n,
                              "Hoja": "MAP_ESPECIALIDADES", "Origen": "Base", "Es_nueva_alta": False}
                             for i, n in CANON_ESP.items() if i in ids_resueltos])
    esp_adic = leer("especialidades", HOJAS_ADIC["especialidades"], adic_xlsx, "Adicional")
    esp_adic["Es_nueva_alta"] = True
    esp_adic["EspecialidadID"] = esp_adic["EspecialidadID"].map(txt)
    esp_adic["Especialidad"] = esp_adic["Especialidad"].map(txt)
    esp = pd.concat([esp_base, esp_adic], ignore_index=True)
    antes = len(esp)
    esp, dup_ids = quitar_duplicados_exactos(esp, ["EspecialidadID", "Especialidad"], "EspecialidadID")
    ctrl_dim.append({"Dimension": "Especialidades", "Filas_antes": antes, "Filas_despues": len(esp),
                     "Descartadas": len(dup_ids), "Duplicado_exacto_descartado": ", ".join(dup_ids),
                     "Clave_unica_OK": esp.EspecialidadID.is_unique})
    cardinalidad("Dimension", "Especialidades", esp, "EspecialidadID")
    nombre_esp = dict(zip(esp.EspecialidadID, esp.Especialidad))

    # ---------------- 4.2 Dimensiones: anexar base + adicional ----------------
    def anexar(ent, nombre, clave):
        df = pd.concat([leer(ent, HOJAS_BASE[ent], base_xlsx, "Base"),
                        leer(ent, HOJAS_ADIC[ent], adic_xlsx, "Adicional")], ignore_index=True)
        antes = len(df)
        df, dups = quitar_duplicados_exactos(df, COLS[ent], clave)
        ctrl_dim.append({"Dimension": nombre, "Filas_antes": antes, "Filas_despues": len(df),
                         "Descartadas": len(dups), "Duplicado_exacto_descartado": ", ".join(dups),
                         "Clave_unica_OK": df[clave].map(txt).is_unique})
        cardinalidad("Dimension", nombre, df, clave)
        return df

    pac_stg = anexar("pacientes", "Pacientes", "PacienteID")
    med_stg = anexar("medicos", "Médicos", "MedicoID")
    pre_stg = anexar("prestaciones", "Prestaciones", "PrestacionID")

    # ---------------- 4.3 Cuarentena de dimensiones ----------------
    pac = aplicar_reglas(pac_stg, [
        r_patron("PacienteID", "paciente"),
        r_obligatorios(["Nombre", "Comuna", "FechaNacimiento", "Prevision", "Sexo"]),
        r_parseable("FechaNacimiento", parse_fecha, "fecha", "RV-FECHA"),
    ], "PacienteID", bit)
    med = aplicar_reglas(med_stg, [
        r_patron("MedicoID", "medico"),
        r_obligatorios(["Medico"]),
        r_fk("EspecialidadID", set(nombre_esp), "especialidades"),
    ], "MedicoID", bit)
    pre = aplicar_reglas(pre_stg, [
        r_patron("PrestacionID", "prestacion"),
        r_obligatorios(["Prestacion"]),
        r_fk("EspecialidadID", set(nombre_esp), "especialidades"),
        r_positivo("Valor", "tarifa ausente: no se imputa", "RV-TARIFA"),
    ], "PrestacionID", bit)

    def carga(nombre, entrada, ok, clave, dups=0, rech=None):
        rech = (entrada - len(ok) - dups) if rech is None else rech
        ctrl_carga.append({"Tabla": nombre, "Entrada": entrada, "Aceptadas": len(ok), "Duplicados": dups,
                           "Rechazadas": rech, "Cuadra": entrada == len(ok) + dups + rech,
                           "Claves_unicas_en_aceptadas": ok[clave].map(txt).is_unique})

    carga("Pacientes", len(pac_stg), pac, "PacienteID")
    carga("Médicos", len(med_stg), med, "MedicoID")
    carga("Prestaciones", len(pre_stg), pre, "PrestacionID")

    dim_paciente = pd.DataFrame({
        "PacienteID": pac.PacienteID.map(txt), "Comuna": pac.Comuna.map(txt),
        "Prevision": pac.Prevision.map(txt), "Sexo": pac.Sexo.map(txt), "Origen": pac.Origen,
    }).sort_values("PacienteID").reset_index(drop=True)
    dim_medico = pd.DataFrame({
        "MedicoID": med.MedicoID.map(txt), "Medico": med.Medico.map(txt),
        "EspecialidadID": med.EspecialidadID.map(txt),
        "Especialidad": med.EspecialidadID.map(lambda x: nombre_esp[txt(x)]), "Origen": med.Origen,
    }).sort_values("MedicoID").reset_index(drop=True)
    dim_prestacion = pd.DataFrame({
        "PrestacionID": pre.PrestacionID.map(txt), "Prestacion": pre.Prestacion.map(txt),
        "EspecialidadID": pre.EspecialidadID.map(txt),
        "Especialidad": pre.EspecialidadID.map(lambda x: nombre_esp[txt(x)]),
        "Tarifa_maestra": pre.Valor.map(parse_num), "Origen": pre.Origen,
    }).sort_values("PrestacionID").reset_index(drop=True)

    # ---------------- 4.4 Hechos: reservas ----------------
    def anexar_hecho(ent):
        partes = [leer(ent, HOJAS_BASE[ent], base_xlsx, "Base")] if ent in HOJAS_BASE else []
        partes.append(leer(ent, HOJAS_ADIC[ent], adic_xlsx, "Adicional"))
        return pd.concat(partes, ignore_index=True)

    res_raw = anexar_hecho("reservas")
    ate_raw = anexar_hecho("atenciones")
    det_raw = anexar_hecho("detalle")
    can_raw = anexar_hecho("canales")
    for nom, df, k in [("Reservas", res_raw, "ReservaID"), ("Atenciones", ate_raw, "AtencionID"),
                       ("Detalle", det_raw, "DetalleID"), ("Canales", can_raw, "ReservaID")]:
        cardinalidad("Hecho", nom, df, k)

    # 4.4.a reservas
    n_res = len(res_raw)
    res_u, d = quitar_duplicados_exactos(res_raw, COLS["reservas"], "ReservaID", bit)
    res_ok = aplicar_reglas(res_u, [
        r_patron("ReservaID", "reserva"),
        r_parseable("FechaReserva", parse_fecha, "fecha (ISO o yyyy/mm/dd)", "RV-FECHA"),
        r_obligatorios(["FechaReserva", "HoraReserva"]),
        r_parseable("HoraReserva", parse_hora, "hora (HH:MM)", "RV-HORA"),
        r_fk("PacienteID", set(dim_paciente.PacienteID), "DimPaciente"),
        r_fk("MedicoID", set(dim_medico.MedicoID), "DimMedico"),
        r_catalogo("EstadoReserva", ESTADOS, "estados", "RV-ESTADO"),
    ], "ReservaID", bit)
    carga("Reservas", n_res, res_ok, "ReservaID", dups=len(d))
    estado_por_reserva = {txt(r): ESTADOS[norm(e)] for r, e in zip(res_ok.ReservaID, res_ok.EstadoReserva)}

    # 4.4.b canales / bloques
    n_can = len(can_raw)
    can_u, d = quitar_duplicados_exactos(can_raw, COLS["canales"], "ReservaID", bit)
    can_u = rechazar_clave_repetida(can_u, "ReservaID", bit)
    can_ok = aplicar_reglas(can_u, [
        r_patron("ReservaID", "reserva"),
        r_positivo("BloqueMinutos", "bloque obligatorio", "RV-BLOQUE"),
        r_fk("ReservaID", set(estado_por_reserva), "reservas aceptadas"),
        r_obligatorios(["CanalReserva"]),
    ], "ReservaID", bit)
    carga("Canales/bloques", n_can, can_ok, "ReservaID", dups=len(d))

    # 4.4.c atenciones
    n_ate = len(ate_raw)
    ate_u, d = quitar_duplicados_exactos(ate_raw, COLS["atenciones"], "AtencionID", bit)
    ate_u = rechazar_clave_repetida(ate_u, "AtencionID", bit)
    ate_ok = aplicar_reglas(ate_u, [
        r_patron("AtencionID", "atencion"),
        r_fk("ReservaID", set(estado_por_reserva), "reservas aceptadas"),
        r_estado_reserva_atendida(estado_por_reserva),
        r_obligatorios(["FechaAtencion"]),
        r_parseable("FechaAtencion", parse_fecha, "fecha", "RV-FECHA"),
    ], "AtencionID", bit)
    ate_ok = rechazar_clave_repetida(ate_ok, "ReservaID", bit, regla="RV-UNA-ATENCION-POR-RESERVA")
    carga("Atenciones", n_ate, ate_ok, "AtencionID", dups=len(d))

    # 4.4.d detalle de atención
    n_det = len(det_raw)
    det_u, d = quitar_duplicados_exactos(det_raw, COLS["detalle"], "DetalleID", bit)
    det_u = rechazar_clave_repetida(det_u, "DetalleID", bit)
    det_ok = aplicar_reglas(det_u, [
        r_patron("DetalleID", "detalle"),
        r_fk("AtencionID", set(ate_ok.AtencionID.map(txt)), "atenciones aceptadas"),
        r_fk("PrestacionID", set(dim_prestacion.PrestacionID), "DimPrestacion"),
        r_positivo("Cantidad", "cantidad", "RV-CANTIDAD"),
        r_positivo("ValorUnitario", "valor ausente: no se imputa", "RV-VALOR"),
    ], "DetalleID", bit)
    carga("Detalle", n_det, det_ok, "DetalleID", dups=len(d))

    # ---------------- 4.5 Etiquetas: mapeo y no resueltos ----------------
    def mapeo(entidad, serie, catalogo, sin_resolver):
        filas = []
        for raw, n in serie.map(mostrar).value_counts(sort=False).items():
            canon = catalogo.get(norm(raw.strip("[]")))
            filas.append({"Entidad": entidad, "EtiquetaRaw": raw, "Filas": int(n),
                          "EspecialidadID": None, "Canonica": canon, "Resuelta": canon is not None,
                          "Motivo": "" if canon else sin_resolver})
        return filas

    cols_map = ["Entidad", "EtiquetaRaw", "Filas", "EspecialidadID", "Canonica", "Resuelta", "Motivo"]
    mapeo_etq = pd.concat([
        mapeo_esp.assign(Filas=1)[cols_map],
        pd.DataFrame(mapeo("Estado", res_raw.EstadoReserva.dropna(), ESTADOS, "Fuera de catálogo: no se interpreta")),
        pd.DataFrame(mapeo("Canal", can_raw.CanalReserva.dropna(), CANALES, "Sin catálogo que la respalde")),
    ], ignore_index=True).sort_values(["Entidad", "EtiquetaRaw"]).reset_index(drop=True)
    no_resueltos = mapeo_etq[~mapeo_etq.Resuelta].reset_index(drop=True)

    # ---------------- 4.6 Tablas de hechos (sin fan-out) ----------------
    can_t = pd.DataFrame({
        "ReservaID": can_ok.ReservaID.map(txt),
        "Canal_raw": can_ok.CanalReserva.map(lambda x: str(x)),
        "Canal": can_ok.CanalReserva.map(lambda x: CANALES.get(norm(x), CANAL_SIN_RESOLVER)),
        "BloqueMinutos": can_ok.BloqueMinutos.map(parse_num)})
    ate_t = pd.DataFrame({"ReservaID": ate_ok.ReservaID.map(txt), "AtencionID": ate_ok.AtencionID.map(txt),
                          "FechaAtencion": ate_ok.FechaAtencion.map(parse_fecha)})
    hr = pd.DataFrame({
        "ReservaID": res_ok.ReservaID.map(txt),
        "FechaReserva": res_ok.FechaReserva.map(parse_fecha),
        "HoraReserva": res_ok.HoraReserva.map(parse_hora),
        "PacienteID": res_ok.PacienteID.map(txt), "MedicoID": res_ok.MedicoID.map(txt),
        "EstadoReserva": res_ok.EstadoReserva.map(lambda x: ESTADOS[norm(x)]),
        "EstadoReserva_raw": res_ok.EstadoReserva.map(lambda x: str(x)),
        "Origen": res_ok.Origen})
    hr = unir_n_a_1(hr, ate_t[["ReservaID", "AtencionID"]], "ReservaID", "Reservas + atención (N:1)", ctrl_merge)
    hr = unir_n_a_1(hr, can_t, "ReservaID", "Reservas + canal/bloque (N:1)", ctrl_merge)
    hr["Canal"] = hr["Canal"].fillna(CANAL_NO_REGISTRADO)
    hr["HoraDia"] = hr.HoraReserva.map(lambda t: t.hour)
    hr["BloqueMinutos"] = pd.array([None if es_nulo(x) else int(x) for x in hr["BloqueMinutos"]], dtype="Int64")
    hecho_reservas = hr[["ReservaID", "FechaReserva", "HoraReserva", "HoraDia", "PacienteID", "MedicoID",
                         "EstadoReserva", "EstadoReserva_raw", "AtencionID", "Canal", "Canal_raw",
                         "BloqueMinutos", "Origen"]].sort_values("ReservaID").reset_index(drop=True)

    hd = pd.DataFrame({
        "DetalleID": det_ok.DetalleID.map(txt), "AtencionID": det_ok.AtencionID.map(txt),
        "PrestacionID": det_ok.PrestacionID.map(txt), "Cantidad": det_ok.Cantidad.map(parse_num),
        "ValorUnitario": det_ok.ValorUnitario.map(parse_num), "Origen": det_ok.Origen})
    hd = unir_n_a_1(hd, ate_t[["AtencionID", "ReservaID", "FechaAtencion"]], "AtencionID",
                    "Detalle + atención (N:1)", ctrl_merge)
    hd = unir_n_a_1(hd, hecho_reservas[["ReservaID", "PacienteID", "MedicoID"]], "ReservaID",
                    "Detalle + reserva (N:1)", ctrl_merge)
    hd["Importe"] = hd.Cantidad * hd.ValorUnitario            # valorizado, no cobrado
    hecho_detalle = hd[["DetalleID", "AtencionID", "ReservaID", "FechaAtencion", "PacienteID", "MedicoID",
                        "PrestacionID", "Cantidad", "ValorUnitario", "Importe", "Origen"]
                       ].sort_values("DetalleID").reset_index(drop=True)

    # ---------------- 4.7 DimFecha ----------------
    f_min = min([FECHA_INI, hecho_reservas.FechaReserva.min(), hecho_detalle.FechaAtencion.min()])
    f_max = max([FECHA_FIN, hecho_reservas.FechaReserva.max(), hecho_detalle.FechaAtencion.max()])
    filas, d0 = [], f_min
    while d0 <= f_max:
        filas.append({"Date": d0, "Anio": d0.year, "Mes": d0.month, "NombreMes": MESES[d0.month - 1],
                      "AnioMes": d0.strftime("%Y-%m"), "Trimestre": f"T{(d0.month - 1) // 3 + 1}",
                      "SemanaISO": d0.isocalendar()[1], "DiaSemana": d0.isoweekday(),
                      "NombreDia": DIAS[d0.weekday()], "EsFinDeSemana": int(d0.weekday() >= 5),
                      "Periodo": "Base" if d0 <= BASE_FIN else "Adicional"})
        d0 += timedelta(days=1)
    dim_fecha = pd.DataFrame(filas)

    # ---------------- 4.8 Controles ----------------
    def huerfanos(hecho, col, dim, dcol):
        return int((~hecho[col].isin(dim[dcol])).sum())

    con_atencion = hecho_reservas.dropna(subset=["AtencionID"])
    integridad = pd.DataFrame([
        {"Relacion": "HechoReservas.FechaReserva -> DimFecha", "Huerfanos": huerfanos(hecho_reservas, "FechaReserva", dim_fecha, "Date")},
        {"Relacion": "HechoReservas.PacienteID -> DimPaciente", "Huerfanos": huerfanos(hecho_reservas, "PacienteID", dim_paciente, "PacienteID")},
        {"Relacion": "HechoReservas.MedicoID -> DimMedico", "Huerfanos": huerfanos(hecho_reservas, "MedicoID", dim_medico, "MedicoID")},
        {"Relacion": "HechoDetalle.FechaAtencion -> DimFecha", "Huerfanos": huerfanos(hecho_detalle, "FechaAtencion", dim_fecha, "Date")},
        {"Relacion": "HechoDetalle.PacienteID -> DimPaciente", "Huerfanos": huerfanos(hecho_detalle, "PacienteID", dim_paciente, "PacienteID")},
        {"Relacion": "HechoDetalle.MedicoID -> DimMedico", "Huerfanos": huerfanos(hecho_detalle, "MedicoID", dim_medico, "MedicoID")},
        {"Relacion": "HechoDetalle.PrestacionID -> DimPrestacion", "Huerfanos": huerfanos(hecho_detalle, "PrestacionID", dim_prestacion, "PrestacionID")},
        {"Relacion": "HechoDetalle.AtencionID -> HechoReservas.AtencionID", "Huerfanos": huerfanos(hecho_detalle, "AtencionID", con_atencion, "AtencionID")},
    ])
    integridad["OK"] = integridad.Huerfanos == 0

    sin_atencion = hecho_reservas[(hecho_reservas.EstadoReserva == "Atendida") & hecho_reservas.AtencionID.isna()][
        ["ReservaID", "FechaReserva", "MedicoID", "PacienteID"]].reset_index(drop=True)

    rechazos = pd.DataFrame(bit.rechazos, columns=["Fuente", "Clave", "Campo", "Regla", "ValorRaw", "Motivo", "Fila_origen"])
    duplicados = pd.DataFrame(bit.duplicados, columns=["Fuente", "Clave", "Fila_origen", "Duplicado_de_fila"])
    estados = hecho_reservas.EstadoReserva.value_counts()
    obtenido = {
        "DimPaciente (filas)": len(dim_paciente), "DimMedico (filas)": len(dim_medico),
        "DimPrestacion (filas)": len(dim_prestacion), "HechoReservas (filas)": len(hecho_reservas),
        "HechoDetalle (filas)": len(hecho_detalle), "DimFecha (filas)": len(dim_fecha),
        **{f"Estado {e}": int(estados.get(e, 0)) for e in ["Atendida", "No asistió", "Cancelada", "Pendiente"]},
        "Suma Importe (CLP)": int(hecho_detalle.Importe.sum()),
        "Rechazos (total)": len(rechazos), "Duplicados descartados (total)": len(duplicados)}
    verificacion = pd.DataFrame([{"Indicador": k, "Esperado_documentacion": v, "Obtenido": obtenido[k],
                                  "OK": v == obtenido[k]} for k, v in ESPERADO.items()])

    tablas = {"DimFecha": dim_fecha, "DimPaciente": dim_paciente, "DimMedico": dim_medico,
              "DimPrestacion": dim_prestacion, "HechoReservas": hecho_reservas, "HechoDetalle": hecho_detalle}
    controles = {"control_fuentes": pd.DataFrame(ctrl_fuentes), "control_dim": pd.DataFrame(ctrl_dim),
                 "control_cardinalidad": pd.DataFrame(ctrl_card), "control_merge": pd.DataFrame(ctrl_merge),
                 "control_carga": pd.DataFrame(ctrl_carga), "control_integridad": integridad,
                 "rechazos": rechazos, "duplicados_descartados": duplicados,
                 "mapeo_etiquetas": mapeo_etq, "no_resueltos": no_resueltos,
                 "reservas_atendidas_sin_atencion": sin_atencion, "verificacion_documentada": verificacion}
    return Resultado(tablas, controles)


# ----------------------------------------------------------------------------
# 5. IDEMPOTENCIA, SALIDA Y CLI
# ----------------------------------------------------------------------------
def huella(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df.astype(str), index=False).values.tobytes()).hexdigest()[:16]


def prueba_idempotencia(r1: Resultado, r2: Resultado) -> pd.DataFrame:
    filas = []
    for nombre, df in r1.tablas.items():
        otro = r2.tablas[nombre]
        filas.append({"Tabla": nombre, "Filas_corrida_1": len(df), "Filas_corrida_2": len(otro),
                      "Mismo_conteo": len(df) == len(otro), "Mismas_filas": huella(df) == huella(otro)})
    return pd.DataFrame(filas)


def resolver_archivo(carpeta: Path, candidatos: list[str]) -> Path:
    for c in candidatos:
        if (carpeta / c).exists():
            return carpeta / c
    raise FileNotFoundError(f"No se encontró ninguno de {candidatos} en {carpeta}")


def exportar(res: Resultado, out: Path, con_excel: bool):
    (out / "control").mkdir(parents=True, exist_ok=True)
    for n, df in res.tablas.items():
        df.to_csv(out / f"{n}.csv", index=False, encoding="utf-8-sig")
    for n, df in res.controles.items():
        df.to_csv(out / "control" / f"{n}.csv", index=False, encoding="utf-8-sig")
    if con_excel:
        with pd.ExcelWriter(out / "SaludVital_ModeloDimensional.xlsx", engine="openpyxl") as xw:
            for n, df in {**res.tablas, **res.controles}.items():
                df.to_excel(xw, sheet_name=n[:31], index=False)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Construye el modelo dimensional de SaludVital.")
    ap.add_argument("--data", type=Path, default=DATA_DIR, help="carpeta con los Excel de origen")
    ap.add_argument("--out", type=Path, default=OUT_DIR, help="carpeta de salida")
    ap.add_argument("--sin-excel", action="store_true", help="no generar el libro .xlsx consolidado")
    a = ap.parse_args()

    base = resolver_archivo(a.data, ARCHIVO_BASE)
    adic = resolver_archivo(a.data, ARCHIVO_ADIC)
    print(f"Base      : {base}\nAdicional : {adic}\nSalida    : {a.out}\n")

    r1 = construir_modelo(base, adic)
    r2 = construir_modelo(base, adic)                       # segunda corrida => idempotencia
    r1.controles["prueba_idempotencia"] = prueba_idempotencia(r1, r2)
    exportar(r1, a.out, not a.sin_excel)

    pd.set_option("display.width", 200, "display.max_columns", 20)
    for t in ("control_carga", "control_merge", "control_integridad", "prueba_idempotencia", "verificacion_documentada"):
        print(f"--- {t} ---\n{r1.controles[t].to_string(index=False)}\n")
    print("Tablas generadas:", ", ".join(f"{n} ({len(d)})" for n, d in r1.tablas.items()))
    ok = bool(r1.controles["verificacion_documentada"].OK.all() and r1.controles["control_integridad"].OK.all()
              and r1.controles["prueba_idempotencia"][["Mismo_conteo", "Mismas_filas"]].all().all())
    print("\nResultado:", "OK - coincide con la documentación" if ok else "REVISAR - hay diferencias (ver tablas de control)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
