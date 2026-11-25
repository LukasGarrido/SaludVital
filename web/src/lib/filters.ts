import { uniqueSorted } from './aggregate';
import { dataset } from './dataset';
import type { Dataset, Detalle, Paciente, Reserva } from './types';

export const MIN_DATE = '2026-01-05';
export const MAX_DATE = '2026-02-28';

export interface Periodo {
  desde: string;
  hasta: string;
}

export const PERIODOS: Record<string, Periodo> = {
  'Todo el período': { desde: MIN_DATE, hasta: MAX_DATE },
  'Enero 2026': { desde: '2026-01-05', hasta: '2026-01-31' },
  'Febrero 2026': { desde: '2026-02-01', hasta: '2026-02-28' },
  'Últimos 30 días': { desde: '2026-01-30', hasta: MAX_DATE },
};

/** Valores disponibles para cada filtro, derivados del modelo. */
export const FILTER_OPTIONS = {
  comunas: uniqueSorted(dataset.pacientes.map((p) => p.Comuna)),
  sexos: uniqueSorted(dataset.pacientes.map((p) => p.Sexo)),
  especialidades: uniqueSorted(dataset.reservas.map((r) => r.Especialidad)),
  medicos: uniqueSorted(dataset.reservas.map((r) => r.Medico)),
  estados: (['Atendida', 'No asistió', 'Cancelada', 'Pendiente'] as const).filter((e) =>
    dataset.reservas.some((r) => r.EstadoReserva === e),
  ) as string[],
  previsiones: uniqueSorted(dataset.reservas.map((r) => r.Prevision)),
  canales: uniqueSorted(dataset.reservas.map((r) => r.Canal)),
};

export interface FilterState extends Periodo {
  atajo: string;
  comunas: string[];
  sexos: string[];
  especialidades: string[];
  medicos: string[];
  estados: string[];
  previsiones: string[];
  canales: string[];
}

/** Campos de filtro que un gráfico puede ofrecer. `periodo` agrupa desde/hasta/atajo. */
export type FilterField =
  | 'periodo'
  | 'comunas'
  | 'sexos'
  | 'especialidades'
  | 'medicos'
  | 'estados'
  | 'previsiones'
  | 'canales';

export const ALL_FIELDS: FilterField[] = [
  'periodo',
  'comunas',
  'sexos',
  'especialidades',
  'medicos',
  'estados',
  'previsiones',
  'canales',
];

/** Cada gráfico parte sin filtros: período completo y listas vacías (vacío = todos). */
export const defaultFilters = (): FilterState => ({
  ...PERIODOS['Todo el período'],
  atajo: 'Todo el período',
  comunas: [],
  sexos: [],
  especialidades: [],
  medicos: [],
  estados: [],
  previsiones: [],
  canales: [],
});

export interface FilteredData {
  reservas: Reserva[];
  detalle: Detalle[];
  /** Cartera de pacientes: filtra solo por comuna y sexo, nunca por fecha. */
  cartera: Paciente[];
}

const inSel = (sel: string[], v: string | null) => sel.length === 0 || (v !== null && sel.includes(v));

/** Aplica los filtros globales a los hechos (misma semántica que app/app.py). */
export function applyFilters(ds: Dataset, f: FilterState): FilteredData {
  const fechaOk = (iso: string) => iso >= f.desde && iso <= f.hasta;

  const reservas = ds.reservas.filter(
    (r) =>
      fechaOk(r.FechaReserva) &&
      inSel(f.comunas, r.Comuna) &&
      inSel(f.sexos, r.Sexo) &&
      inSel(f.especialidades, r.Especialidad) &&
      inSel(f.medicos, r.Medico) &&
      inSel(f.previsiones, r.Prevision) &&
      inSel(f.estados, r.EstadoReserva) &&
      inSel(f.canales, r.Canal),
  );

  let detalle = ds.detalle.filter(
    (d) =>
      fechaOk(d.FechaAtencion) &&
      inSel(f.comunas, d.Comuna) &&
      inSel(f.sexos, d.Sexo) &&
      inSel(f.especialidades, d.Especialidad) &&
      inSel(f.medicos, d.Medico) &&
      inSel(f.previsiones, d.Prevision),
  );

  // Estado y canal solo existen en reservas: el detalle se acota a esas reservas.
  if (f.estados.length > 0 || f.canales.length > 0) {
    const ids = new Set(reservas.map((r) => r.ReservaID));
    detalle = detalle.filter((d) => d.ReservaID !== null && ids.has(d.ReservaID));
  }

  const cartera = ds.pacientes.filter((p) => inSel(f.comunas, p.Comuna) && inSel(f.sexos, p.Sexo));
  return { reservas, detalle, cartera };
}

/** Cantidad de filtros activos entre los campos que ofrece un gráfico (cada lista con selección cuenta 1). */
export function countActive(f: FilterState, fields: FilterField[]): number {
  const base = PERIODOS['Todo el período'];
  return fields.filter((field) =>
    field === 'periodo' ? f.desde !== base.desde || f.hasta !== base.hasta : f[field].length > 0,
  ).length;
}
