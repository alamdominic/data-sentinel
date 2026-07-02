import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StatusBadge } from '@/components/StatusBadge';

describe('StatusBadge', () => {
  it('renders known statuses with label', () => {
    render(<StatusBadge status="SUCCESS" />);
    expect(screen.getByText('Success')).toBeInTheDocument();
  });

  it('normalizes lowercase status', () => {
    render(<StatusBadge status="failed" />);
    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  it('shows raw text for unknown status', () => {
    render(<StatusBadge status="WEIRD_STATE" />);
    expect(screen.getByText('WEIRD_STATE')).toBeInTheDocument();
  });
});
