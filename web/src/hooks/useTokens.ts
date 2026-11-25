import { useStore } from '@nanostores/react';
import { useMemo } from 'react';
import { readTokens, type ChartTokens } from '@/lib/chartTheme';
import { $theme } from '@/stores/theme';

/** Colores del tema activo; se recalculan al cambiar entre modo claro y oscuro. */
export function useTokens(): ChartTokens {
  const theme = useStore($theme);
  // `theme` es la dependencia que invalida el cálculo: el atributo ya está aplicado al leer.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useMemo(() => readTokens(), [theme]);
}
