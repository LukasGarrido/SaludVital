/** Formateadores es-CL: miles con punto y decimales con coma. */
const isNil = (v: number | null | undefined): v is null | undefined =>
  v === null || v === undefined || Number.isNaN(v);

const miles = (n: number) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

export const formatNum = (v: number | null | undefined): string => (isNil(v) ? '—' : miles(v));

export const formatClp = (v: number | null | undefined): string => (isNil(v) ? '—' : `$${miles(v)}`);

export const formatPct = (v: number | null | undefined): string =>
  isNil(v) ? '—' : `${(v * 100).toFixed(1).replace('.', ',')} %`;

export const formatDec = (v: number | null | undefined, digits = 1): string =>
  isNil(v) ? '—' : v.toFixed(digits).replace('.', ',');
