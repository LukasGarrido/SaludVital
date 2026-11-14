# Guía de Usuario y del Repositorio — SaludVital BI

Esta guía describe la arquitectura, la estructura del proyecto, el funcionamiento del pipeline ETL y las instrucciones para ejecutar y mantener la solución de Business Intelligence (BI) de **SaludVital**.

---

## 1. Estructura del Repositorio

El proyecto se organiza de la siguiente manera:

```text
SaludVital/
├── .venv/                      # Entorno virtual de Python
├── data/                       # Datos de origen y modelo dimensional generado
│   ├── modelo/                 # Esquema en estrella (CSV y Excel consolidado)
│   │   ├── DimFecha.csv
│   │   ├── DimMedico.csv
│   │   ├── DimPaciente.csv
│   │   ├── DimPrestacion.csv
│   │   ├── HechoReservas.csv
│   │   ├── HechoDetalle.csv
│   │   ├── SaludVital_ModeloDimensional.xlsx
│   │   └── control/            # Bitácoras de calidad, rechazos e idempotencia
│   │       ├── control_cardinalidad.csv
│   │       ├── control_carga.csv
│   │       ├── control_dim.csv
│   │       ├── control_fuentes.csv
│   │       ├── control_integridad.csv
│   │       ├── control_merge.csv
│   │       ├── duplicados_descartados.csv
│   │       ├── mapeo_etiquetas.csv
│   │       ├── no_resueltos.csv
│   │       ├── prueba_idempotencia.csv
│   │       ├── rechazos.csv
│   │       ├── reservas_atendidas_sin_atencion.csv
│   │       └── verificacion_documentada.csv
│   ├── SaludVital_BaseDatos.xlsx
│   └── SaludVital_DatosAdicionales.xlsx
├── docs/                       # Documentación técnica y funcional
│   ├── documentacion_etl.md    # Reglas de negocio, mapeos y especificación ETL
│   ├── guia_usuario.md         # Esta guía de uso
│   ├── Instrucciones.pdf       # Pauta original del caso / proyecto
│   └── Proyecto_SaludVital_Analisis.md # Análisis analítico y estratégico
├── reports/                    # Visualización Power BI
│   └── SaludVital.pbix         # Dashboard de BI (Modelo dimensional + DAX)
├── scripts/                    # Scripts de procesamiento
│   └── modelo_dimensional.py   # Script ETL principal (Python + Pandas)
├── .gitignore                  # Archivos excluidos del control de versiones (incl. CSV y entornos)
├── README.md                   # Resumen ejecutivo del proyecto
└── requirements.txt            # Dependencias de Python (pandas, openpyxl)
```

---

## 2. Requisitos Previos e Instalación

1. **Python 3.10+** instalado en el sistema.
2. **Entorno Virtual** configurado (opcional pero recomendado):
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```
3. **Instalación de Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Ejecución del Pipeline ETL

El script `scripts/modelo_dimensional.py` procesa los libros Excel de origen en `data/`, aplica rigurosas reglas de validación, limpieza, desduplicación e idempotencia, y genera el modelo dimensional listo para Power BI.

### Comando de ejecución estándar:
```bash
python scripts/modelo_dimensional.py
```

### Opciones adicionales del script:
- `--out <ruta>`: Especifica la carpeta de salida (por defecto `data/modelo`).
- `--sin-excel`: Omite la generación del archivo consolidado `.xlsx`, generando solo los archivos `.csv` y la carpeta `control/`.

### Resultados generados en `data/modelo/`:
- **Dimensiones:** `DimFecha.csv`, `DimPaciente.csv`, `DimMedico.csv`, `DimPrestacion.csv`.
- **Hechos:** `HechoReservas.csv`, `HechoDetalle.csv`.
- **Control y Calidad (`data/modelo/control/`):** Bitácoras detalladas sobre rechazos, duplicados descartados, pruebas de idempotencia, cardinalidad y consistencia de datos.

---

## 4. Visualización en Power BI (`reports/SaludVital.pbix`)

1. Abrir Power BI Desktop.
2. Cargar el archivo `reports/SaludVital.pbix`.
3. El modelo dimensional en estrella conecta las tablas de dimensiones (`DimFecha`, `DimPaciente`, `DimMedico`, `DimPrestacion`) con las tablas de hechos (`HechoReservas`, `HechoDetalle`) mediante relaciones 1:N (filtrado en un sentido).
4. Las medidas DAX calculan indicadores clave de demanda, ingresos valorizados, tasas de inasistencia y productividad médica.

---

## 5. Documentación Adicional

- **`docs/documentacion_etl.md`**: Detalla el mapa de procesos, entidades, preguntas analíticas de negocio (Dirección, Recepción, Profesionales) y las reglas de validación ETL.
- **`docs/Proyecto_SaludVital_Analisis.md`**: Análisis de negocio en profundidad.
- **`docs/Instrucciones.pdf`**: Pauta y requerimientos originales del caso práctico.
