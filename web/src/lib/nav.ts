export interface NavItem {
  label: string;
  href: string; // relativo a BASE_URL
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Resumen', href: '' },
  { label: 'Visión ejecutiva', href: 'vision-ejecutiva' },
  { label: 'Gestión médica', href: 'gestion-medica' },
  { label: 'Pacientes', href: 'pacientes' },
  { label: 'Pruebas de aceptación', href: 'pruebas-aceptacion' },
];
