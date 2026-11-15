# Guía de Usuario y del Repositorio — SaludVital BI & Streamlit

Esta guía describe la arquitectura, la estructura del proyecto, el funcionamiento del pipeline ETL, el dashboard interactivo en Streamlit y las instrucciones para ejecutar y mantener la solución de Business Intelligence (BI) de **SaludVital**.

---

## 1. Estructura del Repositorio

El proyecto se organiza de la siguiente manera:

```text
SaludVital/
├── app/                        # Aplicación modular en Streamlit
│   ├── app.py                  # Punto de entrada principal y navegación de páginas
│   ├── data.py                 # Carga de datos, modelado en estrella y fusiones 1:N
│   └── medidas.py              # Cálculo de medidas, formateadores y pruebas de aceptación
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
├── docs/                       # Documentación técnica y funcional
│   ├── documentacion_etl.md    # Reglas de negocio, mapeos y especificación ETL
│   ├── guia_usuario.md         # Esta guía de uso
│   ├── Instrucciones.pdf       # Pauta original del caso / proyecto
│   └── Proyecto_SaludVital_Analisis.md # Análisis analítico y estratégico
├── notebooks/                  # Análisis exploratorio interactivo
│   └── analisis_saludvital.ipynb # Notebook Jupyter que valida y grafica
├── reports/                    # Visualización Power BI
│   └── SaludVital.pbix         # Dashboard de BI (Modelo dimensional + DAX)
├── scripts/                    # Scripts de procesamiento
│   └── modelo_dimensional.py   # Script ETL principal (Python + Pandas)
├── .gitignore                  # Archivos excluidos (CSV, XLSX locales, caché, .venv)
├── app.py                      # Entrypoint de conveniencia para Streamlit
├── README.md                   # Resumen ejecutivo del proyecto
└── requirements.txt            # Dependencias de Python (streamlit, plotly, pandas, openpyxl)
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

El script `scripts/modelo_dimensional.py` procesa los libros Excel de origen en `data/`, aplica reglas de validación, limpieza y desduplicación, y genera el modelo dimensional.

### Comando de ejecución:
```bash
python scripts/modelo_dimensional.py
```

---

## 4. Dashboard Interactivo en Streamlit (`app/`)

El tablero interactivo de SaludVital replica el cuadro de mando de Power BI en una aplicación web moderna construida con Streamlit y gráficos de Plotly.

### Arquitectura Modular (`app/`):
- **`app/data.py`**: Carga las tablas del modelo dimensional (con opción de subida mediante `st.file_uploader` si no se encuentran en disco) y realiza uniones *many-to-one* con las dimensiones sin generar *fan-out*.
- **`app/medidas.py`**: Contiene la lógica de cálculo para cada medida (Total Reservas, Tasas de Atención/Inasistencia/Cancelación, Ingresos, Ingreso Promedio, Prestaciones Realizadas, etc.), manejo de división por cero, formateadores en español y las pruebas de aceptación.
- **`app/app.py`**: Interfaz de usuario estructurada en dos páginas y una sección de pruebas, con filtros globales en la barra lateral (`st.session_state`) para rango de fechas, comuna y sexo.

### Páginas del Dashboard:
1. **Resumen de reservas**: Tarjetas métricas (Total Reservas, Atenciones Realizadas, Pacientes Distintos, Ingresos), gráfico de líneas de reservas por día, barras horizontales de reservas por médico y gráfico de anillo por previsión.
2. **Ingresos y prestaciones**: Tarjetas métricas financieras, nota aclaratoria de ingreso valorizado, barras de ingresos por especialidad, Top 10 prestaciones, líneas de ingresos por día y anillo de ingresos por previsión.
3. **Pruebas de aceptación**: Tabla de validación automática que verifica sin filtros los 16 indicadores clave requeridos por la especificación.

### Ejecución del Dashboard:
```bash
streamlit run app/app.py
```
O bien:
```bash
streamlit run app.py
```

---

## 5. Análisis Exploratorio y Power BI

- **Jupyter (`notebooks/analisis_saludvital.ipynb`)**: Análisis exploratorio interactivo para validar las preguntas de negocio.
- **Power BI (`reports/SaludVital.pbix`)**: Dashboard oficial de BI con modelo en estrella y medidas DAX.

---

## 6. Documentación Adicional

- **`docs/documentacion_etl.md`**: Detalla el mapa de procesos, entidades y reglas ETL.
- **`docs/Proyecto_SaludVital_Analisis.md`**: Análisis de negocio en profundidad.
- **`docs/Instrucciones.pdf`**: Pauta y requerimientos originales del caso práctico.
