import { useMemo } from 'react';
import { useFilteredData } from '@/hooks/useFilteredData';
import { countBy, groupBy, sortAsc, sumBy, type Entry } from '@/lib/aggregate';
import { PREVISION_COLORS } from '@/lib/chartTheme';
import { NOTA_VISIBLE } from '@/lib/content';
import { formatDec, formatNum } from '@/lib/format';
import { porMes } from '@/lib/series';
import BarChart from '../charts/BarChart';
import DonutChart from '../charts/DonutChart';
import Card from '../ui/Card';
import DataTable from '../ui/DataTable';
import Empty from '../ui/Empty';
import Grid from '../ui/Grid';
import KpiGrid from '../ui/KpiGrid';
import Note from '../ui/Note';
import Section from '../ui/Section';

interface FilaInasistencia {
  paciente: string;
  inasistencias: number;
}

export default function PacientesPage() {
  const { reservas, detalle, cartera, medidas: m } = useFilteredData();
  const hay = reservas.length > 0;

  const atendidasComuna = useMemo(
    () => sortAsc(countBy(reservas.filter((r) => r.EstadoReserva === 'Atendida'), (r) => r.Comuna)),
    [reservas],
  );
  const reservasPrevision = useMemo(() => countBy(reservas, (r) => r.Prevision), [reservas]);
  const ingresosPrevision = useMemo(() => sumBy(detalle, (d) => d.Prevision, (d) => d.Importe), [detalle]);

  // La frecuencia de uso responde a comuna y sexo, pero no a la fecha.
  const frecuencia = useMemo<Entry[]>(
    () =>
      [...groupBy(cartera, (p) => p['Tramo Frecuencia'])]
        .sort((a, b) => a[1][0]['Orden Tramo'] - b[1][0]['Orden Tramo'])
        .map(([tramo, rows]) => ({ key: tramo, value: rows.length })),
    [cartera],
  );

  const pacientesMes = useMemo<Entry[]>(
    () =>
      porMes(reservas, (r) => r.FechaReserva).map((g) => ({
        key: g.nombre,
        value: new Set(g.rows.map((r) => r.PacienteID)).size,
      })),
    [reservas],
  );

  const inasistentes = useMemo<FilaInasistencia[]>(
    () =>
      [...groupBy(reservas.filter((r) => r.EstadoReserva === 'No asistió'), (r) => r.PacienteID)]
        .map(([paciente, rows]) => ({ paciente, inasistencias: rows.length }))
        .filter((f) => f.inasistencias >= 2)
        .sort((a, b) => b.inasistencias - a.inasistencias),
    [reservas],
  );

  return (
    <>
      <KpiGrid
        columns={2}
        items={[
          { label: 'Pacientes con reservas', value: formatNum(m.PacientesDistintos) },
          { label: 'Reservas por paciente', value: formatDec(m.ReservasPorPaciente) },
        ]}
      />
      <hr className="divider" />

      <Grid>
        <Card title="Reservas atendidas por comuna">
          {atendidasComuna.length > 0 ? <BarChart data={atendidasComuna} orientation="h" /> : <Empty message="Sin datos de comuna." />}
        </Card>
        <Card title="Reservas por previsión">
          {hay ? <DonutChart data={reservasPrevision} colors={PREVISION_COLORS} /> : <Empty message="Sin datos de previsión." />}
        </Card>
      </Grid>

      <Grid>
        <Card title="Ingresos por previsión (valorizado)">
          {detalle.length > 0 ? <DonutChart data={ingresosPrevision} colors={PREVISION_COLORS} /> : <Empty message="Sin datos de ingresos por previsión." />}
        </Card>
        <Card title="Frecuencia de uso (reservas por paciente)">
          {frecuencia.length > 0 ? <BarChart data={frecuencia} /> : <Empty message="Sin datos de frecuencia." />}
        </Card>
      </Grid>

      <Section title="Pacientes distintos por mes">
        <Card>{hay ? <BarChart data={pacientesMes} xTitle="Mes" /> : <Empty />}</Card>
      </Section>

      <Section title="Pacientes con 2 o más inasistencias (solo IDs)">
        {inasistentes.length > 0 ? (
          <DataTable
            rows={inasistentes}
            rowKey={(r) => r.paciente}
            columns={[
              { header: 'PacienteID', sortValue: (r) => r.paciente, render: (r) => r.paciente },
              { header: 'Reservas No Asistió', align: 'right', sortValue: (r) => r.inasistencias, render: (r) => r.inasistencias },
            ]}
          />
        ) : (
          <Empty message="Sin pacientes con 2 o más inasistencias." />
        )}
      </Section>

      <hr className="divider" />
      <Note>{NOTA_VISIBLE}</Note>
    </>
  );
}
