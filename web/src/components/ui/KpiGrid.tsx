import KpiCard from './KpiCard';

export interface Kpi {
  label: string;
  value: string;
}

interface Props {
  items: Kpi[];
  /** Columnas en escritorio. */
  columns?: 2 | 3 | 4;
}

export default function KpiGrid({ items, columns = 4 }: Props) {
  return (
    <div className={`kpi-grid kpi-grid--${columns}`}>
      {items.map((k) => (
        <KpiCard key={k.label} {...k} />
      ))}
    </div>
  );
}
