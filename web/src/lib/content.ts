/** Textos editoriales del panel (conclusiones, recomendaciones y nota de alcance). */

export const NOTA_VISIBLE =
  'Datos simulados (no corresponden a la operación real de SaludVital). ' +
  'Cobertura: reservas del 05-01-2026 al 28-02-2026 (alrededor de 2 meses), lo que no permite evaluar estacionalidad. ' +
  'Los ingresos son valorizados, no cobrados. Canal y bloque horario existen solo desde el 04-02-2026 (51 % de las reservas), ' +
  'por lo que horas perdidas y utilización cubren ese subconjunto. Con menos de 10 reservas por canal o especialidad, ' +
  'las diferencias son indicativas. 34 filas fueron rechazadas por calidad de datos.';

export const CONCLUSIONES = [
  'De 70 reservas resueltas, 48 terminaron en atención (68,6 %). La inasistencia es 20,0 % y la cancelación 14,3 %.',
  'La inasistencia subió de 16,7 % en enero a 22,2 % en febrero. Con solo 2 meses de datos no se puede confirmar una tendencia.',
  'Se perdieron 5,0 horas por inasistencia, todas en febrero y solo en reservas con bloque horario (51 % del total).',
  'El Dr. Rodrigo Soto concentra 4 inasistencias en 6 reservas.',
  'Cardiología y Dermatología concentran la mayor demanda (11 reservas cada una). Dermatología lidera el ingreso valorizado ($363.000).',
  'Concepción concentra la mayor cantidad de atenciones (19). FONASA reúne 43 reservas e Isapre 32.',
  '27 de los 44 pacientes tienen una sola reserva.',
];

export const RECOMENDACIONES = [
  'Enviar recordatorios de cita (llamada o mensaje) 24 a 48 horas antes, priorizando los canales con más inasistencia (Teléfono y App) y las agendas más afectadas.',
  'Registrar canal y bloque horario en todas las reservas: hoy solo el 51 % los tiene.',
  'Cerrar las reservas pendientes de febrero con un seguimiento diario de recepción.',
  'Registrar las atenciones faltantes de 2 reservas atendidas y completar el valor unitario de 5 atenciones sin tarifa.',
  'Revisar las tarifas: 12 de 41 detalles tienen un valor distinto de la tarifa maestra.',
  'Contactar a los pacientes con una sola reserva para favorecer su retorno.',
  'Ampliar el período de datos antes de decidir cambios de dotación o de agenda.',
];
