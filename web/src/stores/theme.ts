import { atom } from 'nanostores';

export type Theme = 'light' | 'dark';

export const THEME_KEY = 'saludvital:tema';

/** Tema inicial: el que dejó el script del <head> (preferencia guardada o del sistema). */
const initial = (): Theme => (document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light');

export const $theme = atom<Theme>(initial());

/** Aplica el tema al documento, lo recuerda y avisa a los gráficos. */
export function setTheme(theme: Theme): void {
  const root = document.documentElement;
  // Clase temporal que suaviza el cambio de color en toda la interfaz (ver styles/motion.css)
  root.classList.add('theme-fade');
  root.dataset.theme = theme;
  window.setTimeout(() => root.classList.remove('theme-fade'), 450);
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* almacenamiento no disponible: el tema solo dura la sesión */
  }
  $theme.set(theme);
}

export const toggleTheme = (): void => setTheme($theme.get() === 'dark' ? 'light' : 'dark');
