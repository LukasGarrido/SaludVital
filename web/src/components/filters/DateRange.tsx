interface Props {
  desde: string;
  hasta: string;
  min: string;
  max: string;
  onChange: (desde: string, hasta: string) => void;
}

/** Rango de fechas con dos campos nativos; mantiene desde <= hasta. */
export default function DateRange({ desde, hasta, min, max, onChange }: Props) {
  return (
    <div className="field">
      <span className="field__label">Rango de fechas</span>
      <div className="date-range">
        <input
          className="input"
          type="date"
          aria-label="Desde"
          value={desde}
          min={min}
          max={hasta}
          onChange={(e) => e.target.value && onChange(e.target.value, hasta)}
        />
        <input
          className="input"
          type="date"
          aria-label="Hasta"
          value={hasta}
          min={desde}
          max={max}
          onChange={(e) => e.target.value && onChange(desde, e.target.value)}
        />
      </div>
    </div>
  );
}
