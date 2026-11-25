import { countBy, groupBy, sortAsc, uniqueSorted, type Entry } from '@/lib/aggregate';
import { except } from '@/lib/chartFilterFields';
import { NOTA_VISIBLE } from '@/lib/content';
import type { FilteredData } from '@/lib/filters';
import { formatClp, formatDec, formatPct } from '@/lib/format';
import { calcularMedidas } from '@/lib/measures';
import { porMes } from '@/lib/series';
import BarChart from '../charts/BarChart';
import StackedBarChart from '../charts/StackedBarChart';
import DataTable, { type Column } from '../ui/DataTable';
import FilterableCard from '../ui/FilterableCard';
import Grid from '../ui/Grid';
import Note from '../ui/Note';

interface FilaMedico {
  medico: string;
  total: number;
  atendidas: number;
  noAsistio: number;
  canceladas: number;
  pendientes: number;
  tasaAtencion: number | null;
  ingresos: number;
  ingresoPromedio: number | null;
}

const ESTADOS = ['Atendida', 'No asistió', 'Cancelada', 'Pendiente'];

/** Rojo bajo 50 % de atención, verde en caso contrario (igual que Streamlit). */
const claseTasa = (v: number | null) => (v === null ? undefined : v < 0.5 ? 'cell-bad' : 'cell-ok');

const COLUMNAS: Column<FilaMedico>[] = [
  { header: 'Médico', sortValue: (r) => r.medico, render: (r) => r.medico },
  { header: 'Total Reservas', align: 'right', sortValue: (r) => r.total, render: (r) => r.total },
  { header: 'Reservas Atendidas', align: 'right', sortValue: (r) => r.atendidas, render: (r) => r.atendidas },
  { header: 'Reservas No Asistió', align: 'right', sortValue: (r) => r.noAsistio, render: (r) => r.noAsistio },
  { header: 'Reservas Canceladas', align: 'right', sortValue: (r) => r.canceladas, render: (r) => r.canceladas },
  { header: 'Reservas Pendientes', align: 'right', sortValue: (r) => r.pendientes, render: (r) => r.pendientes },
  {
    header: 'Tasa de Atención',
    align: 'right',
    sortValue: (r) => r.tasaAtencion,
    render: (r) => formatPct(r.tasaAtencion),
    cellClass: (r) => claseTasa(r.tasaAtencion),
  },
  { header: 'Ingresos', align: 'right', sortValue: (r) => r.ingresos, render: (r) => formatClp(r.ingresos) },
  {
    header: 'Ingreso Promedio por Atención',
    align: 'right',
    sortValue: (r) => r.ingresoPromedio,
    render: (r) => formatClp(r.ingresoPromedio),
  },
];

const renderAtendidas = ({ reservas }: FilteredData) => (
  <BarChart data={sortAsc(countBy(reservas.filter((r) => r.EstadoReserva === 'Atendida'), (r) => r.Medico))} orientation="h" />
);

const renderEstadoMedico = ({ reservas }: FilteredData) => {
  const medicos = uniqueSorted(reservas.map((r) => r.Medico));
  const series = ESTADOS.map((estado) => ({
    name: estado,
    values: medicos.map((m) => reservas.filter((r) => r.Medico === m && r.EstadoReserva === estado).length),
  })).filter((s) => s.values.some((v) => v > 0));
  return <StackedBarChart categories={medicos} series={series} />;
};

const renderInasistencia = ({ reservas }: FilteredData) => {
  const data: Entry[] = sortAsc(
    [...groupBy(reservas, (r) => r.Especialidad)].map(([esp, rows]) => ({
      key: esp,
      value: (calcularMedidas(rows, []).TasaInasistencia ?? 0) * 100,
    })),
  );
  return <BarChart data={data} orientation="h" format={(v) => `${formatDec(v)} %`} />;
};

const renderHorasMes = ({ reservas }: FilteredData) => (
  <BarChart
    data={porMes(reservas, (r) => r.FechaReserva).map((g) => ({
      key: g.nombre,
      value: Math.round(calcularMedidas(g.rows, []).HorasPerdidas * 10) / 10,
    }))}
    format={(v) => formatDec(v)}
    xTitle="Mes"
  />
);

const renderHorasCanal = ({ reservas }: FilteredData) => {
  const data: Entry[] = sortAsc(
    [...groupBy(reservas.filter((r) => r.EstadoReserva === 'No asistió'), (r) => r.Canal)].map(([canal, rows]) => ({
      key: canal,
      value: rows.reduce((a, r) => a + (r.BloqueMinutos ?? 0), 0) / 60,
    })),
  );
  return data.length > 0 ? (
    <BarChart data={data} orientation="h" format={(v) => formatDec(v)} />
  ) : (
    <p className="empty">Sin inasistencias para los filtros seleccionados.</p>
  );
};

const renderDesempeno = ({ reservas, detalle }: FilteredData) => {
  const filas: FilaMedico[] = [...groupBy(reservas, (r) => r.Medico)]
    .map(([medico, rows]) => {
      const id = rows[0].MedicoID;
      const det = detalle.filter((d) => d.MedicoID === id);
      const m = calcularMedidas(rows, []);
      const ingresos = det.reduce((a, d) => a + (d.Importe ?? 0), 0);
      const atenciones = new Set(det.map((d) => d.AtencionID).filter(Boolean)).size;
      return {
        medico,
        total: m.TotalReservas,
        atendidas: m.Atendidas,
        noAsistio: m.NoAsistio,
        canceladas: m.Canceladas,
        pendientes: m.Pendientes,
        tasaAtencion: m.TasaAtencion,
        ingresos,
        ingresoPromedio: atenciones > 0 ? ingresos / atenciones : 0,
      };
    })
    .sort((a, b) => b.total - a.total);
  return <DataTable rows={filas} columns={COLUMNAS} rowKey={(r) => r.medico} initialSort={{ col: 1, dir: 'desc' }} />;
};

export default function GestionMedicaPage() {
  return (
    <>
      <Grid>
        <FilterableCard id="gestion.atendidas" title="Reservas atendidas por médico" scope="reservas" fields={except('estados', 'medicos')} render={renderAtendidas} />
        <FilterableCard id="gestion.estadomedico" title="Reservas por estado y médico" scope="reservas" fields={except('estados')} render={renderEstadoMedico} />
      </Grid>

      <Grid>
        <FilterableCard id="gestion.inasistencia" title="Tasa de inasistencia por especialidad" scope="reservas" fields={except('estados', 'especialidades')} render={renderInasistencia} />
        <FilterableCard id="gestion.horasmes" title="Horas perdidas por inasistencia (por mes)" scope="reservas" fields={except('estados')} render={renderHorasMes} />
      </Grid>

      <FilterableCard
        id="gestion.horascanal"
        title="Horas perdidas por canal (solo reservas con bloque)"
        scope="reservas"
        fields={except('estados', 'canales')}
        render={renderHorasCanal}
        className="card--wide"
      />

      <FilterableCard
        id="gestion.desempeno"
        title="Desempeño por médico"
        scope="reservas"
        fields={except('estados', 'medicos')}
        render={renderDesempeno}
        className="card--wide"
      />

      <hr className="divider" />
      <Note>{NOTA_VISIBLE}</Note>
    </>
  );
}
