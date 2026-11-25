import { useMemo } from 'react';
import type { Data } from 'plotly.js-basic-dist-min';
import type { Entry } from '@/lib/aggregate';
import { COLORS } from '@/lib/chartTheme';
import PlotlyChart from './PlotlyChart';

interface Props {
  data: Entry[];
  orientation?: 'v' | 'h';
  /** Formatea el valor mostrado sobre cada barra. */
  format?: (v: number) => string;
  xTitle?: string;
  yTitle?: string;
  height?: number;
  color?: string;
}

/** Barras verticales u horizontales con etiqueta de valor. El orden de `data` es el orden visual. */
export default function BarChart({
  data,
  orientation = 'v',
  format = (v) => String(v),
  xTitle,
  yTitle,
  height,
  color = COLORS.accent,
}: Props) {
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
        textfont: { color: COLORS.ink, size: 12 },
        marker: { color, line: { color: COLORS.surface, width: 2 } },
        hovertemplate: orientation === 'v' ? '%{x}: %{text}<extra></extra>' : '%{y}: %{text}<extra></extra>',
      },
    ];
  }, [data, orientation, format, color]);

  const layout = useMemo(
    () => ({
      xaxis: { title: { text: xTitle } },
      yaxis: { title: { text: yTitle } },
      bargap: 0.25,
    }),
    [xTitle, yTitle],
  );

  return <PlotlyChart data={traces} layout={layout} height={height ?? (orientation === 'h' ? Math.max(260, data.length * 34 + 80) : 340)} />;
}
