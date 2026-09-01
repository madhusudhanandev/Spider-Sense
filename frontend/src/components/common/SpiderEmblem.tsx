interface Props {
  className?: string;
}

/**
 * An original spider-silhouette-in-a-web mark. Deliberately abstract rather
 * than a licensed character illustration -- this is the "graceful fallback"
 * the design directive calls for (spider emblem / web illustration / masked
 * silhouette) so the product never depends on copyrighted artwork.
 */
export default function SpiderEmblem({ className = "w-8 h-8" }: Props) {
  return (
    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
      <circle cx="24" cy="24" r="22" stroke="currentColor" strokeOpacity="0.25" strokeWidth="1" />
      <g stroke="currentColor" strokeOpacity="0.35" strokeWidth="1">
        <line x1="24" y1="2" x2="24" y2="46" />
        <line x1="2" y1="24" x2="46" y2="24" />
        <line x1="8" y1="8" x2="40" y2="40" />
        <line x1="40" y1="8" x2="8" y2="40" />
      </g>
      <ellipse cx="24" cy="26" rx="6.5" ry="8.5" fill="currentColor" />
      <ellipse cx="24" cy="15" rx="4" ry="4.5" fill="currentColor" />
      <g stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
        <path d="M18 22 L7 15" />
        <path d="M18 26 L5 26" />
        <path d="M18 30 L7 37" />
        <path d="M30 22 L41 15" />
        <path d="M30 26 L43 26" />
        <path d="M30 30 L41 37" />
      </g>
    </svg>
  );
}
