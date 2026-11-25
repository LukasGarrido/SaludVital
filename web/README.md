# SaludVital · Dashboard en Astro

Réplica del panel de Streamlit (`app/`) como sitio estático con Astro + islas React.
Muestra las mismas 5 páginas y medidas, con filtros propios en cada gráfico, y no necesita servidor Python.

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
│   │   ├── filters.ts          #   estado de filtros, applyFilters y campos disponibles
│   │   ├── chartFilterFields.ts#   conjuntos de campos de filtro por tipo de gráfico
│   │   ├── aggregate.ts        #   groupBy / countBy / sumBy
│   │   ├── series.ts, dates.ts #   agrupación mensual
│   │   ├── format.ts           #   formato es-CL (CLP, %, miles)
│   │   ├── chartTheme.ts       #   tema y paleta de Plotly
│   │   └── content.ts, nav.ts  #   textos editoriales y navegación
│   ├── stores/                 # Stores compartidos (nanostores) persistidos en localStorage
│   │   ├── chartFilters.ts     #   filtros de cada gráfico (por id)
│   │   └── theme.ts            #   modo claro / oscuro
│   ├── hooks/useChartFilters.ts# Filtros y datos filtrados de un gráfico concreto
│   ├── layouts/Layout.astro    # Estructura: barra lateral + contenido
│   ├── components/
│   │   ├── *.astro             #   partes estáticas (marca, navegación, encabezado)
│   │   ├── ui/                 #   Card, KpiGrid, DataTable, Note, Grid, Section…
│   │   ├── charts/             #   PlotlyChart, BarChart, DonutChart, StackedBarChart
│   │   ├── filters/            #   FilterPopover y sus controles (chips, casillas, fechas)
│   │   └── pages/              #   una isla React por página
│   ├── pages/                  # Rutas Astro (una por página del panel)
│   ├── scripts/sidebar.ts      # Barra lateral: fijar/colapsar y enlace activo
│   └── styles/                 # Módulos CSS (ver más abajo)
└── vitest.config.ts
```

### Flujo de datos

`dataset.json` → `applyFilters(filtros del gráfico)` → agregaciones del gráfico → componente.
Cada gráfico, grupo de KPI y tabla tiene **sus propios filtros** (`useChartFilters(id, campos)`), guardados por `id` en un store
y recordados en el navegador. Cambiar el filtro de un gráfico no afecta a los demás.
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

### Filtros por gráfico

Cada tarjeta (`FilterableCard`) y cada grupo de KPI (`FilterableKpis`) muestra un botón **Filtros** con un contador de filtros activos.
Al abrirlo aparece un popover con solo los controles que tienen sentido para ese gráfico: por ejemplo, «Reservas por estado» no
ofrece filtrar por estado, y la frecuencia de uso de pacientes solo responde a comuna y sexo.

| Campos | Dónde |
| --- | --- |
| Período, comuna, sexo, especialidad, médico, estado, previsión, canal | Gráficos y KPI de reservas (menos la dimensión que el propio gráfico ya muestra) |
| Período, comuna, sexo, especialidad, médico, previsión | Gráficos de ingresos (detalle) |
| Comuna, sexo | Frecuencia de uso (cartera de pacientes) |

Para agregar un gráfico con filtros: usa `FilterableCard` con un `id` único, el `scope` de los datos (`reservas`, `detalle` o `cartera`),
la lista de `fields` (ver `lib/chartFilterFields.ts`) y una función `render(data)` que dibuja el gráfico con los datos ya filtrados.

### Paridad con Streamlit

- Las 16 pruebas de aceptación se ejecutan en `npm test` y en la página *Pruebas de aceptación*.
- Los filtros siguen la misma semántica de datos: vacío = todos, la cartera de pacientes ignora la fecha y estado/canal acotan también el detalle.
  A diferencia de Streamlit (filtros globales en la barra lateral), aquí cada gráfico se filtra de forma independiente.

> Si cambia el ETL o el modelo en `data/modelo`, ejecuta `npm run export-data` y commitea el JSON.
