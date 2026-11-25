# SaludVital · Dashboard en Astro

Réplica del panel de Streamlit (`app/`) como sitio estático con Astro + islas React.
Muestra las mismas 5 páginas, filtros globales y medidas, y no necesita servidor Python.

## Comandos

Desde `web/`:

| Comando | Acción |
| --- | --- |
| `npm install` | Instala dependencias |
| `npm run export-data` | Regenera `src/data/dataset.json` desde el modelo de `data/modelo` (requiere Python) |
| `npm run dev` | Servidor de desarrollo en `http://localhost:4321` |
| `npm run build` | Chequeo de tipos + build estático en `dist/` |
| `npm run preview` | Sirve `dist/` localmente |
| `npm test` | Pruebas (paridad con Streamlit y filtros) |

Para desplegar en una subruta (p. ej. GitHub Pages): `SITE_BASE=/SaludVital/ npm run build`.

## Arquitectura

```text
web/
├── scripts/export_data.py      # Python: exporta el modelo enriquecido a JSON (reutiliza app/data.py)
├── src/
│   ├── data/dataset.json       # Modelo exportado (reservas, detalle, pacientes)
│   ├── lib/                    # Lógica pura, sin React (testeable)
│   │   ├── types.ts            #   tipos del modelo
│   │   ├── measures.ts         #   port de calcular_medidas
│   │   ├── acceptance.ts       #   port de ejecutar_pruebas_aceptacion
│   │   ├── filters.ts          #   estado de filtros y applyFilters
│   │   ├── aggregate.ts        #   groupBy / countBy / sumBy
│   │   ├── series.ts, dates.ts #   agrupación mensual
│   │   ├── format.ts           #   formato es-CL (CLP, %, miles)
│   │   ├── chartTheme.ts       #   tema y paleta de Plotly
│   │   └── content.ts, nav.ts  #   textos editoriales y navegación
│   ├── stores/                 # Stores compartidos (nanostores) persistidos en localStorage
│   │   ├── filters.ts          #   filtros globales
│   │   └── theme.ts            #   modo claro / oscuro
│   ├── hooks/useFilteredData.ts# Datos filtrados + medidas para cualquier página
│   ├── layouts/Layout.astro    # Estructura: barra lateral + contenido
│   ├── components/
│   │   ├── *.astro             #   partes estáticas (marca, navegación, encabezado)
│   │   ├── ui/                 #   Card, KpiGrid, DataTable, Note, Grid, Section…
│   │   ├── charts/             #   PlotlyChart, BarChart, DonutChart, StackedBarChart
│   │   ├── filters/            #   FilterPanel y sus controles
│   │   └── pages/              #   una isla React por página
│   ├── pages/                  # Rutas Astro (una por página del panel)
│   └── styles/                 # tokens.css (claro + oscuro), base.css, components.css
└── vitest.config.ts
```

### Flujo de datos

`dataset.json` → `applyFilters(filtros)` → `calcularMedidas` → componentes de página.
Los filtros viven en un store compartido, por lo que se conservan al navegar entre páginas.
Las islas usan `client:only="react"` porque dependen del estado del navegador.

### Tema claro y oscuro

La paleta es minimalista: superficies planas, un azul de acento y colores de contraste puntuales (ámbar, turquesa, coral, violeta).
Todos los colores viven como variables CSS en `src/styles/tokens.css`; el modo oscuro se activa con `<html data-theme="dark">`.
Un script en el `<head>` aplica la preferencia guardada (o la del sistema) antes de pintar, y los gráficos Plotly leen las mismas variables, por lo que cambian de tema sin recargar.
Para ajustar la identidad visual basta con editar `tokens.css`.

### Paridad con Streamlit

- Las 16 pruebas de aceptación se ejecutan en `npm test` y en la página *Pruebas de aceptación*.
- Los filtros siguen la misma semántica: comuna y sexo parten con todo seleccionado, el resto vacío = todos,
  la cartera de pacientes ignora la fecha y estado/canal acotan también el detalle.

> Si cambia el ETL o el modelo en `data/modelo`, ejecuta `npm run export-data` y commitea el JSON.
