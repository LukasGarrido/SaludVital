import raw from '@/data/dataset.json';
import type { Dataset } from './types';

/** Modelo dimensional completo, sin filtros. Generado con `npm run export-data`. */
export const dataset = raw as unknown as Dataset;
