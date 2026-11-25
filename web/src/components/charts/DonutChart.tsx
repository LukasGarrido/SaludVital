import { useMemo } from 'react';
import type { Data } from 'plotly.js-basic-dist-min';
import type { Entry } from '@/lib/aggregate';
import { type ChartTokens } from '@/lib/chartTheme';
import { useTokens } from '@/hooks/useTokens';
import { formatNum } from '@/lib/format';
import PlotlyChart from './PlotlyChart';

interface Props {
  data: Entry[];
  /** Rol de color fijo por categoría (token del tema); las no listadas usan la paleta. */
  colors?: Record<string, keyof ChartTokens>;
  height?: number;
  /** Formatea el total mostrado al centro. */
  format?: (v: number) => string;
}

export default function DonutChart({ data, colors, height = 360, format = formatNum }: Props) {
  const t = useTokens();
  const traces = useMemo<Data[]>(
    () => [
      {
        type: 'pie',
        hole: 0.64,
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
          line: { color: t.edge, width: 3 },
        },
        sort: false,
        hovertemplate: '%{label}: %{value} (%{percent})<extra></extra>',
      },
    ],
    [data, colors, t],
  );
  const total = useMemo(() => data.reduce((a, d) => a + d.value, 0), [data]);
  const layout = useMemo(
    () => ({
      showlegend: true,
      annotations: [
        {
          text: `<b>${format(total)}</b><br><span style="font-size:11px">total</span>`,
          showarrow: false,
          x: 0.5,
          y: 0.5,
          xref: 'paper' as const,
          yref: 'paper' as const,
          font: { size: 22, color: t.ink },
        },
      ],
    }),
    [total, format, t],
  );
  return <PlotlyChart kind="pie" data={traces} height={height} layout={layout} />;
}
