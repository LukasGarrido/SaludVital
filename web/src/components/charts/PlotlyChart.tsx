import { useEffect, useRef } from 'react';
import type { Data, Layout } from 'plotly.js-basic-dist-min';
import { baseConfig, baseLayout, type ChartTokens } from '@/lib/chartTheme';
import { useTokens } from '@/hooks/useTokens';

interface Props {
  data: Data[];
  layout?: Partial<Layout>;
  height?: number;
}

/** Fusión superficial por eje para no perder el tema base al personalizar. */
function mergeLayout(tokens: ChartTokens, extra: Partial<Layout> = {}): Partial<Layout> {
  const base = baseLayout(tokens);
  return {
    ...base,
    ...extra,
    xaxis: { ...base.xaxis, ...extra.xaxis },
    yaxis: { ...base.yaxis, ...extra.yaxis },
    margin: { ...base.margin, ...extra.margin },
    legend: { ...base.legend, ...extra.legend },
  };
}

/**
 * Wrapper mínimo sobre Plotly. La librería se importa de forma diferida
 * (solo en el cliente) para mantener liviana la carga inicial.
 */
export default function PlotlyChart({ data, layout, height = 340 }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const tokens = useTokens();

  useEffect(() => {
    let cancelled = false;
    const el = ref.current;
    if (!el) return;
    import('plotly.js-basic-dist-min').then((mod) => {
      if (cancelled) return;
      const Plotly = mod.default;
      Plotly.react(el, data, { ...mergeLayout(tokens, layout), height, autosize: true }, baseConfig);
    });
    return () => {
      cancelled = true;
    };
  }, [data, layout, height, tokens]);

  useEffect(() => {
    const el = ref.current;
    return () => {
      if (el) import('plotly.js-basic-dist-min').then((m) => m.default.purge(el));
    };
  }, []);

  return <div ref={ref} className="chart" style={{ height }} />;
}
