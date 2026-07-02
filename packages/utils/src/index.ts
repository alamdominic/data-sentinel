/** Utilidades puras compartidas. Sin logica de negocio critica. */

/** Formatea segundos como "2h 05m", "3m 20s" o "45s". */
export function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined || Number.isNaN(seconds)) return '—';
  const total = Math.max(0, Math.round(seconds));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  if (hours > 0) return `${hours}h ${String(minutes).padStart(2, '0')}m`;
  if (minutes > 0) return `${minutes}m ${String(secs).padStart(2, '0')}s`;
  return `${secs}s`;
}

/** Formatea fecha ISO como "01 jul 2026, 10:05". */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/** Formatea fecha ISO como "01 jul 2026". */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' });
}

/** Tiempo relativo: "hace 5 min", "hace 2 h", "hace 3 d". */
export function formatRelativeTime(iso: string | null | undefined, now: Date = new Date()): string {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '—';
  const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (diffSeconds < 0) return formatDateTime(iso);
  if (diffSeconds < 60) return 'hace unos segundos';
  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) return `hace ${diffMinutes} min`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `hace ${diffHours} h`;
  return `hace ${Math.floor(diffHours / 24)} d`;
}

/** Formatea numeros con separador de miles es-MX. */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—';
  return value.toLocaleString('es-MX');
}

/** Rango de paginas visible alrededor de la actual: [1, '…', 4, 5, 6, '…', 20]. */
export function pageRange(current: number, totalPages: number, siblings = 1): Array<number | '…'> {
  if (totalPages <= 0) return [];
  const pages = new Set<number>([1, totalPages]);
  for (let page = current - siblings; page <= current + siblings; page += 1) {
    if (page >= 1 && page <= totalPages) pages.add(page);
  }
  const sorted = [...pages].sort((a, b) => a - b);
  const result: Array<number | '…'> = [];
  let previous = 0;
  for (const page of sorted) {
    if (previous && page - previous > 1) result.push('…');
    result.push(page);
    previous = page;
  }
  return result;
}

/** Convierte params a query string omitiendo vacios. */
export function toQueryString(params: object): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params as Record<string, unknown>)) {
    if (value !== undefined && value !== null && `${value}` !== '') {
      search.set(key, String(value));
    }
  }
  const raw = search.toString();
  return raw ? `?${raw}` : '';
}
