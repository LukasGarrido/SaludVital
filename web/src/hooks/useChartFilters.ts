import { useStore } from '@nanostores/react';
import { useCallback, useMemo } from 'react';
import { dataset } from '@/lib/dataset';
import { applyFilters, countActive, PERIODOS, type FilterField, type FilteredData, type FilterState } from '@/lib/filters';
import { $chartFilters, DEFAULT_FILTERS, patchChartFilters, resetChartFilters } from '@/stores/chartFilters';

export interface ChartFilters {
  filters: FilterState;
  /** Datos del modelo ya filtrados con los filtros propios de este gráfico. */
  data: FilteredData;
  activeCount: number;
  patch: (patch: Partial<FilterState>) => void;
  setAtajo: (nombre: string) => void;
  reset: () => void;
}

/** Filtros independientes de un gráfico (identificado por `id`) y los datos resultantes. */
export function useChartFilters(id: string, fields: FilterField[]): ChartFilters {
  const all = useStore($chartFilters, { keys: [id] });
  const filters = all[id] ?? DEFAULT_FILTERS;

  const data = useMemo(() => applyFilters(dataset, filters), [filters]);
  const patch = useCallback((p: Partial<FilterState>) => patchChartFilters(id, p), [id]);
  const reset = useCallback(() => resetChartFilters(id), [id]);
  const setAtajo = useCallback(
    (nombre: string) => {
      const p = PERIODOS[nombre];
      if (p) patchChartFilters(id, { atajo: nombre, ...p });
    },
    [id],
  );

  return { filters, data, activeCount: countActive(filters, fields), patch, setAtajo, reset };
}
