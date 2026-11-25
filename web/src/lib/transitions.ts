import type { TransitionAnimationPair } from 'astro';

/**
 * Animación entre vistas: la página saliente se desvanece y sube levemente,
 * la entrante aparece desde abajo con un suave desenfoque. Los @keyframes viven en styles/motion.css.
 * La barra lateral persiste entre páginas y no participa de esta animación.
 */
const pair: TransitionAnimationPair = {
  old: { name: 'page-out', duration: '0.2s', easing: 'cubic-bezier(0.4, 0, 1, 1)', fillMode: 'forwards' },
  new: { name: 'page-in', duration: '0.5s', easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fillMode: 'backwards' },
};

export const pageTransition = { forwards: pair, backwards: pair };
