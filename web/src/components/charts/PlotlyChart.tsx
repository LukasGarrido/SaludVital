import { useEffect, useRef } from 'react';
import type { Data, Layout } from 'plotly.js-basic-dist-min';
import { baseConfig, baseLayout, type ChartTokens } from '@/lib/chartTheme';
import { useTokens } from '@/hooks/useTokens';

/** Tipo de gráfico: define la animación de entrada en CSS (barras verticales, horizontales o circular). */
export type ChartKind = 'v' | 'h' | 'pie';

interface Props {
  data: Data[];
  layout?: Partial<Layout>;
  height?: number;
  kind?: ChartKind;
  /** Índice de la barra destacada (recibe un resplandor). */
  highlightIndex?: number;
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
export default function PlotlyChart({ data, layout, height = 340, kind = 'v', highlightIndex }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const tokens = useTokens();

  useEffect(() => {
    let cancelled = false;
    const el = ref.current;
    if (!el) return;
    import('plotly.js-basic-dist-min').then((mod) => {
      if (cancelled) return;
      const Plotly = mod.default;
      // `transition` anima los cambios de datos al filtrar (Plotly.react los interpola)
      const full = { ...mergeLayout(tokens, layout), height, autosize: true, transition: { duration: 550, easing: 'cubic-in-out' } };
      Promise.resolve(Plotly.react(el, data, full as Partial<Layout>, baseConfig)).then(() => {
        if (cancelled || highlightIndex === undefined) return;
        el.querySelectorAll('.barlayer .point').forEach((p, i) => p.classList.toggle('is-hi', i === highlightIndex));
      });
    });
    return () => {
      cancelled = true;
    };
  }, [data, layout, height, tokens, highlightIndex]);

  useEffect(() => {
    const el = ref.current;
    return () => {
      if (el) import('plotly.js-basic-dist-min').then((m) => m.default.purge(el));
    };
  }, []);

  return <div ref={ref} className="chart" data-kind={kind} style={{ height }} />;
}
