import { useFilteredData } from '@/hooks/useFilteredData';
import { CONCLUSIONES, NOTA_VISIBLE, RECOMENDACIONES } from '@/lib/content';
import { formatClp, formatNum, formatPct } from '@/lib/format';
import Card from '../ui/Card';
import Grid from '../ui/Grid';
import KpiGrid from '../ui/KpiGrid';
import Note from '../ui/Note';

const Lista = ({ items }: { items: string[] }) => (
  <ul>
    {items.map((t) => (
      <li key={t}>{t}</li>
    ))}
  </ul>
);

export default function ResumenPage() {
  const { medidas: m } = useFilteredData();
  return (
    <>
      <KpiGrid
        items={[
          { label: 'Total de reservas', value: formatNum(m.TotalReservas) },
          { label: 'Tasa de atención', value: formatPct(m.TasaAtencion) },
          { label: 'Tasa de inasistencia', value: formatPct(m.TasaInasistencia) },
          { label: 'Ingreso valorizado', value: formatClp(m.Ingresos) },
        ]}
      />
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
