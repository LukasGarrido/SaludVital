import { useMemo } from 'react';
import { useFilteredData } from '@/hooks/useFilteredData';
import { countBy, sortAsc } from '@/lib/aggregate';
import { NOTA_VISIBLE } from '@/lib/content';
import { formatClp, formatNum, formatPct } from '@/lib/format';
import { calcularMedidas } from '@/lib/measures';
import { mesNum } from '@/lib/dates';
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

interface FilaTasa {
  mes: string;
  atencion: number | null;
  inasistencia: number | null;
  cancelacion: number | null;
}

export default function VisionEjecutivaPage() {
  const { reservas, detalle, medidas: m } = useFilteredData();

  const porEstado = useMemo(() => countBy(reservas, (r) => r.EstadoReserva), [reservas]);
  const reservasMes = useMemo(() => porMes(reservas, (r) => r.FechaReserva).map((g) => ({ key: g.nombre, value: g.rows.length })), [reservas]);
  const porEspecialidad = useMemo(() => sortAsc(countBy(reservas, (r) => r.Especialidad)), [reservas]);
  const ingresoMes = useMemo(
    () => porMes(detalle, (d) => d.FechaAtencion).map((g) => ({ key: g.nombre, value: g.rows.reduce((a, d) => a + (d.Importe ?? 0), 0) })),
    [detalle],
  );
  const tasasMes = useMemo<FilaTasa[]>(
    () =>
      porMes(reservas, (r) => r.FechaReserva).map((g) => {
        const ms = calcularMedidas(g.rows, detalle.filter((d) => mesNum(d.FechaAtencion) === g.mes));
        return { mes: g.nombre, atencion: ms.TasaAtencion, inasistencia: ms.TasaInasistencia, cancelacion: ms.TasaCancelacion };
      }),
    [reservas, detalle],
  );

  const hayReservas = reservas.length > 0;

  return (
    <>
      <KpiGrid
        columns={3}
        items={[
          { label: 'Total de reservas', value: formatNum(m.TotalReservas) },
          { label: 'Atenciones registradas', value: formatNum(m.AtencionesRealizadas) },
          { label: 'Tasa de atención', value: formatPct(m.TasaAtencion) },
          { label: 'Tasa de inasistencia', value: formatPct(m.TasaInasistencia) },
          { label: 'Ingreso valorizado', value: formatClp(m.Ingresos) },
          { label: 'Ingreso promedio / at.', value: formatClp(m.IngresoPromedio) },
        ]}
      />
      <hr className="divider" />

      <Grid>
        <Card title="Reservas por estado">{hayReservas ? <DonutChart data={porEstado} /> : <Empty />}</Card>
        <Card title="Reservas por mes">{hayReservas ? <BarChart data={reservasMes} xTitle="Mes" /> : <Empty />}</Card>
      </Grid>

      <Grid>
        <Card title="Reservas por especialidad (del médico)">
          {hayReservas ? <BarChart data={porEspecialidad} orientation="h" /> : <Empty />}
        </Card>
        <Card title="Ingreso valorizado por mes">
          {detalle.length > 0 ? <BarChart data={ingresoMes} format={formatClp} xTitle="Mes" /> : <Empty />}
        </Card>
      </Grid>

      <Section title="Tasas por mes">
        {tasasMes.length > 0 ? (
          <DataTable
            rows={tasasMes}
            rowKey={(r) => r.mes}
            columns={[
              { header: 'Mes', render: (r) => r.mes },
              { header: 'Tasa de Atención', align: 'right', render: (r) => formatPct(r.atencion) },
              { header: 'Tasa de Inasistencia', align: 'right', render: (r) => formatPct(r.inasistencia) },
              { header: 'Tasa de Cancelación', align: 'right', render: (r) => formatPct(r.cancelacion) },
            ]}
          />
        ) : (
          <Empty message="Sin datos para calcular tasas por mes." />
        )}
      </Section>

      <hr className="divider" />
      <Note>{NOTA_VISIBLE}</Note>
    </>
  );
}
