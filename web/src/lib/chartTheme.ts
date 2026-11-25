import type { Config, Layout } from 'plotly.js-basic-dist-min';

/** Colores resueltos del tema activo (se leen de las variables CSS, única fuente de verdad). */
export interface ChartTokens {
  ink: string;
  muted: string;
  line: string;
  /** Fondo sólido para tooltips. */
  tooltip: string;
  /** Borde luminoso del vidrio (separadores). */
  edge: string;
  accent: string;
  sky: string;
  indigo: string;
  teal: string;
  /** Paleta categórica: familia de azules con índigo y turquesa para contraste. */
  palette: string[];
}

const PALE_BLUE = '#93c5fd';
const LILAC = '#a78bfa';

export function readTokens(): ChartTokens {
  const css = getComputedStyle(document.documentElement);
  const v = (name: string) => css.getPropertyValue(name).trim();
  const accent = v('--accent');
  const sky = v('--sky');
  const indigo = v('--indigo');
  const teal = v('--teal');
  return {
    ink: v('--ink'),
    muted: v('--muted'),
    line: v('--line'),
    tooltip: v('--tooltip'),
    edge: v('--glass-border'),
    accent,
    sky,
    indigo,
    teal,
    palette: [accent, sky, indigo, teal, PALE_BLUE, LILAC],
  };
}

/** Color fijo por previsión (se resuelve contra el tema activo). */
export const PREVISION_ROLES: Record<string, keyof ChartTokens> = { FONASA: 'accent', Isapre: 'sky' };

export const baseLayout = (t: ChartTokens): Partial<Layout> => ({
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Inter, Segoe UI, sans-serif', size: 13, color: t.ink },
  margin: { l: 8, r: 8, t: 24, b: 8 },
  colorway: t.palette,
  hoverlabel: { bgcolor: t.tooltip, bordercolor: t.line, font: { color: t.ink } },
  legend: { orientation: 'h', y: -0.28, x: 0, font: { size: 12, color: t.muted } },
  xaxis: {
    showgrid: false,
    zeroline: false,
    linecolor: t.line,
    tickfont: { color: t.muted },
    title: { font: { color: t.muted, size: 12 } },
    automargin: true,
  },
  yaxis: {
    gridcolor: t.line,
    zeroline: false,
    linecolor: 'rgba(0,0,0,0)',
    tickfont: { color: t.muted },
    title: { font: { color: t.muted, size: 12 } },
    automargin: true,
  },
});

export const baseConfig: Partial<Config> = { displayModeBar: false, responsive: true };
