import { useStore } from '@nanostores/react';
import { dataset } from '@/lib/dataset';
import { ddmm } from '@/lib/dates';
import { filtroActivo, FILTER_OPTIONS as O, PERIODOS } from '@/lib/filters';
import { formatNum } from '@/lib/format';
import { useFilteredData } from '@/hooks/useFilteredData';
import { $filters, patchFilters, resetFilters, setAtajo } from '@/stores/filters';
import ChipGroup from './ChipGroup';
import CheckList from './CheckList';
import DateRange from './DateRange';
import FilterSummary, { type SummaryItem } from './FilterSummary';

/** Panel de filtros globales (isla de la barra lateral). Su estado vive en el store compartido. */
export default function FilterPanel() {
  const f = useStore($filters);
  const { reservas } = useFilteredData();

  const summary: SummaryItem[] = [
    { name: 'Período', value: `${ddmm(f.desde)} – ${ddmm(f.hasta)}`, active: true },
    { name: 'Comuna', value: `${f.comunas.length}/${O.comunas.length}`, active: filtroActivo(f.comunas, O.comunas.length) },
    { name: 'Sexo', value: `${f.sexos.length}/${O.sexos.length}`, active: filtroActivo(f.sexos, O.sexos.length) },
    { name: 'Especialidad', value: String(f.especialidades.length), active: f.especialidades.length > 0 },
    { name: 'Médico', value: String(f.medicos.length), active: f.medicos.length > 0 },
    { name: 'Estado', value: String(f.estados.length), active: f.estados.length > 0 },
    { name: 'Previsión', value: String(f.previsiones.length), active: f.previsiones.length > 0 },
    { name: 'Canal', value: String(f.canales.length), active: f.canales.length > 0 },
  ];

  return (
    <div className="filters">
      <div className="side-title">Filtros globales</div>
      <button type="button" className="btn" onClick={resetFilters}>
        Limpiar filtros
      </button>

      <label className="field">
        <span className="field__label">Atajo de período</span>
        <select className="select" value={f.atajo} onChange={(e) => setAtajo(e.target.value)}>
          {Object.keys(PERIODOS).map((p) => (
            <option key={p}>{p}</option>
          ))}
          {!(f.atajo in PERIODOS) && <option>{f.atajo}</option>}
        </select>
      </label>

      <DateRange
        desde={f.desde}
        hasta={f.hasta}
        min="2026-01-01"
        max="2026-12-31"
        onChange={(desde, hasta) => patchFilters({ desde, hasta, atajo: 'Personalizado' })}
      />

      <ChipGroup label="Comuna" options={O.comunas} selected={f.comunas} onChange={(comunas) => patchFilters({ comunas })} />
      <ChipGroup label="Sexo" options={O.sexos} selected={f.sexos} onChange={(sexos) => patchFilters({ sexos })} />

      <details className="adv">
        <summary>Filtros avanzados</summary>
        <div className="filters">
          <CheckList label="Especialidad" options={O.especialidades} selected={f.especialidades} onChange={(especialidades) => patchFilters({ especialidades })} placeholder="Todas" />
          <CheckList label="Médico" options={O.medicos} selected={f.medicos} onChange={(medicos) => patchFilters({ medicos })} />
          <ChipGroup label="Estado de la reserva" options={O.estados} selected={f.estados} onChange={(estados) => patchFilters({ estados })} />
          <ChipGroup label="Previsión" options={O.previsiones} selected={f.previsiones} onChange={(previsiones) => patchFilters({ previsiones })} />
          <CheckList label="Canal" options={O.canales} selected={f.canales} onChange={(canales) => patchFilters({ canales })} />
        </div>
      </details>

      <FilterSummary items={summary} />
      <div className="count-card">
        <b>
          {formatNum(reservas.length)} <small>/ {formatNum(dataset.reservas.length)}</small>
        </b>
        <span>reservas visibles</span>
      </div>
      {reservas.length === 0 && <p className="warn-inline">Ninguna reserva coincide con los filtros.</p>}
    </div>
  );
}
