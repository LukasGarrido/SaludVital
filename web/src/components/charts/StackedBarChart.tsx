import { useMemo } from 'react';
import type { Data } from 'plotly.js-basic-dist-min';
import { COLORS, PALETTE } from '@/lib/chartTheme';
import PlotlyChart from './PlotlyChart';

export interface Series {
  name: string;
  values: number[];
}

interface Props {
  categories: string[];
  series: Series[];
  height?: number;
}

/** Barras horizontales apiladas (una serie por estado, una categoría por fila). */
export default function StackedBarChart({ categories, series, height }: Props) {
  const traces = useMemo<Data[]>(
    () =>
      series.map((s, i) => ({
        type: 'bar',
        orientation: 'h',
        name: s.name,
        y: categories,
        x: s.values,
        marker: { color: PALETTE[i % PALETTE.length], line: { color: COLORS.surface, width: 1 } },
        hovertemplate: '%{y} · ' + s.name + ': %{x}<extra></extra>',
      })),
    [categories, series],
  );
  return (
    <PlotlyChart
      data={traces}
      layout={{ barmode: 'stack', bargap: 0.25 }}
      height={height ?? Math.max(300, categories.length * 34 + 110)}
    />
  );
}
