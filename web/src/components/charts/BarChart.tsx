import { useMemo } from 'react';
import type { Data } from 'plotly.js-basic-dist-min';
import type { Entry } from '@/lib/aggregate';
import { useTokens } from '@/hooks/useTokens';
import PlotlyChart from './PlotlyChart';

interface Props {
  data: Entry[];
  orientation?: 'v' | 'h';
  /** Formatea el valor mostrado sobre cada barra. */
  format?: (v: number) => string;
  xTitle?: string;
  yTitle?: string;
  height?: number;
  /** Color único para todas las barras (desactiva el destacado). */
  color?: string;
  /** Destaca la barra de mayor valor y atenúa las demás (por defecto sí). */
  highlightMax?: boolean;
}

/** Barras verticales u horizontales con etiqueta de valor. El orden de `data` es el orden visual. */
export default function BarChart({
  data,
  orientation = 'v',
  format = (v) => String(v),
  xTitle,
  yTitle,
  height,
  color,
  highlightMax = true,
}: Props) {
  const t = useTokens();
  const highlight = highlightMax && !color && data.length > 1;
  const maxIndex = highlight ? data.reduce((best, d, i, arr) => (d.value > arr[best].value ? i : best), 0) : undefined;
  const traces = useMemo<Data[]>(() => {
    const keys = data.map((d) => d.key);
    const values = data.map((d) => d.value);
    return [
      {
        type: 'bar',
        orientation,
        x: orientation === 'v' ? keys : values,
        y: orientation === 'v' ? values : keys,
        text: values.map(format),
        textposition: 'outside',
        cliponaxis: false,
        textfont: { color: t.ink, size: 12 },
        // cornerradius existe en plotly.js >= 3 pero aún no figura en los tipos
        marker: { color: highlight ? data.map((_, i) => (i === maxIndex ? t.accent : t.barDim)) : (color ?? t.accent), line: { width: 0 }, ...({ cornerradius: 8 } as object) },
        hovertemplate: orientation === 'v' ? '%{x}: %{text}<extra></extra>' : '%{y}: %{text}<extra></extra>',
      },
    ];
  }, [data, orientation, format, color, highlight, maxIndex, t]);

  const layout = useMemo(
    () => ({
      xaxis: { title: { text: xTitle } },
      yaxis: { title: { text: yTitle } },
      bargap: 0.25,
    }),
    [xTitle, yTitle],
  );

  return <PlotlyChart kind={orientation} highlightIndex={maxIndex} data={traces} layout={layout} height={height ?? (orientation === 'h' ? Math.max(260, data.length * 34 + 80) : 340)} />;
}
