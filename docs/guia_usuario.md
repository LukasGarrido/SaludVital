<div align="center">

# Guía de Usuario y del Repositorio — SaludVital BI & Streamlit

Esta guía describe la arquitectura, la estructura del proyecto, el funcionamiento del pipeline ETL, el dashboard interactivo en Streamlit y las instrucciones para ejecutar y mantener la solución de Business Intelligence (BI) de **SaludVital**.

</div>

---

## 1. Estructura del Repositorio

El proyecto se organiza de la siguiente manera:

```text
SaludVital/
├── app/                        # Aplicación modular en Streamlit
│   ├── __init__.py             # Inicializador del paquete Streamlit
│   ├── app.py                  # Punto de entrada principal y navegación de páginas
│   ├── data.py                 # Carga de datos, modelado en estrella y fusiones 1:N
│   ├── medidas.py              # Cálculo de medidas, formateadores y pruebas de aceptación
│   └── styles.py               # Estilos visuales, temas y diseño corporativo
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
│   ├── guia_usuario.md         # Guía de uso y funcionamiento del repo
│   └── informe/                # Informe formal del proyecto (v2.1)
│       ├── Informe_SaludVital.md # Informe integral de proyecto
│       └── img/                # Figuras y visualizaciones del informe (fig01 a fig17)
├── notebooks/                  # Análisis exploratorio interactivo
│   └── analisis_saludvital.ipynb # Notebook Jupyter para análisis y respuestas a preguntas de negocio
├── reports/                    # Visualización Power BI
│   └── SaludVital.pbix         # Dashboard de BI (Modelo dimensional + DAX)
├── scripts/                    # Scripts de procesamiento
│   └── modelo_dimensional.py   # Script ETL en Python (Pandas)
├── theme/                      # Recursos visuales corporativos
│   └── SaludVital.json         # Tema de diseño corporativo para Power BI
├── .gitignore                  # Archivos ignorados (CSV, XLSX, PBIX, caché, .venv)
├── AGENTS.md                   # Guía de referencia para agentes de IA y desarrollo
├── app.py                      # Entrypoint de conveniencia para Streamlit
├── README.md                   # Resumen ejecutivo del proyecto
└── requirements.txt            # Dependencias de Python
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

El tablero interactivo de SaludVital replica exactamente el cuadro de mando de Power BI en una aplicación web moderna construida con Streamlit y gráficos de Plotly.

### Arquitectura Modular (`app/`):
- **`app/data.py`**: Carga las tablas del modelo dimensional, calcula columnas derivadas en `DimPaciente` (`Reservas del Paciente`, `Tramo Frecuencia`, `Orden Tramo`) y realiza uniones *many-to-one* con las dimensiones sin generar *fan-out*.
- **`app/medidas.py`**: Contiene la lógica de cálculo para cada medida (Total Reservas, Tasas de Atención/Inasistencia/Cancelación, Ingresos, Ingreso Promedio, Horas Perdidas, Utilización, Cobertura de Bloque, Pacientes Distintos, etc.), formateadores en español y las pruebas de aceptación.
- **`app/app.py`**: Interfaz de usuario estructurada en cinco páginas, con filtros globales en la barra lateral para rango de fechas, comuna y sexo.

### Páginas del Dashboard:
1. **Resumen**: Cuatro tarjetas métricas (Total de reservas, Tasa de atención, Tasa de inasistencia, Ingreso valorizado), cuadros de Conclusiones y Recomendaciones operacionales, y la nota visible al pie.
2. **Visión ejecutiva**: Seis tarjetas (Total de reservas, Atenciones registradas, Tasa de atención, Tasa de inasistencia, Ingreso valorizado, Ingreso promedio por atención), gráficos de reservas por estado, reservas por mes, reservas por especialidad del médico, ingreso valorizado por mes y tabla de tasas por mes.
3. **Gestión médica**: Gráficos de reservas atendidas por médico, reservas por estado y médico, tasa de inasistencia por especialidad, horas perdidas por mes, horas perdidas por canal (con bloque) y tabla de desempeño por médico con formato condicional (rojo <50%, verde >=50%).
4. **Pacientes**: Dos tarjetas (Pacientes con reservas, Reservas por paciente), reservas atendidas por comuna, reservas por previsión, ingresos por previsión valorizado, frecuencia de uso (tramo de frecuencia), pacientes distintos por mes y tabla de pacientes con 2 o más inasistencias (solo IDs).
5. **Pruebas de aceptación**: Tabla de validación automática que verifica sin filtros los 16 indicadores clave requeridos por la especificación.

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

### 5.1. Jupyter

`notebooks/analisis_saludvital.ipynb` contiene el análisis exploratorio interactivo que valida las preguntas de negocio y recalcula los indicadores con las mismas definiciones DAX.

### 5.2. Tablero de Power BI (`reports/SaludVital.pbix`)

El tablero oficial se apoya en el modelo en estrella (dos hechos y cuatro dimensiones) y en las medidas DAX del capítulo 9 del informe. Tiene cuatro páginas:

| Página | Contenido |
|---|---|
| **Resumen** | Cuatro tarjetas (reservas, tasa de atención, tasa de inasistencia, ingreso valorizado), conclusiones, recomendaciones operacionales y nota de cobertura |
| **Visión ejecutiva** | Seis tarjetas, reservas por estado, reservas por mes, reservas por especialidad, ingreso por mes y tasas por mes |
| **Gestión médica** | Reservas atendidas por médico, estados por médico, inasistencia por especialidad, horas perdidas por mes y por canal, y tabla de desempeño por médico |
| **Pacientes** | Pacientes con reservas, reservas por paciente, comuna, previsión (reservas e ingresos), frecuencia de uso, pacientes por mes y pacientes con inasistencias repetidas (solo IDs) |

Todas las páginas incluyen la nota visible de cobertura, simulación y limitaciones, y las páginas de análisis incluyen las segmentaciones de fecha, comuna y sexo.

**Cómo usarlo**
- Abre `reports/SaludVital.pbix` en Power BI Desktop.
- Para cambiar de página, usa el navegador inferior con **Ctrl + clic** (en Desktop un clic solo selecciona el botón) o las pestañas de la parte inferior.
- Las segmentaciones de fecha, comuna y sexo están sincronizadas entre páginas. Para ver los valores generales, deja todas sin selección.
- Pasa el mouse sobre un gráfico y usa **... → Mostrar como tabla** para ver los números exactos.

**Medidas principales** (tabla `_Medidas`)

| Medida | Qué calcula |
|---|---|
| `Total Reservas`, `Reservas Atendidas`, `Reservas No Asistió`, `Reservas Canceladas`, `Reservas Pendientes`, `Reservas Resueltas` | Conteos de reservas por estado |
| `Atenciones Realizadas` | Atenciones registradas (46) |
| `Tasa de Atención`, `Tasa de Inasistencia`, `Tasa de Cancelación` | Tasas sobre reservas resueltas (las pendientes no entran al denominador) |
| `Ingresos` | Suma de `Cantidad × ValorUnitario`. Es ingreso valorizado, no cobrado |
| `Ticket Promedio` | Ingreso promedio por atención valorizada |
| `Horas Perdidas por Inasistencia (con bloque)`, `Utilización (solo reservas con bloque)`, `Cobertura de Bloque` | Horas y utilización calculadas solo sobre reservas con bloque horario (51 % del total) |
| `Pacientes Distintos`, `Reservas por Paciente`, `Pacientes (cartera)` | Medidas de pacientes |

Las columnas calculadas de `DimPaciente` (`Reservas del Paciente`, `Tramo Frecuencia` y `Orden Tramo`) se crean en ese orden, porque cada una depende de la anterior. `Tramo Frecuencia` se ordena por `Orden Tramo` y `DimFecha[Mes]` por `MesNum`.

**Actualización de datos**
1. Ejecuta el pipeline ETL (sección 3) si cambiaron los libros Excel de origen.
2. En Power BI Desktop, usa **Inicio → Actualizar**.
3. Revisa que `control_carga` entregue 75 reservas, 46 atenciones, 41 detalles y 38 canales aceptados.
4. Confirma que no haya relaciones nuevas creadas automáticamente. La detección automática de relaciones debe estar desactivada.

**Verificación rápida.** Con las segmentaciones sin selección, el tablero debe mostrar: 75 reservas, 46 atenciones, tasa de atención 68,6 %, inasistencia 20,0 %, cancelación 14,3 %, ingreso valorizado $1.671.000, ingreso promedio $40.756, 44 pacientes con reservas y 5,0 horas perdidas. La lista completa de valores de control está en la Tabla 26 del informe.

**Limitaciones que conviene recordar al usarlo**
- Los datos son una simulación y cubren del 05-01-2026 al 28-02-2026.
- Los ingresos son valorizados, no cobrados.
- Las horas perdidas y la utilización solo cubren las reservas con bloque horario.
- Reservas por especialidad usa la especialidad del médico e ingresos por especialidad usa la de la prestación, por lo que no deben compararse directamente.

### 5.3. Capturas del tablero

Guarda una captura por página en `reports/capturas/` con estos nombres, que son los que usa el informe:

| Archivo | Página |
|---|---|
| `fig18_pbi_resumen.png` | Resumen |
| `fig19_pbi_vision_ejecutiva.png` | Visión ejecutiva |
| `fig20_pbi_gestion_medica.png` | Gestión médica |
| `fig21_pbi_pacientes.png` | Pacientes |

Para capturar, deja las segmentaciones sin selección y usa **Win + Shift + S**, o bien **Archivo → Exportar → Exportar a PDF**. El informe referencia las imágenes desde su carpeta `img/`, así que copia también los cuatro archivos allí.

---

## 6. Documentación Adicional

- **`docs/guia_usuario.md`**: Guía de uso y funcionamiento del repositorio y la aplicación.
- **`docs/informe/Informe_SaludVital.md`**: Informe integral de proyecto (versión 2.1), con análisis estratégico, especificación ETL, modelo dimensional, medidas DAX, tablero Power BI (capítulo 9), valores de control (sección 10.4) y recomendaciones operacionales (sección 13.1).
