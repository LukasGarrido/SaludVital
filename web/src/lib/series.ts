import { groupBy } from './aggregate';
import { mesNum, nombreMes } from './dates';

export interface MesGrupo<T> {
  mes: number;
  nombre: string;
  rows: T[];
}

/** Agrupa filas por mes calendario (ordenado de enero a diciembre). */
export function porMes<T>(rows: T[], fecha: (r: T) => string): MesGrupo<T>[] {
  return [...groupBy(rows, (r) => mesNum(fecha(r)))]
    .sort((a, b) => a[0] - b[0])
    .map(([mes, grupo]) => ({ mes, nombre: nombreMes(mes), rows: grupo }));
}
