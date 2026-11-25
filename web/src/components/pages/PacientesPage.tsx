import { countBy, groupBy, sortAsc, sumBy, type Entry } from '@/lib/aggregate';
import { ALL_FIELDS, CARTERA_FIELDS, DETALLE_FIELDS, except } from '@/lib/chartFilterFields';
import { PREVISION_ROLES } from '@/lib/chartTheme';
import { NOTA_VISIBLE } from '@/lib/content';
import type { FilteredData } from '@/lib/filters';
import { formatClp, formatDec, formatNum } from '@/lib/format';
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

interface FilaInasistencia {
  paciente: string;
  inasistencias: number;
}

const kpis = (m: Medidas): Kpi[] => [
  { label: 'Pacientes con reservas', value: formatNum(m.PacientesDistintos) },
  { label: 'Reservas por paciente', value: formatDec(m.ReservasPorPaciente) },
];

const renderComuna = ({ reservas }: FilteredData) => (
  <BarChart data={sortAsc(countBy(reservas.filter((r) => r.EstadoReserva === 'Atendida'), (r) => r.Comuna))} orientation="h" />
);

const renderPrevisionReservas = ({ reservas }: FilteredData) => (
  <DonutChart data={countBy(reservas, (r) => r.Prevision)} colors={PREVISION_ROLES} />
);

const renderPrevisionIngresos = ({ detalle }: FilteredData) => (
  <DonutChart data={sumBy(detalle, (d) => d.Prevision, (d) => d.Importe)} colors={PREVISION_ROLES} format={formatClp} />
);

/** La frecuencia de uso responde a comuna y sexo, pero no a la fecha. */
const renderFrecuencia = ({ cartera }: FilteredData) => {
  const data: Entry[] = [...groupBy(cartera, (p) => p['Tramo Frecuencia'])]
    .sort((a, b) => a[1][0]['Orden Tramo'] - b[1][0]['Orden Tramo'])
    .map(([tramo, rows]) => ({ key: tramo, value: rows.length }));
  return <BarChart data={data} />;
};

const renderPacientesMes = ({ reservas }: FilteredData) => (
  <BarChart
    data={porMes(reservas, (r) => r.FechaReserva).map((g) => ({ key: g.nombre, value: new Set(g.rows.map((r) => r.PacienteID)).size }))}
    xTitle="Mes"
  />
);

const renderInasistentes = ({ reservas }: FilteredData) => {
  const filas: FilaInasistencia[] = [...groupBy(reservas.filter((r) => r.EstadoReserva === 'No asistió'), (r) => r.PacienteID)]
    .map(([paciente, rows]) => ({ paciente, inasistencias: rows.length }))
    .filter((f) => f.inasistencias >= 2)
    .sort((a, b) => b.inasistencias - a.inasistencias);
  return filas.length > 0 ? (
    <DataTable
      rows={filas}
      rowKey={(r) => r.paciente}
      columns={[
        { header: 'PacienteID', sortValue: (r) => r.paciente, render: (r) => r.paciente },
        { header: 'Reservas No Asistió', align: 'right', sortValue: (r) => r.inasistencias, render: (r) => r.inasistencias },
      ]}
    />
  ) : (
    <p className="empty">Sin pacientes con 2 o más inasistencias.</p>
  );
};

export default function PacientesPage() {
  return (
    <>
      <FilterableKpis id="pacientes.kpis" fields={ALL_FIELDS} columns={2} build={kpis} />
      <hr className="divider" />

      <Grid>
        <FilterableCard id="pacientes.comuna" title="Reservas atendidas por comuna" scope="reservas" fields={except('comunas', 'estados')} render={renderComuna} />
        <FilterableCard id="pacientes.prevision" title="Reservas por previsión" scope="reservas" fields={except('previsiones')} render={renderPrevisionReservas} />
      </Grid>

      <Grid>
        <FilterableCard
          id="pacientes.ingresos"
          title="Ingresos por previsión (valorizado)"
          scope="detalle"
          fields={DETALLE_FIELDS.filter((f) => f !== 'previsiones')}
          render={renderPrevisionIngresos}
        />
        <FilterableCard id="pacientes.frecuencia" title="Frecuencia de uso (reservas por paciente)" scope="cartera" fields={CARTERA_FIELDS} render={renderFrecuencia} />
      </Grid>

      <FilterableCard id="pacientes.mes" title="Pacientes distintos por mes" scope="reservas" fields={ALL_FIELDS} render={renderPacientesMes} className="card--wide" />

      <FilterableCard
        id="pacientes.inasistentes"
        title="Pacientes con 2 o más inasistencias (solo IDs)"
        scope="reservas"
        fields={except('estados')}
        render={renderInasistentes}
        className="card--wide"
      />

      <hr className="divider" />
      <Note>{NOTA_VISIBLE}</Note>
    </>
  );
}
