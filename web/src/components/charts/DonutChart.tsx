import { useMemo } from 'react';
import type { Data } from 'plotly.js-basic-dist-min';
import type { Entry } from '@/lib/aggregate';
import { type ChartTokens } from '@/lib/chartTheme';
import { useTokens } from '@/hooks/useTokens';
import PlotlyChart from './PlotlyChart';

interface Props {
  data: Entry[];
  /** Rol de color fijo por categoría (token del tema); las no listadas usan la paleta. */
  colors?: Record<string, keyof ChartTokens>;
  height?: number;
}

export default function DonutChart({ data, colors, height = 360 }: Props) {
  const t = useTokens();
  const traces = useMemo<Data[]>(
    () => [
      {
        type: 'pie',
        hole: 0.4,
        labels: data.map((d) => d.key),
        values: data.map((d) => d.value),
        textinfo: 'percent',
        textposition: 'inside',
        insidetextfont: { color: '#ffffff', size: 13 },
        marker: {
          colors: data.map((d, i) => {
            const role = colors?.[d.key];
            return (role ? (t[role] as string) : undefined) ?? t.palette[i % t.palette.length];
          }),
          line: { color: t.edge, width: 2 },
        },
        sort: false,
        hovertemplate: '%{label}: %{value} (%{percent})<extra></extra>',
      },
    ],
    [data, colors, t],
  );
  return <PlotlyChart data={traces} height={height} layout={{ showlegend: true }} />;
}
