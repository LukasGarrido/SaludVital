import { useStore } from '@nanostores/react';
import { useMemo } from 'react';
import { dataset } from '@/lib/dataset';
import { applyFilters, type FilteredData } from '@/lib/filters';
import { calcularMedidas } from '@/lib/measures';
import type { Medidas } from '@/lib/types';
import { $filters } from '@/stores/filters';

export interface DashboardData extends FilteredData {
  medidas: Medidas;
}

/** Datos filtrados y medidas derivadas; se recalculan cuando cambia algún filtro. */
export function useFilteredData(): DashboardData {
  const filters = useStore($filters);
  return useMemo(() => {
    const data = applyFilters(dataset, filters);
    return { ...data, medidas: calcularMedidas(data.reservas, data.detalle, data.cartera) };
  }, [filters]);
}
