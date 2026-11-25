interface Props {
  label: string;
  options: string[];
  selected: string[];
  onChange: (next: string[]) => void;
  /** Texto de ayuda cuando no hay selección (equivale a "todos"). */
  placeholder?: string;
}

/** Lista de casillas con scroll, para filtros con muchas opciones (médicos, especialidades). */
export default function CheckList({ label, options, selected, onChange, placeholder = 'Todos' }: Props) {
  const toggle = (o: string) =>
    onChange(selected.includes(o) ? selected.filter((s) => s !== o) : [...selected, o]);
  return (
    <div className="field">
      <span className="field__label">
        {label} · {selected.length === 0 ? placeholder : `${selected.length} sel.`}
      </span>
      <div className="multi" role="group" aria-label={label}>
        {options.map((o) => (
          <label key={o}>
            <input type="checkbox" checked={selected.includes(o)} onChange={() => toggle(o)} />
            {o}
          </label>
        ))}
      </div>
    </div>
  );
}
