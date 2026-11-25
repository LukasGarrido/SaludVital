import { useMemo, useState, type ReactNode } from 'react';

export interface Column<T> {
  header: string;
  /** Valor usado para ordenar; si falta, la columna no es ordenable. */
  sortValue?: (row: T) => number | string | null;
  render: (row: T) => ReactNode;
  align?: 'left' | 'right';
  /** Clase CSS opcional por celda (p. ej. colores de estado). */
  cellClass?: (row: T) => string | undefined;
}

interface Props<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  /** Orden inicial: índice de columna y dirección. */
  initialSort?: { col: number; dir: 'asc' | 'desc' };
}

/** Tabla con ordenamiento por columna. */
export default function DataTable<T>({ columns, rows, rowKey, initialSort }: Props<T>) {
  const [sort, setSort] = useState(initialSort ?? null);

  const sorted = useMemo(() => {
    const sv = sort ? columns[sort.col]?.sortValue : undefined;
    if (!sort || !sv) return rows;
    const dir = sort.dir === 'asc' ? 1 : -1;
    return [...rows].sort((a, b) => {
      const x = sv(a);
      const y = sv(b);
      if (x === y) return 0;
      if (x === null) return 1;
      if (y === null) return -1;
      return (x < y ? -1 : 1) * dir;
    });
  }, [rows, columns, sort]);

  const toggle = (i: number) =>
    setSort((s) => (s && s.col === i ? { col: i, dir: s.dir === 'asc' ? 'desc' : 'asc' } : { col: i, dir: 'desc' }));

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((c, i) => {
              const sortable = !!c.sortValue;
              const active = sort?.col === i;
              return (
                <th
                  key={c.header}
                  className={c.align === 'right' ? 'is-right' : undefined}
                  aria-sort={active ? (sort!.dir === 'asc' ? 'ascending' : 'descending') : undefined}
                >
                  {sortable ? (
                    <button type="button" className="table__sort" onClick={() => toggle(i)}>
                      {c.header}
                      <span aria-hidden="true">{active ? (sort!.dir === 'asc' ? ' ▲' : ' ▼') : ''}</span>
                    </button>
                  ) : (
                    c.header
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((c) => (
                <td key={c.header} className={[c.align === 'right' ? 'is-right' : '', c.cellClass?.(row) ?? ''].join(' ').trim() || undefined}>
                  {c.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
