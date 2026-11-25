import { atom } from 'nanostores';
import { defaultFilters, PERIODOS, type FilterState } from '@/lib/filters';

const STORAGE_KEY = 'saludvital:filtros';

function load(): FilterState {
  const base = defaultFilters();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? { ...base, ...(JSON.parse(raw) as Partial<FilterState>) } : base;
  } catch {
    return base;
  }
}

/** Estado global de filtros, compartido por todas las páginas y persistido en el navegador. */
export const $filters = atom<FilterState>(load());

$filters.listen((value) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  } catch {
    /* almacenamiento no disponible: se ignora */
  }
});

export const patchFilters = (patch: Partial<FilterState>) => $filters.set({ ...$filters.get(), ...patch });

export const resetFilters = () => $filters.set(defaultFilters());

export const setAtajo = (nombre: string) => {
  const p = PERIODOS[nombre];
  if (p) patchFilters({ atajo: nombre, ...p });
};
