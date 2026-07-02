import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Pagination } from '@/components/Pagination';

describe('Pagination', () => {
  it('renders nothing with a single page', () => {
    const { container } = render(<Pagination page={1} totalPages={1} onPageChange={() => {}} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('marks current page and navigates', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={2} totalPages={5} onPageChange={onPageChange} />);
    expect(screen.getByRole('button', { name: '2' })).toHaveAttribute('aria-current', 'page');
    fireEvent.click(screen.getByRole('button', { name: '3' }));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('disables previous button on first page', () => {
    render(<Pagination page={1} totalPages={5} onPageChange={() => {}} />);
    expect(screen.getByRole('button', { name: 'Pagina anterior' })).toBeDisabled();
  });
});
