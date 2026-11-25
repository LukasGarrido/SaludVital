import { mesNum } from './dates';
import { formatClp, formatPct } from './format';
import { calcularMedidas } from './measures';
import type { Detalle, Reserva } from './types';

export interface Prueba {
  indicador: string;
  esperado: string;
  obtenido: string;
  ok: boolean;
}

const near = (v: number | null, target: number, tol = 0.002) => v !== null && Math.abs(v - target) < tol;

/** Port de `ejecutar_pruebas_aceptacion`: valida los 16 indicadores sobre datos sin filtrar. */
export function ejecutarPruebasAceptacion(reservas: Reserva[], detalle: Detalle[]): Prueba[] {
  const m = calcularMedidas(reservas, detalle);
  const ingresosMes = (mes: number) =>
    detalle.filter((d) => mesNum(d.FechaAtencion) === mes).reduce((a, d) => a + (d.Importe ?? 0), 0);
  const ingEne = ingresosMes(1);
  const ingFeb = ingresosMes(2);
  const medicos = new Set(reservas.map((r) => r.MedicoID)).size;

  const entero = (indicador: string, esperado: number, obtenido: number): Prueba => ({
    indicador,
    esperado: String(esperado),
    obtenido: String(obtenido),
    ok: obtenido === esperado,
  });

  return [
    entero('Total Reservas', 75, m.TotalReservas),
    entero('Reservas Atendidas', 48, m.Atendidas),
    entero('Reservas No Asistió', 12, m.NoAsistio),
    entero('Reservas Canceladas', 10, m.Canceladas),
    entero('Reservas Pendientes', 5, m.Pendientes),
    {
      indicador: 'Tasa de Atención',
      esperado: '68,6 %',
      obtenido: formatPct(m.TasaAtencion),
      ok: near(m.TasaAtencion, 0.6857) || formatPct(m.TasaAtencion) === '68,6 %',
    },
    {
      indicador: 'Tasa de Inasistencia',
      esperado: '20,0 %',
      obtenido: formatPct(m.TasaInasistencia),
      ok: near(m.TasaInasistencia, 0.2),
    },
    {
      indicador: 'Tasa de Cancelación',
      esperado: '14,3 %',
      obtenido: formatPct(m.TasaCancelacion),
      ok: near(m.TasaCancelacion, 0.1428) || formatPct(m.TasaCancelacion) === '14,3 %',
    },
    entero('Atenciones Realizadas', 46, m.AtencionesRealizadas),
    entero('Detalles de Prestación', 41, detalle.length),
    { indicador: 'Ingresos Totales', esperado: '$1.671.000', obtenido: formatClp(m.Ingresos), ok: m.Ingresos === 1671000 },
    { indicador: 'Ingresos Enero', esperado: '$745.000', obtenido: formatClp(ingEne), ok: ingEne === 745000 },
    { indicador: 'Ingresos Febrero', esperado: '$926.000', obtenido: formatClp(ingFeb), ok: ingFeb === 926000 },
    {
      indicador: 'Ingreso Promedio por Atención',
      esperado: '$40.756',
      obtenido: formatClp(m.IngresoPromedio),
      ok: Math.round(m.IngresoPromedio ?? NaN) === 40756,
    },
    entero('Pacientes Distintos', 44, m.PacientesDistintos),
    entero('Médicos Activos', 14, medicos),
  ];
}
