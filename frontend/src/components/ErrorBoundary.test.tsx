import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ErrorBoundary from './ErrorBoundary';

const Boom = () => { throw new Error('render exploded'); };

describe('ErrorBoundary', () => {
  beforeEach(() => { vi.spyOn(console, 'error').mockImplementation(() => {}); });
  afterEach(() => { vi.restoreAllMocks(); });

  it('renders children when nothing throws', () => {
    render(<ErrorBoundary><p>all good</p></ErrorBoundary>);
    expect(screen.getByText('all good')).toBeInTheDocument();
  });

  it('shows recovery UI instead of a blank page when a child throws', () => {
    // Every route is wrapped in this. Without it a render error blanks the app.
    render(<ErrorBoundary><Boom /></ErrorBoundary>);
    expect(document.body.textContent?.trim()).not.toBe('');
    expect(screen.queryByText('all good')).not.toBeInTheDocument();
  });

  it('only shows the raw error message in development', () => {
    // Raw messages can carry internal paths or state, so they are dev-only.
    render(<ErrorBoundary><Boom /></ErrorBoundary>);
    const leaked = screen.queryByText(/render exploded/);
    if (import.meta.env.DEV) {
      expect(leaked).toBeInTheDocument();
    } else {
      expect(leaked).not.toBeInTheDocument();
    }
  });

  it('offers a way to recover', () => {
    render(<ErrorBoundary><Boom /></ErrorBoundary>);
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });

  it('calls onReset and re-renders children after recovery', async () => {
    const onReset = vi.fn();
    let shouldThrow = true;
    const Flaky = () => {
      if (shouldThrow) throw new Error('transient');
      return <p>recovered</p>;
    };
    const { getByRole } = render(
      <ErrorBoundary onReset={onReset}><Flaky /></ErrorBoundary>,
    );
    shouldThrow = false;
    getByRole('button', { name: /try again/i }).click();
    expect(onReset).toHaveBeenCalledTimes(1);
    expect(await screen.findByText('recovered')).toBeInTheDocument();
  });
});
