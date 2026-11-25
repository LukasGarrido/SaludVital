import { useMemo } from 'react';
import { useChartFilters } from '@/hooks/useChartFilters';
import { calcularMedidas } from '@/lib/measures';
import type { FilterField } from '@/lib/filters';
import type { Medidas } from '@/lib/types';
import FilterPopover from '../filters/FilterPopover';
import KpiGrid, { type Kpi } from './KpiGrid';

interface Props {
  id: string;
  title?: string;
  fields: FilterField[];
  columns?: 2 | 3 | 4;
  /** Construye los indicadores a partir de las medidas calculadas con los filtros de este grupo. */
  build: (m: Medidas) => Kpi[];
}

/** Grupo de KPI con un único filtro propio, alineado a la derecha sobre las tarjetas. */
export default function FilterableKpis({ id, title = 'Indicadores', fields, columns = 4, build }: Props) {
  const state = useChartFilters(id, fields);
  const { reservas, detalle, cartera } = state.data;
  const medidas = useMemo(() => calcularMedidas(reservas, detalle, cartera), [reservas, detalle, cartera]);
  const items = useMemo(() => build(medidas), [medidas, build]);

  return (
    <div className="kpi-section">
      <div className="kpi-bar">
        <span className="kpi-bar__title">{title}</span>
        <FilterPopover fields={fields} state={state} label={title} />
      </div>
      <KpiGrid items={items} columns={columns} />
    </div>
  );
}
