import { useMemo, useRef, type ReactNode } from 'react';
import { useChartFilters } from '@/hooks/useChartFilters';
import type { FilterField, FilteredData } from '@/lib/filters';
import FilterPopover from '../filters/FilterPopover';
import Empty from './Empty';

/** Hechos sobre los que opera el gráfico: define cuándo se considera "sin datos". */
export type Scope = 'reservas' | 'detalle' | 'cartera';

interface Props {
  /** Identificador único del gráfico: clave de su estado de filtros. */
  id: string;
  title: string;
  scope: Scope;
  /** Filtros que ofrece este gráfico. */
  fields: FilterField[];
  /** Dibuja el contenido con los datos filtrados de este gráfico. */
  render: (data: FilteredData) => ReactNode;
  emptyMessage?: string;
  className?: string;
}

/** Evita redibujar el gráfico (y su animación) cuando solo cambia estado del contenedor, como abrir el popover. */
function Body({ data, render }: { data: FilteredData; render: Props['render'] }) {
  const latest = useRef(render);
  latest.current = render;
  return useMemo(() => latest.current(data), [data]);
}

/** Tarjeta de gráfico con filtros propios en la cabecera. */
export default function FilterableCard({ id, title, scope, fields, render, emptyMessage, className = '' }: Props) {
  const state = useChartFilters(id, fields);
  const empty = state.data[scope].length === 0;

  return (
    <section className={`card ${className}`.trim()}>
      <header className="card__head">
        <h3 className="card__title">{title}</h3>
        <FilterPopover fields={fields} state={state} label={title} />
      </header>
      {empty ? <Empty message={emptyMessage ?? 'Ningún dato coincide con los filtros de este gráfico.'} /> : <Body data={state.data} render={render} />}
    </section>
  );
}
