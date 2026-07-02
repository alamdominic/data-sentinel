/** Badge de estado de ejecucion (03-UI seccion 13). */
const STATUS_STYLES: Record<string, { label: string; className: string }> = {
  SUCCESS: { label: 'Success', className: 'bg-success/15 text-success' },
  FAILED: { label: 'Failed', className: 'bg-danger/15 text-danger' },
  RUNNING: { label: 'Running', className: 'bg-info/15 text-info' },
  WARNING: { label: 'Warning', className: 'bg-warning/15 text-warning' },
  CANCELLED: { label: 'Cancelled', className: 'bg-textSecondary/15 text-textSecondary' },
};

export function StatusBadge({ status }: { status: string }) {
  const normalized = status?.toUpperCase?.() ?? '';
  const style = STATUS_STYLES[normalized] ?? {
    label: status || 'Unknown',
    className: 'bg-textMuted/15 text-textMuted',
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1.5 text-label font-medium ${style.className}`}
    >
      {style.label}
    </span>
  );
}
