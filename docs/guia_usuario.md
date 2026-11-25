<div align="center">

# Guía de Usuario y del Repositorio — SaludVital BI, Streamlit & Astro

Esta guía describe la arquitectura, la estructura del proyecto, el funcionamiento del pipeline ETL, los dashboards interactivos en Streamlit y Astro y las instrucciones para ejecutar y mantener la solución de Business Intelligence (BI) de **SaludVital**.

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
├── assets/                     # Recursos gráficos e imágenes del proyecto
│   ├── universidad-tecnica-federico-santa-maria-seeklogo.png # Logo institucional
│   └── img/                    # Figuras y visualizaciones del análisis (fig01 a fig17)
├── docs/                       # Documentación técnica y funcional
│   ├── guia_usuario.md         # Guía de uso y funcionamiento del repo
│   └── Informe_SaludVital.md   # Informe integral de proyecto (versión 2.1)
├── notebooks/                  # Análisis exploratorio interactivo
│   └── analisis_saludvital.ipynb # Notebook Jupyter para análisis y respuestas a preguntas de negocio
├── reports/                    # Visualización Power BI
│   └── SaludVital.pbix         # Dashboard de BI (Modelo dimensional + DAX)
├── scripts/                    # Scripts de procesamiento
│   └── modelo_dimensional.py   # Script ETL en Python (Pandas)
├── theme/                      # Recursos visuales corporativos
│   └── SaludVital.json         # Tema de diseño corporativo para Power BI
├── web/                        # Dashboard alternativo en Astro + React (sitio estático)
│   ├── scripts/
│   │   └── export_data.py      # Exporta el modelo enriquecido a JSON (reutiliza app/data.py)
│   ├── src/
│   │   ├── data/dataset.json   # Modelo exportado (reservas, detalle, pacientes)
│   │   ├── lib/                # Lógica pura en TypeScript: medidas, filtros, pruebas, formato
│   │   ├── stores/             # Estado compartido: filtros y tema claro/oscuro
│   │   ├── hooks/              # useFilteredData, useTokens
│   │   ├── components/         # ui/, charts/, filters/, pages/ y piezas .astro
│   │   ├── layouts/            # Layout.astro (barra lateral + contenido)
│   │   ├── pages/              # Una ruta por página del panel
│   │   └── styles/             # tokens, base, glass, layout, cards, charts, table, filters, motion
│   ├── Dockerfile              # Imagen multi-etapa (dev y producción con nginx)
│   ├── nginx.conf              # Configuración de nginx para el sitio estático
│   ├── package.json            # Dependencias y scripts (dev, build, test, export-data)
│   └── README.md               # Documentación técnica del dashboard Astro
├── .gitignore                  # Archivos ignorados (CSV, XLSX, PBIX, caché, .venv)
├── Dockerfile                  # Imagen del dashboard de Streamlit
├── docker-compose.yml          # Despliegue (producción): Streamlit + Astro (nginx)
├── docker-compose.dev.yml      # Override de desarrollo: bind mounts y recarga en caliente
├── .env.example                # Puertos configurables para docker compose
├── AGENTS.md                   # Guía de referencia para agentes de IA y desarrollo
├── app.py                      # Entrypoint de conveniencia para Streamlit
├── LICENSE                     # Licencia MIT
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
4. **Docker y Docker Compose** (opcional, para la sección 7).
5. **Node.js 20+** (solo para ejecutar el dashboard en Astro sin Docker, sección 5):
   ```bash
   cd web
   npm install
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
- **`app/styles.py`**: Capa visual del panel (CSS, tema de los gráficos Plotly y controles de filtros).
- **`app/app.py`**: Interfaz de usuario estructurada en cinco páginas, con filtros globales en la barra lateral: atajo de período, rango de fechas, comuna y sexo, más un panel de filtros avanzados (especialidad, médico, estado de la reserva, previsión y canal), un resumen de filtros activos y un contador de reservas visibles.

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

## 5. Dashboard en Astro (`web/`)

Réplica estática del panel de Streamlit construida con **Astro + React + TypeScript** y gráficos Plotly. No necesita servidor Python: el modelo dimensional se exporta una vez a JSON y todo el cálculo (filtros, medidas y pruebas de aceptación) ocurre en el navegador.

### Ejecución

Desde `web/`:

| Comando | Acción |
|---|---|
| `npm install` | Instala las dependencias |
| `npm run export-data` | Regenera `src/data/dataset.json` desde `data/modelo` (requiere Python) |
| `npm run dev` | Servidor de desarrollo en `http://localhost:4321` |
| `npm run build` | Chequeo de tipos y build estático en `dist/` |
| `npm run preview` | Sirve `dist/` localmente |
| `npm test` | Pruebas de paridad con Streamlit y de filtros |

Para publicarlo en una subruta (por ejemplo GitHub Pages): `SITE_BASE=/SaludVital/ npm run build`.

### Arquitectura

- **`scripts/export_data.py`**: reutiliza `app/data.py` para exportar reservas, detalle y pacientes ya enriquecidos con sus dimensiones.
- **`src/lib/`**: lógica pura sin React. `measures.ts` y `acceptance.ts` son el port de `calcular_medidas` y `ejecutar_pruebas_aceptacion`; `filters.ts` aplica los filtros globales con la misma semántica que Streamlit; `format.ts` entrega el formato es-CL (CLP, porcentajes, miles).
- **`src/stores/`**: estado compartido entre páginas (filtros y tema), persistido en el navegador.
- **`src/components/`**: componentes reutilizables (`ui/`, `charts/`, `filters/`), una isla React por página (`pages/`) y piezas estáticas `.astro`.
- **`src/styles/`**: `tokens.css` define toda la paleta en variables CSS para el tema claro y el oscuro.

### Páginas y filtros

Las cinco páginas (Resumen, Visión ejecutiva, Gestión médica, Pacientes y Pruebas de aceptación) muestran los mismos indicadores que el dashboard de Streamlit. Los filtros globales de la barra lateral se conservan al navegar entre páginas:

- Atajo de período (todo el período, enero, febrero, últimos 30 días) y rango de fechas.
- Comuna y sexo (parten con todo seleccionado).
- Filtros avanzados: especialidad, médico, estado de la reserva, previsión y canal (sin selección equivale a todos).
- La frecuencia de uso de pacientes responde a comuna y sexo, pero no a la fecha.
- Las pruebas de aceptación siempre se ejecutan sobre el modelo completo, sin filtros.

### Diseño glass, menú expandible y transiciones

- **Estilo:** vidrio translúcido en azules con el coral de SaludVital como acento cálido.
- **Menú lateral:** riel de iconos que se expande al pasar el cursor; el botón inferior lo fija abierto (se recuerda la elección).
- **Navegación:** transiciones animadas entre páginas sin recargar; el menú y los filtros se conservan.
- **Gráficos:** barras que crecen al aparecer, barra máxima destacada y transición suave al filtrar.

### Modo claro y oscuro

El botón de sol y luna en la parte inferior del menú lateral alterna el tema. La primera vez se usa la preferencia del sistema y después se recuerda la elección. Para cambiar la identidad visual basta con editar `src/styles/tokens.css`.

### Mantenimiento

- Si cambia el modelo en `data/modelo` (por ejemplo, tras ejecutar el ETL), corre `npm run export-data` y commitea el JSON resultante.
- La lógica de medidas existe en Python y en TypeScript: `npm test` verifica que las 16 pruebas de aceptación den las mismas cifras en ambas.

---

## 6. Análisis Exploratorio y Power BI

### 6.1. Jupyter

`notebooks/analisis_saludvital.ipynb` contiene el análisis exploratorio interactivo que valida las preguntas de negocio y recalcula los indicadores con las mismas definiciones DAX.

### 6.2. Tablero de Power BI (`reports/SaludVital.pbix`)

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

### 6.3. Capturas del tablero

Guarda una captura por página en `reports/capturas/` con estos nombres, que son los que usa el informe:

| Archivo | Página |
|---|---|
| `fig18_pbi_resumen.png` | Resumen |
| `fig19_pbi_vision_ejecutiva.png` | Visión ejecutiva |
| `fig20_pbi_gestion_medica.png` | Gestión médica |
| `fig21_pbi_pacientes.png` | Pacientes |

Para capturar, deja las segmentaciones sin selección y usa **Win + Shift + S**, o bien **Archivo → Exportar → Exportar a PDF**. El informe referencia las imágenes desde su carpeta `img/`, así que copia también los cuatro archivos allí.

---

## 7. Despliegue con Docker

El repositorio incluye imágenes y archivos de Compose para ejecutar ambos dashboards sin instalar Python ni Node.

### Archivos

| Archivo | Función |
|---|---|
| `Dockerfile` | Imagen de Streamlit (Python 3.12 slim, usuario sin privilegios, healthcheck) |
| `web/Dockerfile` | Imagen multi-etapa de Astro: target `dev` (servidor de desarrollo) y `prod` (nginx sin privilegios) |
| `web/nginx.conf` | Sirve el sitio estático, caché larga para `/_astro/`, cabeceras de seguridad y `/healthz` |
| `docker-compose.yml` | Despliegue de producción de ambos servicios |
| `docker-compose.dev.yml` | Override de desarrollo con bind mounts y recarga en caliente |
| `.env.example` | Puertos configurables (`STREAMLIT_PORT`, `WEB_PORT`, `WEB_DEV_PORT`) |

### Producción

```bash
docker compose up -d --build
```

- Streamlit: `http://localhost:8501`
- Astro (nginx): `http://localhost:8080`

Los contenedores corren sin privilegios, con sistema de archivos de solo lectura y `no-new-privileges`. Ambos tienen `healthcheck`; revisa su estado con `docker compose ps`.

### Desarrollo

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

- Streamlit (`app/` montado, recarga al guardar): `http://localhost:8501`
- Astro (servidor de desarrollo con recarga en caliente): `http://localhost:4321`

Se usa *polling* para detectar cambios porque los eventos de archivo no cruzan los bind mounts en Windows y macOS.

### Datos

`data/` está en `.gitignore`, por lo que los CSV del modelo **no se incluyen en la imagen**: Streamlit los lee del volumen `./data` (montado en solo lectura). Antes de levantarlo, genera el modelo con el pipeline ETL (sección 3). Si faltan, la app permite subir los archivos desde la interfaz. El dashboard de Astro no necesita volumen porque su `dataset.json` está versionado en `web/src/data/`.

### Comandos útiles

```bash
docker compose logs -f streamlit      # logs de un servicio
docker compose down                   # detiene y elimina los contenedores
docker compose build --no-cache web   # reconstruye una imagen desde cero
```

> Si cambias el modelo, ejecuta `npm run export-data` en `web/` y reconstruye la imagen de Astro (`docker compose up -d --build web`).

---

## 8. Documentación Adicional

- **`docs/guia_usuario.md`**: Guía de uso y funcionamiento del repositorio y las aplicaciones.
- **`web/README.md`**: Documentación técnica del dashboard en Astro.
- **`docs/Informe_SaludVital.md`**: Informe integral de proyecto (versión 2.1), con análisis estratégico, especificación ETL, modelo dimensional, medidas DAX, tablero Power BI (capítulo 9), valores de control (sección 10.4) y recomendaciones operacionales (sección 13.1).
