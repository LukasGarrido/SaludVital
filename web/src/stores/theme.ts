import { atom } from 'nanostores';

export type Theme = 'light' | 'dark';

export const THEME_KEY = 'saludvital:tema';

/** Tema inicial: el que dejó el script del <head> (preferencia guardada o del sistema). */
const initial = (): Theme => (document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light');

export const $theme = atom<Theme>(initial());

/** Aplica el tema al documento, lo recuerda y avisa a los gráficos. */
export function setTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* almacenamiento no disponible: el tema solo dura la sesión */
  }
  $theme.set(theme);
}

export const toggleTheme = (): void => setTheme($theme.get() === 'dark' ? 'light' : 'dark');
