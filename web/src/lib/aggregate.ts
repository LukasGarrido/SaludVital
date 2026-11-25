/** Helpers de agrupación genéricos (equivalentes a groupby de pandas). */

export function groupBy<T, K extends string | number>(rows: T[], key: (r: T) => K | null | undefined): Map<K, T[]> {
  const out = new Map<K, T[]>();
  for (const r of rows) {
    const k = key(r);
    if (k === null || k === undefined) continue;
    const arr = out.get(k);
    if (arr) arr.push(r);
    else out.set(k, [r]);
  }
  return out;
}

export interface Entry {
  key: string;
  value: number;
}

export function countBy<T>(rows: T[], key: (r: T) => string | null | undefined): Entry[] {
  return [...groupBy(rows, key)].map(([k, v]) => ({ key: k, value: v.length }));
}

export function sumBy<T>(
  rows: T[],
  key: (r: T) => string | null | undefined,
  val: (r: T) => number | null | undefined,
): Entry[] {
  return [...groupBy(rows, key)].map(([k, v]) => ({
    key: k,
    value: v.reduce((acc, r) => acc + (val(r) ?? 0), 0),
  }));
}

export const sortAsc = (e: Entry[]): Entry[] => [...e].sort((a, b) => a.value - b.value);
export const sortDesc = (e: Entry[]): Entry[] => [...e].sort((a, b) => b.value - a.value);

export const unique = <T>(xs: (T | null | undefined)[]): T[] =>
  [...new Set(xs.filter((x): x is T => x !== null && x !== undefined))];

export const uniqueSorted = (xs: (string | null | undefined)[]): string[] =>
  unique(xs).sort((a, b) => a.localeCompare(b, 'es'));
