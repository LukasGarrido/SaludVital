import { ALL_FIELDS, type FilterField } from './filters';

/** Todos los campos excepto los indicados (el filtro de la dimensión que el gráfico ya muestra no aporta). */
export const except = (...omit: FilterField[]): FilterField[] => ALL_FIELDS.filter((f) => !omit.includes(f));

/** Campos válidos para los hechos de detalle (ingresos): estado y canal solo existen en reservas. */
export const DETALLE_FIELDS: FilterField[] = ['periodo', 'comunas', 'sexos', 'especialidades', 'medicos', 'previsiones'];

/** La cartera de pacientes solo responde a comuna y sexo (nunca a la fecha). */
export const CARTERA_FIELDS: FilterField[] = ['comunas', 'sexos'];

export { ALL_FIELDS };
