import { useMemo } from 'react';
import type { Data } from 'plotly.js-basic-dist-min';
import type { Entry } from '@/lib/aggregate';
import { COLORS, PALETTE } from '@/lib/chartTheme';
import PlotlyChart from './PlotlyChart';

interface Props {
  data: Entry[];
  /** Color fijo por categoría; las no listadas usan la paleta. */
  colors?: Record<string, string>;
  height?: number;
}

export default function DonutChart({ data, colors, height = 360 }: Props) {
  const traces = useMemo<Data[]>(
    () => [
      {
        type: 'pie',
        hole: 0.4,
        labels: data.map((d) => d.key),
        values: data.map((d) => d.value),
        textinfo: 'label+percent',
        textfont: { color: COLORS.ink, size: 12 },
        marker: {
          colors: data.map((d, i) => colors?.[d.key] ?? PALETTE[i % PALETTE.length]),
          line: { color: COLORS.surface, width: 2 },
        },
        sort: false,
        hovertemplate: '%{label}: %{value} (%{percent})<extra></extra>',
      },
    ],
    [data, colors],
  );
  return <PlotlyChart data={traces} height={height} layout={{ showlegend: true }} />;
}
