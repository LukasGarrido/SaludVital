/**
 * Carga diferida de Plotly y rescate de su hoja de estilos.
 *
 * Plotly inyecta sus reglas CSS (p. ej. `.main-svg { position: absolute }`) en un <style> del <head>
 * una sola vez, al importar el módulo. Con View Transitions de Astro el <head> se reemplaza en cada
 * navegación y esa hoja se pierde: las capas SVG del gráfico pasan a `position: static`, se apilan
 * verticalmente y las barras, etiquetas y anotaciones quedan deformadas o fuera de lugar.
 *
 * Solución: mover el <style> a un contenedor que persiste entre páginas (ver Layout.astro).
 */
const importPlotly = () => import('plotly.js-basic-dist-min').then((mod) => mod.default);
type PlotlyApi = Awaited<ReturnType<typeof importPlotly>>;

const STYLE_ID = 'plotly.js-style-global';
const HOST_ID = 'plotly-style-host';

let cached: Promise<PlotlyApi> | null = null;

/** Mantiene las reglas de Plotly dentro del contenedor persistente. */
export function keepPlotlyStyles(): void {
  const host = document.getElementById(HOST_ID);
  const style = document.getElementById(STYLE_ID);
  if (!host || !style || style.parentElement === host) return;
  // Plotly agrega las reglas con `insertRule` (solo en el CSSOM, el <style> queda vacío): al mover el nodo
  // se reinicia la hoja, así que se copian a texto antes y se restauran después.
  const css = Array.from((style as HTMLStyleElement).sheet?.cssRules ?? [])
    .map((rule) => rule.cssText)
    .join('\n');
  host.appendChild(style);
  if (css) style.textContent = css;
}

export function loadPlotly(): Promise<PlotlyApi> {
  cached ??= importPlotly();
  return cached.then((Plotly) => {
    keepPlotlyStyles();
    return Plotly;
  });
}
