# Guía de Usuario y del Repositorio — SaludVital BI

Esta guía describe la arquitectura, la estructura del proyecto, el funcionamiento del pipeline ETL, el análisis exploratorio en Jupyter y las instrucciones para ejecutar y mantener la solución de Business Intelligence (BI) de **SaludVital**.

---

## 1. Estructura del Repositorio

El proyecto se organiza de la siguiente manera:

```text
SaludVital/
├── .venv/                      # Entorno virtual de Python
├── data/                       # Datos de origen y modelo dimensional generado
│   ├── modelo/                 # Esquema en estrella (CSV y control)
│   │   ├── DimFecha.csv        # Dimensión Fecha (86 filas)
│   │   ├── DimMedico.csv       # Dimensión Médico (14 filas)
│   │   ├── DimPaciente.csv     # Dimensión Paciente (44 filas)
│   │   ├── DimPrestacion.csv   # Dimensión Prestación (19 filas)
│   │   ├── HechoReservas.csv   # Tabla de Hechos: Reservas (75 filas)
│   │   ├── HechoDetalle.csv    # Tabla de Hechos: Detalle de Prestaciones (41 filas)
│   │   ├── SaludVital_ModeloDimensional.xlsx # Libro Excel consolidado del modelo
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
│   ├── SaludVital_BaseDatos.xlsx        # Libro Excel fuente período base
│   └── SaludVital_DatosAdicionales.xlsx # Libro Excel fuente período adicional
├── docs/                       # Documentación técnica y funcional
│   ├── documentacion_etl.md    # Reglas de negocio, mapeos y especificación ETL
│   ├── guia_usuario.md         # Esta guía de uso
│   ├── Instrucciones.pdf       # Pauta original del caso / proyecto
│   └── Proyecto_SaludVital_Analisis.md # Análisis analítico y estratégico
├── notebooks/                  # Análisis exploratorio interactivo
│   └── analisis_saludvital.ipynb # Notebook Jupyter que valida y grafica las 24 preguntas de negocio
├── reports/                    # Visualización Power BI
│   └── SaludVital.pbix         # Dashboard de BI (Modelo dimensional + DAX)
├── scripts/                    # Scripts de procesamiento
│   └── modelo_dimensional.py   # Script ETL principal (Python + Pandas)
├── .gitignore                  # Archivos excluidos (CSV, XLSX locales, checkpoints, .venv)
├── README.md                   # Resumen ejecutivo del proyecto
└── requirements.txt            # Dependencias de Python (pandas, openpyxl, etc.)
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

El script `scripts/modelo_dimensional.py` procesa los libros Excel de origen en `data/`, aplica rigurosas reglas de validación, limpieza, desduplicación e idempotencia, y genera el modelo dimensional listo para Power BI y análisis.

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

## 4. Análisis Exploratorio en Jupyter (`notebooks/analisis_saludvital.ipynb`)

El notebook interactivo `notebooks/analisis_saludvital.ipynb` permite realizar un análisis exploratorio y validar con gráficos las 24 preguntas de negocio del proyecto (D1–D5, R1–R5, M1–M5, P1–P5 y RQ01–RQ24).

### Instrucciones de uso:
1. Asegurarse de haber ejecutado previamente el ETL (`python scripts/modelo_dimensional.py`) para generar las tablas en `data/modelo/`.
2. Abrir Jupyter Lab o Jupyter Notebook:
   ```bash
   jupyter notebook
   ```
3. Abrir `notebooks/analisis_saludvital.ipynb` y ejecutar todas las celdas (*Run All*).

---

## 5. Visualización en Power BI (`reports/SaludVital.pbix`)

1. Abrir Power BI Desktop.
2. Cargar el archivo `reports/SaludVital.pbix`.
3. El modelo dimensional en estrella conecta las tablas de dimensiones (`DimFecha`, `DimPaciente`, `DimMedico`, `DimPrestacion`) con las tablas de hechos (`HechoReservas`, `HechoDetalle`) mediante relaciones 1:N (filtrado en un sentido).
4. Las medidas DAX calculan indicadores clave de demanda, ingresos valorizados, tasas de inasistencia y productividad médica.

---

## 6. Documentación Adicional

- **`docs/documentacion_etl.md`**: Detalla el mapa de procesos, entidades, preguntas analíticas de negocio y las reglas de validación ETL.
- **`docs/Proyecto_SaludVital_Analisis.md`**: Análisis de negocio en profundidad.
- **`docs/Instrucciones.pdf`**: Pauta y requerimientos originales del caso práctico.
