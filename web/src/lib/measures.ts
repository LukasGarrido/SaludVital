import type { Detalle, Medidas, Paciente, Reserva } from './types';

const distinct = (xs: (string | null)[]): number =>
  new Set(xs.filter((x): x is string => x !== null && x !== '')).size;

const ratio = (num: number, den: number): number | null => (den > 0 ? num / den : null);

const sum = (xs: (number | null)[]): number => xs.reduce<number>((a, x) => a + (x ?? 0), 0);

/**
 * Port de `calcular_medidas` (app/medidas.py): todas las medidas del modelo
 * calculadas sobre los hechos ya filtrados.
 */
export function calcularMedidas(
  reservas: Reserva[],
  detalle: Detalle[],
  cartera?: Paciente[],
): Medidas {
  const total = reservas.length;
  const count = (estado: Reserva['EstadoReserva']) => reservas.filter((r) => r.EstadoReserva === estado).length;

  const atendidas = count('Atendida');
  const noAsistio = count('No asistió');
  const canceladas = count('Cancelada');
  const pendientes = count('Pendiente');
  const resueltas = atendidas + noAsistio + canceladas;

  const pacientesDistintos = distinct(reservas.map((r) => r.PacienteID));
  const ingresos = sum(detalle.map((d) => d.Importe));
  const atencionesDetalle = distinct(detalle.map((d) => d.AtencionID));

  const minutosPerdidos = sum(
    reservas.filter((r) => r.EstadoReserva === 'No asistió').map((r) => r.BloqueMinutos),
  );
  const conBloque = reservas.filter((r) => r.BloqueMinutos !== null).length;

  return {
    TotalReservas: total,
    Atendidas: atendidas,
    NoAsistio: noAsistio,
    Canceladas: canceladas,
    Pendientes: pendientes,
    Resueltas: resueltas,
    AtencionesRealizadas: distinct(reservas.map((r) => r.AtencionID)),
    TasaAtencion: ratio(atendidas, resueltas),
    TasaInasistencia: ratio(noAsistio, atendidas + noAsistio),
    TasaCancelacion: ratio(canceladas, resueltas),
    PacientesDistintos: pacientesDistintos,
    ReservasPorPaciente: ratio(total, pacientesDistintos),
    PacientesCartera: cartera && cartera.length > 0 ? distinct(cartera.map((p) => p.PacienteID)) : pacientesDistintos,
    Ingresos: ingresos,
    IngresoPromedio: ratio(ingresos, atencionesDetalle),
    PrestacionesRealizadas: sum(detalle.map((d) => d.Cantidad)),
    HorasPerdidas: minutosPerdidos / 60,
    CoberturaBloque: total > 0 ? conBloque / total : 0,
  };
}
