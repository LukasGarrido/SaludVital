export type EstadoReserva = 'Atendida' | 'No asistió' | 'Cancelada' | 'Pendiente';

export interface Reserva {
  ReservaID: string;
  FechaReserva: string; // ISO yyyy-mm-dd
  PacienteID: string;
  MedicoID: string;
  EstadoReserva: EstadoReserva;
  AtencionID: string | null;
  Canal: string | null;
  BloqueMinutos: number | null;
  Comuna: string | null;
  Prevision: string | null;
  Sexo: string | null;
  Medico: string | null;
  Especialidad: string | null;
}

export interface Detalle {
  DetalleID: string;
  AtencionID: string | null;
  ReservaID: string | null;
  FechaAtencion: string; // ISO yyyy-mm-dd
  PacienteID: string;
  MedicoID: string;
  Cantidad: number | null;
  ValorUnitario: number | null;
  Importe: number | null;
  Comuna: string | null;
  Prevision: string | null;
  Sexo: string | null;
  Medico: string | null;
  Especialidad: string | null;
  Prestacion: string | null;
}

export interface Paciente {
  PacienteID: string;
  Comuna: string | null;
  Sexo: string | null;
  'Reservas del Paciente': number;
  'Tramo Frecuencia': string;
  'Orden Tramo': number;
}

export interface Dataset {
  reservas: Reserva[];
  detalle: Detalle[];
  pacientes: Paciente[];
}

export interface Medidas {
  TotalReservas: number;
  Atendidas: number;
  NoAsistio: number;
  Canceladas: number;
  Pendientes: number;
  Resueltas: number;
  AtencionesRealizadas: number;
  TasaAtencion: number | null;
  TasaInasistencia: number | null;
  TasaCancelacion: number | null;
  PacientesDistintos: number;
  ReservasPorPaciente: number | null;
  PacientesCartera: number;
  Ingresos: number;
  IngresoPromedio: number | null;
  PrestacionesRealizadas: number;
  HorasPerdidas: number;
  CoberturaBloque: number;
}
