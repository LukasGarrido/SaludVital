import type { ReactNode } from 'react';

interface Props {
  title?: string;
  children: ReactNode;
}

/** Bloque de página con título de sección; separa las áreas del panel. */
export default function Section({ title, children }: Props) {
  return (
    <div className="section">
      {title && <h2 className="section__title">{title}</h2>}
      {children}
    </div>
  );
}
