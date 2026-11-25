interface Props {
  label: string;
  options: string[];
  selected: string[];
  onChange: (next: string[]) => void;
}

/** Selector múltiple tipo chips (equivalente a st.pills). */
export default function ChipGroup({ label, options, selected, onChange }: Props) {
  const toggle = (o: string) =>
    onChange(selected.includes(o) ? selected.filter((s) => s !== o) : [...selected, o]);
  return (
    <div className="field" role="group" aria-label={label}>
      <span className="field__label">{label}</span>
      <div className="chips">
        {options.map((o) => (
          <button key={o} type="button" className="chip" aria-pressed={selected.includes(o)} onClick={() => toggle(o)}>
            {o}
          </button>
        ))}
      </div>
    </div>
  );
}
