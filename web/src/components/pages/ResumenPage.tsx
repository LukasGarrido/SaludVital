import { ALL_FIELDS } from '@/lib/chartFilterFields';
import { CONCLUSIONES, NOTA_VISIBLE, RECOMENDACIONES } from '@/lib/content';
import { formatClp, formatNum, formatPct } from '@/lib/format';
import type { Medidas } from '@/lib/types';
import Card from '../ui/Card';
import FilterableKpis from '../ui/FilterableKpis';
import Grid from '../ui/Grid';
import type { Kpi } from '../ui/KpiGrid';
import Note from '../ui/Note';

const Lista = ({ items }: { items: string[] }) => (
  <ul>
    {items.map((t) => (
      <li key={t}>{t}</li>
    ))}
  </ul>
);

const kpis = (m: Medidas): Kpi[] => [
  { label: 'Total de reservas', value: formatNum(m.TotalReservas) },
  { label: 'Tasa de atención', value: formatPct(m.TasaAtencion) },
  { label: 'Tasa de inasistencia', value: formatPct(m.TasaInasistencia) },
  { label: 'Ingreso valorizado', value: formatClp(m.Ingresos) },
];

export default function ResumenPage() {
  return (
    <>
      <FilterableKpis id="resumen.kpis" fields={ALL_FIELDS} build={kpis} />
      <hr className="divider" />
      <Grid>
        <Card title="CONCLUSIONES">
          <Lista items={CONCLUSIONES} />
        </Card>
        <Card title="RECOMENDACIONES OPERACIONALES">
          <Lista items={RECOMENDACIONES} />
        </Card>
      </Grid>
      <hr className="divider" />
      <Note>{NOTA_VISIBLE}</Note>
    </>
  );
}
