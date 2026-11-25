import { useMemo } from 'react';
import { useFilteredData } from '@/hooks/useFilteredData';
import { countBy, groupBy, sortAsc, uniqueSorted, type Entry } from '@/lib/aggregate';
import { NOTA_VISIBLE } from '@/lib/content';
import { formatClp, formatDec, formatPct } from '@/lib/format';
import { calcularMedidas } from '@/lib/measures';
import { porMes } from '@/lib/series';
import BarChart from '../charts/BarChart';
import StackedBarChart from '../charts/StackedBarChart';
import Card from '../ui/Card';
import DataTable, { type Column } from '../ui/DataTable';
import Empty from '../ui/Empty';
import Grid from '../ui/Grid';
import Note from '../ui/Note';
import Section from '../ui/Section';

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

export default function GestionMedicaPage() {
  const { reservas, detalle } = useFilteredData();
  const hay = reservas.length > 0;

  const atendidasPorMedico = useMemo(
    () => sortAsc(countBy(reservas.filter((r) => r.EstadoReserva === 'Atendida'), (r) => r.Medico)),
    [reservas],
  );

  const estadoMedico = useMemo(() => {
    const medicos = uniqueSorted(reservas.map((r) => r.Medico));
    const series = ESTADOS.map((estado) => ({
      name: estado,
      values: medicos.map((m) => reservas.filter((r) => r.Medico === m && r.EstadoReserva === estado).length),
    })).filter((s) => s.values.some((v) => v > 0));
    return { medicos, series };
  }, [reservas]);

  const inasistenciaEsp = useMemo<Entry[]>(
    () =>
      sortAsc(
        [...groupBy(reservas, (r) => r.Especialidad)].map(([esp, rows]) => ({
          key: esp,
          value: (calcularMedidas(rows, []).TasaInasistencia ?? 0) * 100,
        })),
      ),
    [reservas],
  );

  const horasMes = useMemo<Entry[]>(
    () =>
      porMes(reservas, (r) => r.FechaReserva).map((g) => ({
        key: g.nombre,
        value: Math.round(calcularMedidas(g.rows, []).HorasPerdidas * 10) / 10,
      })),
    [reservas],
  );

  const horasCanal = useMemo<Entry[]>(
    () =>
      sortAsc(
        [...groupBy(reservas.filter((r) => r.EstadoReserva === 'No asistió'), (r) => r.Canal)].map(([canal, rows]) => ({
          key: canal,
          value: rows.reduce((a, r) => a + (r.BloqueMinutos ?? 0), 0) / 60,
        })),
      ),
    [reservas],
  );

  const desempeno = useMemo<FilaMedico[]>(
    () =>
      [...groupBy(reservas, (r) => r.Medico)]
        .map(([medico, rows]) => {
          const id = rows[0].MedicoID;
          const det = detalle.filter((d) => d.MedicoID === id);
          const ms = calcularMedidas(rows, []);
          const ingresos = det.reduce((a, d) => a + (d.Importe ?? 0), 0);
          const atenciones = new Set(det.map((d) => d.AtencionID).filter(Boolean)).size;
          return {
            medico,
            total: ms.TotalReservas,
            atendidas: ms.Atendidas,
            noAsistio: ms.NoAsistio,
            canceladas: ms.Canceladas,
            pendientes: ms.Pendientes,
            tasaAtencion: ms.TasaAtencion,
            ingresos,
            ingresoPromedio: atenciones > 0 ? ingresos / atenciones : 0,
          };
        })
        .sort((a, b) => b.total - a.total),
    [reservas, detalle],
  );

  return (
    <>
      <Grid>
        <Card title="Reservas atendidas por médico">
          {hay ? <BarChart data={atendidasPorMedico} orientation="h" /> : <Empty />}
        </Card>
        <Card title="Reservas por estado y médico">
          {hay ? <StackedBarChart categories={estadoMedico.medicos} series={estadoMedico.series} /> : <Empty />}
        </Card>
      </Grid>

      <Grid>
        <Card title="Tasa de inasistencia por especialidad">
          {hay ? <BarChart data={inasistenciaEsp} orientation="h" format={(v) => `${formatDec(v)} %`} /> : <Empty />}
        </Card>
        <Card title="Horas perdidas por inasistencia (por mes)">
          {hay ? <BarChart data={horasMes} format={(v) => formatDec(v)} xTitle="Mes" /> : <Empty />}
        </Card>
      </Grid>

      <Section title="Horas perdidas por canal (solo reservas con bloque)">
        <Card>{horasCanal.length > 0 ? <BarChart data={horasCanal} orientation="h" format={(v) => formatDec(v)} /> : <Empty message="Sin datos de canal." />}</Card>
      </Section>

      <Section title="Desempeño por médico">
        {desempeno.length > 0 ? (
          <DataTable rows={desempeno} columns={COLUMNAS} rowKey={(r) => r.medico} initialSort={{ col: 1, dir: 'desc' }} />
        ) : (
          <Empty message="Sin datos de médico." />
        )}
      </Section>

      <hr className="divider" />
      <Note>{NOTA_VISIBLE}</Note>
    </>
  );
}
