export const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
] as const;

/** Número de mes (1-12) de una fecha ISO yyyy-mm-dd. */
export const mesNum = (iso: string): number => Number(iso.slice(5, 7));

export const nombreMes = (n: number): string => MESES[n - 1] ?? String(n);

/** dd/mm a partir de una fecha ISO. */
export const ddmm = (iso: string): string => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;
