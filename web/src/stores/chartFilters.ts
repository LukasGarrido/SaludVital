import { map } from 'nanostores';
import { defaultFilters, type FilterState } from '@/lib/filters';

const KEY = 'saludvital:filtros-grafico';

function load(): Record<string, FilterState> {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Record<string, FilterState>) : {};
  } catch {
    return {};
  }
}

/** Filtros de cada gráfico, indexados por id; se recuerdan entre visitas. */
export const $chartFilters = map<Record<string, FilterState>>(load());

$chartFilters.listen((value) => {
  try {
    localStorage.setItem(KEY, JSON.stringify(value));
  } catch {
    /* almacenamiento no disponible: se ignora */
  }
});

/** Estado inicial compartido (referencia estable para no re-renderizar gráficos sin filtros). */
export const DEFAULT_FILTERS: FilterState = defaultFilters();

export const patchChartFilters = (id: string, patch: Partial<FilterState>) =>
  $chartFilters.setKey(id, { ...($chartFilters.get()[id] ?? DEFAULT_FILTERS), ...patch });

export const resetChartFilters = (id: string) => $chartFilters.setKey(id, DEFAULT_FILTERS);
