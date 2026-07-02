/**
 * Tabla generica minimalista: ordenable, con estados loading/empty/error.
 * Sin lineas verticales (03-UI seccion 12).
 */
import type { ReactNode } from 'react';
import { ArrowDown, ArrowUp } from 'lucide-react';
import { Skeleton } from '@/components/Skeleton';
import { EmptyState } from '@/components/EmptyState';
import { ErrorState } from '@/components/ErrorState';

export interface DataTableColumn<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  sortable?: boolean;
  align?: 'left' | 'right';
}

interface DataTableProps<T> {
  columns: Array<DataTableColumn<T>>;
  rows: T[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
  onSortChange?: (key: string) => void;
  isLoading?: boolean;
  error?: unknown;
  onRetry?: () => void;
  emptyMessage?: string;
}

export function DataTable<T>({
  columns,
  rows,
  rowKey,
  onRowClick,
  sortBy,
  sortDir,
  onSortChange,
  isLoading,
  error,
  onRetry,
  emptyMessage,
}: DataTableProps<T>) {
  if (error) return <ErrorState error={error} onRetry={onRetry} />;

  return (
    <div className="overflow-x-auto rounded-card border border-border">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="h-12 border-b border-border bg-surface">
            {columns.map((column) => (
              <th
                key={column.key}
                className={`whitespace-nowrap px-5 text-label font-medium uppercase tracking-wide text-textSecondary ${
                  column.align === 'right' ? 'text-right' : ''
                }`}
              >
                {column.sortable && onSortChange ? (
                  <button
                    className="inline-flex items-center gap-1 hover:text-textPrimary"
                    onClick={() => onSortChange(column.key)}
                  >
                    {column.header}
                    {sortBy === column.key &&
                      (sortDir === 'asc' ? (
                        <ArrowUp className="h-3.5 w-3.5" aria-label="ascendente" />
                      ) : (
                        <ArrowDown className="h-3.5 w-3.5" aria-label="descendente" />
                      ))}
                  </button>
                ) : (
                  column.header
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading
            ? Array.from({ length: 5 }).map((_, index) => (
                <tr key={index} className="h-14 border-b border-border last:border-b-0">
                  {columns.map((column) => (
                    <td key={column.key} className="px-5">
                      <Skeleton className="h-4 w-full max-w-32" />
                    </td>
                  ))}
                </tr>
              ))
            : rows.map((row) => (
                <tr
                  key={rowKey(row)}
                  className={`h-14 border-b border-border bg-surface transition-colors last:border-b-0 hover:bg-surfaceElevated ${
                    onRowClick ? 'cursor-pointer' : ''
                  }`}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={`whitespace-nowrap px-5 text-description text-textPrimary ${
                        column.align === 'right' ? 'text-right' : ''
                      }`}
                    >
                      {column.render(row)}
                    </td>
                  ))}
                </tr>
              ))}
        </tbody>
      </table>
      {!isLoading && rows.length === 0 && <EmptyState message={emptyMessage} />}
    </div>
  );
}
