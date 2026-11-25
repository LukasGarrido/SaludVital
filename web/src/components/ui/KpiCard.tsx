interface Props {
  label: string;
  value: string;
}

export default function KpiCard({ label, value }: Props) {
  return (
    <div className="kpi">
      <div className="kpi__label">{label}</div>
      <div className="kpi__value">{value}</div>
    </div>
  );
}
