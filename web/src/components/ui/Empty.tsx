/** Estado vacío de una tarjeta cuando los filtros no dejan datos. */
export default function Empty({ message = 'Sin datos para los filtros seleccionados.' }: { message?: string }) {
  return <p className="empty">{message}</p>;
}
