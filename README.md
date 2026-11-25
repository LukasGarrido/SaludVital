<div align="center">

# SaludVital BI

Solución de BI (ETL + modelo dimensional + dashboard interactivo en Streamlit y Astro, y reporte en Power BI) para analizar las atenciones médicas de SaludVital, centro médico ambulatorio privado de la Región del Biobío.

</div>

## Contexto

SaludVital lleva 8 años operando, tiene 10 especialidades, más de 20 profesionales y ~2.000 consultas mensuales. Sus sistemas no permiten análisis multidimensional, lo que genera:

- Información dispersa en distintas fuentes
- Pacientes duplicados y especialidades con nombres inconsistentes
- Reservas que no terminan en atención (Atendida, Cancelada, No asistió, Pendiente)
- Reportes mensuales manuales y sin visión consolidada del desempeño

## Objetivo

Diseñar e implementar una solución de BI que permita analizar demanda, atención, desempeño médico, pacientes e ingresos para apoyar la toma de decisiones de la dirección.

## Estructura del repositorio

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
│   │   ├── stores/             # Estado compartido: filtros por gráfico y tema claro/oscuro
│   │   ├── hooks/              # useChartFilters, useTokens
│   │   ├── components/         # ui/, charts/, filters/, pages/ y piezas .astro
│   │   ├── layouts/            # Layout.astro (barra lateral + contenido)
│   │   ├── pages/              # Una ruta por página del panel
│   │   └── styles/             # tokens.css (claro y oscuro), base.css, components.css
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

## Stack

Python (Streamlit + Pandas + Plotly) · Astro + React + TypeScript (dashboard estático) · Power BI + DAX (reporte) · Jupyter Notebooks · Excel (fuente)

## Ejecución del Dashboard en Streamlit

```bash
streamlit run app/app.py
```

## Dashboard alternativo en Astro

El directorio [`web/`](web/README.md) contiene una réplica estática del panel construida con Astro + React, sin servidor Python. Incluye las mismas cinco páginas, filtros propios en cada gráfico (botón «Filtros» en la cabecera de cada tarjeta) y un modo claro/oscuro.

```bash
cd web
npm install
npm run dev      # http://localhost:4321
```

Otros comandos útiles (desde `web/`):

```bash
npm run export-data   # regenera el JSON desde data/modelo (requiere Python)
npm test              # pruebas de paridad con Streamlit y de filtros
npm run build         # chequeo de tipos + build estático en dist/
```

## Despliegue con Docker

Ambos dashboards se pueden levantar con Docker Compose, tanto en desarrollo como en producción.

| Servicio | Producción | Desarrollo |
| --- | --- | --- |
| Streamlit | http://localhost:8501 | http://localhost:8501 |
| Astro | http://localhost:8080 (nginx) | http://localhost:4321 (dev server) |

**Producción** (imágenes inmutables, usuario sin privilegios, sistema de archivos de solo lectura):

```bash
docker compose up -d --build
```

**Desarrollo** (código montado desde el host con recarga en caliente):

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Notas:

- Los CSV del modelo (`data/modelo`) no están versionados ni van dentro de la imagen: Streamlit los lee del volumen `./data`. Si faltan, la app permite subirlos desde la interfaz. El dashboard de Astro no necesita volumen porque su JSON va en el repositorio.
- Los puertos se pueden cambiar copiando `.env.example` a `.env`.
- Para detener todo: `docker compose down`.

## Documentación y Guía de Uso

- **[Guía de Usuario (`docs/guia_usuario.md`)](docs/guia_usuario.md)**: Instrucciones detalladas de configuración, ejecución del pipeline ETL, uso de los dashboards de Streamlit y Astro, y estructura.
- **[Informe Formal de Proyecto (`docs/Informe_SaludVital.md`)](docs/Informe_SaludVital.md)**: Documento formal completo (v2.1) con análisis, reglas, ETL, modelo dimensional, medidas DAX y validación con Jupyter.

## Licencia

El código se distribuye bajo licencia [MIT](LICENSE). Los datos incluidos son simulados y no corresponden a la operación real de SaludVital.
