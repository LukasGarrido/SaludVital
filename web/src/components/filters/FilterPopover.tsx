import { useEffect, useId, useRef, useState } from 'react';
import type { ChartFilters } from '@/hooks/useChartFilters';
import { FILTER_OPTIONS as O, PERIODOS, type FilterField } from '@/lib/filters';
import SvgIcon from '../ui/SvgIcon';
import CheckList from './CheckList';
import ChipGroup from './ChipGroup';
import DateRange from './DateRange';

interface Props {
  /** Campos que este gráfico ofrece (cada gráfico define los suyos). */
  fields: FilterField[];
  state: ChartFilters;
  /** Nombre accesible del gráfico filtrado. */
  label: string;
}

const has = (fields: FilterField[], f: FilterField) => fields.includes(f);

/**
 * Botón "Filtros" con popover de vidrio. Se muestra en la cabecera de cada gráfico y solo
 * contiene los controles que aplican a ese gráfico. Un contador indica cuántos filtros hay activos.
 */
export default function FilterPopover({ fields, state, label }: Props) {
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const panelId = useId();
  const { filters: f, patch, setAtajo, reset, activeCount } = state;

  // Cierra con clic fuera o con Escape
  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (root.current && !root.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false);
    document.addEventListener('pointerdown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <div className="filter-pop" ref={root} data-open={open}>
      <button
        type="button"
        className="filter-btn"
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={`Filtros de ${label}${activeCount ? `, ${activeCount} activos` : ''}`}
        data-active={activeCount > 0}
        onClick={() => setOpen((o) => !o)}
      >
        <SvgIcon name="filtros" size={15} />
        <span>Filtros</span>
        {activeCount > 0 && <b className="filter-btn__badge">{activeCount}</b>}
      </button>

      {open && (
        <div className="filter-pop__panel" id={panelId} role="dialog" aria-label={`Filtros de ${label}`}>
          <div className="filters">
            {has(fields, 'periodo') && (
              <>
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
                  onChange={(desde, hasta) => patch({ desde, hasta, atajo: 'Personalizado' })}
                />
              </>
            )}
            {has(fields, 'comunas') && <ChipGroup label="Comuna" options={O.comunas} selected={f.comunas} onChange={(comunas) => patch({ comunas })} />}
            {has(fields, 'sexos') && <ChipGroup label="Sexo" options={O.sexos} selected={f.sexos} onChange={(sexos) => patch({ sexos })} />}
            {has(fields, 'previsiones') && <ChipGroup label="Previsión" options={O.previsiones} selected={f.previsiones} onChange={(previsiones) => patch({ previsiones })} />}
            {has(fields, 'estados') && <ChipGroup label="Estado de la reserva" options={O.estados} selected={f.estados} onChange={(estados) => patch({ estados })} />}
            {has(fields, 'canales') && <ChipGroup label="Canal" options={O.canales} selected={f.canales} onChange={(canales) => patch({ canales })} />}
            {has(fields, 'especialidades') && <CheckList label="Especialidad" options={O.especialidades} selected={f.especialidades} onChange={(especialidades) => patch({ especialidades })} placeholder="Todas" />}
            {has(fields, 'medicos') && <CheckList label="Médico" options={O.medicos} selected={f.medicos} onChange={(medicos) => patch({ medicos })} />}
          </div>
          <div className="filter-pop__foot">
            <button type="button" className="btn" onClick={reset} disabled={activeCount === 0}>
              Limpiar filtros
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
