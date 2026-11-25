import { countBy, sortAsc } from '@/lib/aggregate';
import { ALL_FIELDS, DETALLE_FIELDS, except } from '@/lib/chartFilterFields';
import { NOTA_VISIBLE } from '@/lib/content';
import { mesNum } from '@/lib/dates';
import type { FilteredData } from '@/lib/filters';
import { formatClp, formatNum, formatPct } from '@/lib/format';
import { calcularMedidas } from '@/lib/measures';
import { porMes } from '@/lib/series';
import type { Medidas } from '@/lib/types';
import BarChart from '../charts/BarChart';
import DonutChart from '../charts/DonutChart';
import DataTable from '../ui/DataTable';
import FilterableCard from '../ui/FilterableCard';
import FilterableKpis from '../ui/FilterableKpis';
import Grid from '../ui/Grid';
import type { Kpi } from '../ui/KpiGrid';
import Note from '../ui/Note';

interface FilaTasa {
  mes: string;
  atencion: number | null;
  inasistencia: number | null;
  cancelacion: number | null;
}

const kpis = (m: Medidas): Kpi[] => [
  { label: 'Total de reservas', value: formatNum(m.TotalReservas) },
  { label: 'Atenciones registradas', value: formatNum(m.AtencionesRealizadas) },
  { label: 'Tasa de atención', value: formatPct(m.TasaAtencion) },
  { label: 'Tasa de inasistencia', value: formatPct(m.TasaInasistencia) },
  { label: 'Ingreso valorizado', value: formatClp(m.Ingresos) },
  { label: 'Ingreso promedio / at.', value: formatClp(m.IngresoPromedio) },
];

/** Cada gráfico ofrece solo los filtros que tienen sentido para él (p. ej. el de estados no filtra por estado). */
const renderEstado = ({ reservas }: FilteredData) => <DonutChart data={countBy(reservas, (r) => r.EstadoReserva)} />;

const renderReservasMes = ({ reservas }: FilteredData) => (
  <BarChart data={porMes(reservas, (r) => r.FechaReserva).map((g) => ({ key: g.nombre, value: g.rows.length }))} xTitle="Mes" />
);

const renderEspecialidad = ({ reservas }: FilteredData) => (
  <BarChart data={sortAsc(countBy(reservas, (r) => r.Especialidad))} orientation="h" />
);

const renderIngresoMes = ({ detalle }: FilteredData) => (
  <BarChart
    data={porMes(detalle, (d) => d.FechaAtencion).map((g) => ({
      key: g.nombre,
      value: g.rows.reduce((a, d) => a + (d.Importe ?? 0), 0),
    }))}
    format={formatClp}
    xTitle="Mes"
  />
);

const renderTasas = ({ reservas, detalle }: FilteredData) => {
  const filas: FilaTasa[] = porMes(reservas, (r) => r.FechaReserva).map((g) => {
    const m = calcularMedidas(g.rows, detalle.filter((d) => mesNum(d.FechaAtencion) === g.mes));
    return { mes: g.nombre, atencion: m.TasaAtencion, inasistencia: m.TasaInasistencia, cancelacion: m.TasaCancelacion };
  });
  return (
    <DataTable
      rows={filas}
      rowKey={(r) => r.mes}
      columns={[
        { header: 'Mes', render: (r) => r.mes },
        { header: 'Tasa de Atención', align: 'right', render: (r) => formatPct(r.atencion) },
        { header: 'Tasa de Inasistencia', align: 'right', render: (r) => formatPct(r.inasistencia) },
        { header: 'Tasa de Cancelación', align: 'right', render: (r) => formatPct(r.cancelacion) },
      ]}
    />
  );
};

export default function VisionEjecutivaPage() {
  return (
    <>
      <FilterableKpis id="vision.kpis" fields={ALL_FIELDS} columns={3} build={kpis} />
      <hr className="divider" />

      <Grid>
        <FilterableCard id="vision.estado" title="Reservas por estado" scope="reservas" fields={except('estados')} render={renderEstado} />
        <FilterableCard id="vision.mes" title="Reservas por mes" scope="reservas" fields={ALL_FIELDS} render={renderReservasMes} />
      </Grid>

      <Grid>
        <FilterableCard
          id="vision.especialidad"
          title="Reservas por especialidad (del médico)"
          scope="reservas"
          fields={except('especialidades')}
          render={renderEspecialidad}
        />
        <FilterableCard id="vision.ingreso" title="Ingreso valorizado por mes" scope="detalle" fields={DETALLE_FIELDS} render={renderIngresoMes} />
      </Grid>

      <FilterableCard id="vision.tasas" title="Tasas por mes" scope="reservas" fields={ALL_FIELDS} render={renderTasas} />

      <hr className="divider" />
      <Note>{NOTA_VISIBLE}</Note>
    </>
  );
}
