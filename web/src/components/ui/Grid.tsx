import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  columns?: 1 | 2;
}

/** Rejilla responsiva para tarjetas (2 columnas en escritorio). */
export default function Grid({ children, columns = 2 }: Props) {
  return <div className={`grid grid--${columns}`}>{children}</div>;
}
