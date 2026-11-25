import { describe, expect, it } from 'vitest';
import { dataset } from './dataset';
import { applyFilters, defaultFilters, FILTER_OPTIONS, PERIODOS } from './filters';

describe('applyFilters', () => {
  it('sin filtros devuelve todo el modelo', () => {
    const r = applyFilters(dataset, defaultFilters());
    expect(r.reservas).toHaveLength(75);
    expect(r.detalle).toHaveLength(41);
  });

  it('filtra por período', () => {
    const r = applyFilters(dataset, { ...defaultFilters(), ...PERIODOS['Febrero 2026'] });
    expect(r.reservas.every((x) => x.FechaReserva >= '2026-02-01')).toBe(true);
    expect(r.reservas.length).toBeLessThan(75);
  });

  it('filtra por especialidad y acota el detalle', () => {
    const esp = FILTER_OPTIONS.especialidades[0];
    const r = applyFilters(dataset, { ...defaultFilters(), especialidades: [esp] });
    expect(r.reservas.every((x) => x.Especialidad === esp)).toBe(true);
    expect(r.detalle.every((x) => x.Especialidad === esp)).toBe(true);
  });

  it('estado acota el detalle a las reservas seleccionadas', () => {
    const r = applyFilters(dataset, { ...defaultFilters(), estados: ['No asistió'] });
    expect(r.reservas).toHaveLength(12);
    expect(r.detalle).toHaveLength(0);
  });

  it('la cartera ignora la fecha', () => {
    const todo = applyFilters(dataset, defaultFilters()).cartera.length;
    const feb = applyFilters(dataset, { ...defaultFilters(), ...PERIODOS['Febrero 2026'] }).cartera.length;
    expect(feb).toBe(todo);
  });
});
