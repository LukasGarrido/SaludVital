export interface SummaryItem {
  name: string;
  value: string;
  active: boolean;
}

/** Chips con el estado de cada filtro (activo = resaltado). */
export default function FilterSummary({ items }: { items: SummaryItem[] }) {
  return (
    <div className="filter-summary" aria-label="Filtros activos">
      {items.map((i) => (
        <span key={i.name} className={`fchip${i.active ? '' : ' fchip--off'}`}>
          {i.name}: {i.value}
        </span>
      ))}
    </div>
  );
}
