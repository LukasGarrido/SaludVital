import type { IconName } from './icons';

export interface NavItem {
  label: string;
  href: string; // relativo a BASE_URL
  icon: IconName;
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Resumen', href: '', icon: 'resumen' },
  { label: 'Visión ejecutiva', href: 'vision-ejecutiva', icon: 'ejecutiva' },
  { label: 'Gestión médica', href: 'gestion-medica', icon: 'medica' },
  { label: 'Pacientes', href: 'pacientes', icon: 'pacientes' },
  { label: 'Pruebas de aceptación', href: 'pruebas-aceptacion', icon: 'pruebas' },
];
