import { ChevronLeft, ChevronRight } from 'lucide-react';
import { pageRange } from '@datasentinel/utils';

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;
  return (
    <nav className="flex items-center gap-1" aria-label="Paginacion">
      <button
        className="flex h-9 w-9 items-center justify-center rounded-control text-textSecondary hover:bg-surfaceElevated disabled:opacity-40"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="Pagina anterior"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>
      {pageRange(page, totalPages).map((item, index) =>
        item === '…' ? (
          <span key={`gap-${index}`} className="px-2 text-textMuted">
            …
          </span>
        ) : (
          <button
            key={item}
            onClick={() => onPageChange(item)}
            aria-current={item === page ? 'page' : undefined}
            className={`h-9 min-w-9 rounded-control px-3 text-label transition-colors ${
              item === page
                ? 'bg-primary text-white'
                : 'text-textSecondary hover:bg-surfaceElevated'
            }`}
          >
            {item}
          </button>
        ),
      )}
      <button
        className="flex h-9 w-9 items-center justify-center rounded-control text-textSecondary hover:bg-surfaceElevated disabled:opacity-40"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        aria-label="Pagina siguiente"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </nav>
  );
}
