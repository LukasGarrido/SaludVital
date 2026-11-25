import type { Config, Layout } from 'plotly.js-basic-dist-min';

/** Colores resueltos del tema activo (se leen de las variables CSS, única fuente de verdad). */
export interface ChartTokens {
  ink: string;
  muted: string;
  line: string;
  surface: string;
  accent: string;
  teal: string;
  amber: string;
  coral: string;
  violet: string;
  /** Paleta categórica: azul primero, luego colores de contraste. */
  palette: string[];
}

const SKY = '#38bdf8';

export function readTokens(): ChartTokens {
  const css = getComputedStyle(document.documentElement);
  const v = (name: string) => css.getPropertyValue(name).trim();
  const accent = v('--accent');
  const teal = v('--teal');
  const amber = v('--amber');
  const coral = v('--coral');
  const violet = v('--violet');
  return {
    ink: v('--ink'),
    muted: v('--muted'),
    line: v('--line'),
    surface: v('--surface'),
    accent,
    teal,
    amber,
    coral,
    violet,
    palette: [accent, amber, teal, coral, violet, SKY],
  };
}

/** Color fijo por previsión (se resuelve contra el tema activo). */
export const PREVISION_ROLES: Record<string, keyof ChartTokens> = { FONASA: 'accent', Isapre: 'amber' };

export const baseLayout = (t: ChartTokens): Partial<Layout> => ({
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Inter, Segoe UI, sans-serif', size: 13, color: t.ink },
  margin: { l: 8, r: 8, t: 24, b: 8 },
  colorway: t.palette,
  hoverlabel: { bgcolor: t.surface, bordercolor: t.line, font: { color: t.ink } },
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
