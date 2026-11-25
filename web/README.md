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
│   ├── scripts/sidebar.ts      # Barra lateral: fijar/colapsar y enlace activo
│   └── styles/                 # Módulos CSS (ver más abajo)
└── vitest.config.ts
```

### Flujo de datos

`dataset.json` → `applyFilters(filtros)` → `calcularMedidas` → componentes de página.
Los filtros viven en un store compartido, por lo que se conservan al navegar entre páginas.
Las islas usan `client:only="react"` porque dependen del estado del navegador.

### Estilos (glass)

Los estilos se dividen en módulos que `styles/index.css` importa en orden de cascada:

| Archivo | Contenido |
| --- | --- |
| `tokens.css` | Variables de diseño del tema claro y oscuro (colores, vidrio, radios, sombras, movimiento) |
| `base.css` | Reset, tipografía y fondo con halos de luz |
| `glass.css` | Superficie de vidrio compartida: degradado, resplandor azul, borde luminoso y desenfoque |
| `layout.css` | Estructura, cabecera, marca y barra lateral |
| `cards.css`, `table.css`, `filters.css`, `charts.css` | Componentes |
| `motion.css` | Transiciones entre vistas, entrada escalonada y `prefers-reduced-motion` |

### Barra lateral expandible

En escritorio la barra es un panel flotante de vidrio que vive como **riel de iconos** y se expande al pasar el cursor
(o al enfocarla con el teclado) como un overlay. El botón de la parte inferior la **fija** abierta y desplaza el contenido;
el estado se recuerda en `localStorage` y se aplica desde el `<head>` para evitar saltos. En pantallas angostas la barra
pasa arriba y queda siempre expandida.

### Transiciones entre vistas

El `Layout` usa `ClientRouter` de Astro (View Transitions): la navegación no recarga el documento, la barra lateral
**persiste** entre páginas (conserva filtros y estado) y el contenido entra con una animación definida en
`lib/transitions.ts` y `styles/motion.css`. Las páginas se precargan al pasar el cursor por los enlaces.
Con `prefers-reduced-motion` todas las animaciones se desactivan.

### Gráficos

Las barras son azules translúcidas con la de mayor valor destacada (azul vivo con resplandor); crecen desde el eje al
aparecer y se interpolan al cambiar los filtros. El donut muestra el total al centro y los tooltips son burbujas blancas.
Los colores se leen de las variables CSS (`lib/chartTheme.ts`), por lo que siguen al tema activo.

### Tema claro y oscuro

La paleta es azul sobre vidrio, con el **coral de SaludVital** (`--hot`) como único acento cálido de contraste (segmentos de alerta, previsión Isapre, línea del encabezado).
Todos los colores viven como variables CSS en `src/styles/tokens.css`; el modo oscuro se activa con `<html data-theme="dark">`.
Un script en el `<head>` aplica la preferencia guardada (o la del sistema) antes de pintar, y los gráficos Plotly leen las mismas variables, por lo que cambian de tema sin recargar.
Para ajustar la identidad visual basta con editar `tokens.css`.

### Paridad con Streamlit

- Las 16 pruebas de aceptación se ejecutan en `npm test` y en la página *Pruebas de aceptación*.
- Los filtros siguen la misma semántica: comuna y sexo parten con todo seleccionado, el resto vacío = todos,
  la cartera de pacientes ignora la fecha y estado/canal acotan también el detalle.

> Si cambia el ETL o el modelo en `data/modelo`, ejecuta `npm run export-data` y commitea el JSON.
