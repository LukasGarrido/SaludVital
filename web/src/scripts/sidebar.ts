/**
 * Control de la barra lateral: riel colapsado que se expande al pasar el cursor,
 * con opción de fijarla (pinned). El estado vive en <html data-sidebar> y se recuerda.
 * El atributo inicial lo aplica el script del <head> para evitar saltos al cargar.
 */
const KEY = 'saludvital:sidebar';
type Mode = 'collapsed' | 'pinned';

const root = document.documentElement;

function apply(mode: Mode): void {
  root.dataset.sidebar = mode;
  try {
    localStorage.setItem(KEY, mode);
  } catch {
    /* sin almacenamiento: el estado dura solo la sesión */
  }
  document.querySelectorAll<HTMLElement>('[data-sidebar-toggle]').forEach((btn) => {
    btn.setAttribute('aria-pressed', String(mode === 'pinned'));
    btn.setAttribute('aria-label', mode === 'pinned' ? 'Contraer menú lateral' : 'Fijar menú lateral expandido');
    btn.title = mode === 'pinned' ? 'Contraer menú' : 'Fijar menú';
  });
}

// Delegación de eventos: sobrevive a los cambios de página (el documento no se recrea)
document.addEventListener('click', (e) => {
  if ((e.target as Element).closest('[data-sidebar-toggle]')) {
    apply(root.dataset.sidebar === 'pinned' ? 'collapsed' : 'pinned');
  }
});

// Sincroniza el estado de los botones al cargar y tras cada navegación
const sync = () => apply(root.dataset.sidebar === 'pinned' ? 'pinned' : 'collapsed');
sync();
document.addEventListener('astro:page-load', sync);
