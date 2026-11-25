import type { Config, Layout } from 'plotly.js-basic-dist-min';

export const COLORS = {
  accent: '#E05A6D',
  teal: '#4FB3A8',
  ink: '#E8EEF0',
  muted: '#8DA2A8',
  line: '#223038',
  grid: '#1A262D',
  surface: '#131C21',
};

/** Paleta categórica (misma que el panel de Streamlit). */
export const PALETTE = ['#E05A6D', '#4FB3A8', '#3B82F6', '#F59E0B', '#10B981', '#8B5CF6', '#EC4899'];

/** Colores fijos por previsión. */
export const PREVISION_COLORS: Record<string, string> = { FONASA: COLORS.teal, Isapre: COLORS.accent };

export const baseLayout = (): Partial<Layout> => ({
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Figtree, Segoe UI, sans-serif', size: 13, color: COLORS.ink },
  margin: { l: 8, r: 8, t: 24, b: 8 },
  colorway: PALETTE,
  hoverlabel: { bgcolor: '#1B2830', bordercolor: COLORS.line, font: { color: '#FFFFFF' } },
  legend: { orientation: 'h', y: -0.28, x: 0, font: { size: 12, color: COLORS.muted } },
  xaxis: {
    showgrid: false,
    zeroline: false,
    linecolor: COLORS.line,
    tickfont: { color: COLORS.muted },
    title: { font: { color: COLORS.muted, size: 12 } },
    automargin: true,
  },
  yaxis: {
    gridcolor: COLORS.grid,
    zeroline: false,
    linecolor: 'rgba(0,0,0,0)',
    tickfont: { color: COLORS.muted },
    title: { font: { color: COLORS.muted, size: 12 } },
    automargin: true,
  },
});

export const baseConfig: Partial<Config> = { displayModeBar: false, responsive: true };
