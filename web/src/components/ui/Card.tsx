import type { ReactNode } from 'react';

interface Props {
  title?: string;
  children: ReactNode;
  className?: string;
}

/** Tarjeta con título opcional; contenedor estándar de gráficos y listas. */
export default function Card({ title, children, className = '' }: Props) {
  return (
    <section className={`card ${className}`.trim()}>
      {title && <h3 className="card__title">{title}</h3>}
      {children}
    </section>
  );
}
