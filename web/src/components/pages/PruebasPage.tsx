import { useMemo } from 'react';
import { ejecutarPruebasAceptacion, type Prueba } from '@/lib/acceptance';
import { dataset } from '@/lib/dataset';
import DataTable from '../ui/DataTable';

/** Las pruebas corren siempre sobre el modelo completo, sin filtros globales. */
export default function PruebasPage() {
  const pruebas = useMemo(() => ejecutarPruebasAceptacion(dataset.reservas, dataset.detalle), []);
  const ok = pruebas.filter((p) => p.ok).length;
  const todas = ok === pruebas.length;

  return (
    <>
      <DataTable<Prueba>
        rows={pruebas}
        rowKey={(p) => p.indicador}
        columns={[
          { header: 'Indicador', render: (p) => p.indicador },
          { header: 'Esperado', align: 'right', render: (p) => p.esperado },
          { header: 'Obtenido', align: 'right', render: (p) => p.obtenido },
          {
            header: 'OK',
            render: (p) => (p.ok ? 'Sí' : 'No'),
            cellClass: (p) => (p.ok ? 'cell-ok' : 'cell-bad'),
          },
        ]}
      />
      <div className={`alert ${todas ? 'alert--ok' : 'alert--warn'}`} role="status">
        {todas
          ? `¡Todas las pruebas de aceptación pasaron exitosamente (${ok}/${pruebas.length})!`
          : `Se pasaron ${ok} de ${pruebas.length} pruebas.`}
      </div>
    </>
  );
}
