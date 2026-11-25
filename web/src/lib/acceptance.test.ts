import { describe, expect, it } from 'vitest';
import { ejecutarPruebasAceptacion } from './acceptance';
import { dataset } from './dataset';
import { formatClp, formatNum, formatPct } from './format';

describe('pruebas de aceptación (paridad con Streamlit)', () => {
  const pruebas = ejecutarPruebasAceptacion(dataset.reservas, dataset.detalle);

  it('evalúa los 16 indicadores', () => {
    expect(pruebas).toHaveLength(16);
  });

  it.each(pruebas.map((p) => [p.indicador, p] as const))('%s', (_n, p) => {
    expect(p.ok, `${p.indicador}: esperado ${p.esperado}, obtenido ${p.obtenido}`).toBe(true);
  });
});

describe('formateadores es-CL', () => {
  it('formatea números, CLP y porcentajes', () => {
    expect(formatNum(1234567)).toBe('1.234.567');
    expect(formatClp(1671000)).toBe('$1.671.000');
    expect(formatPct(0.6857)).toBe('68,6 %');
    expect(formatPct(null)).toBe('—');
  });
});
