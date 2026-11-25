import type { ReactNode } from 'react';

/** Aviso informativo (equivalente a st.info). */
export default function Note({ children }: { children: ReactNode }) {
  return (
    <aside className="note" role="note">
      {children}
    </aside>
  );
}
