import { ICONS, type IconName } from '@/lib/icons';

interface Props {
  name: IconName;
  size?: number;
}

/** Equivalente React de Icon.astro (mismos paths de lib/icons.ts). */
export default function SvgIcon({ name, size = 16 }: Props) {
  return (
    <svg
      className="icon"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {ICONS[name].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  );
}
