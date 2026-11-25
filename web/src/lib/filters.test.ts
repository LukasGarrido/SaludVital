import { describe, expect, it } from 'vitest';
import { dataset } from './dataset';
import { ALL_FIELDS, applyFilters, countActive, defaultFilters, FILTER_OPTIONS, PERIODOS } from './filters';
import { CARTERA_FIELDS, DETALLE_FIELDS, except } from './chartFilterFields';

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

describe('filtros por gráfico', () => {
  it('cada gráfico parte sin filtros activos', () => {
    expect(countActive(defaultFilters(), ALL_FIELDS)).toBe(0);
  });

  it('cuenta período y listas con selección', () => {
    const f = { ...defaultFilters(), ...PERIODOS['Febrero 2026'], comunas: [FILTER_OPTIONS.comunas[0]], medicos: [] };
    expect(countActive(f, ALL_FIELDS)).toBe(2);
  });

  it('ignora filtros de campos que el gráfico no ofrece', () => {
    const f = { ...defaultFilters(), estados: ['Atendida'] };
    expect(countActive(f, except('estados'))).toBe(0);
    expect(countActive(f, DETALLE_FIELDS)).toBe(0);
    expect(countActive(f, CARTERA_FIELDS)).toBe(0);
  });

  it('dos gráficos con filtros distintos devuelven datos independientes', () => {
    const a = applyFilters(dataset, { ...defaultFilters(), ...PERIODOS['Enero 2026'] });
    const b = applyFilters(dataset, { ...defaultFilters(), ...PERIODOS['Febrero 2026'] });
    expect(a.reservas.length + b.reservas.length).toBeLessThanOrEqual(75);
    expect(a.reservas.length).not.toBe(b.reservas.length);
  });
});
