import { Component } from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

type Props = {
  children: React.ReactNode;
  onReset?: () => void;
};

type State = {
  hasError: boolean;
  error: Error | null;
};

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) this.props.onReset();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div style={{
        minHeight: '60vh',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '40px 16px',
      }}>
        <div className="card" style={{
          maxWidth: '480px', width: '100%', padding: '32px', textAlign: 'center',
        }}>
          <div style={{
            width: '56px', height: '56px', borderRadius: '50%',
            background: 'var(--color-error-light)', color: 'var(--color-error)',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            marginBottom: '16px',
          }}>
            <AlertTriangle size={26} />
          </div>
          <h2 style={{
            fontSize: '20px', fontWeight: 'var(--font-bold)',
            color: 'var(--color-text)', margin: '0 0 8px',
          }}>
            Something went wrong
          </h2>
          <p style={{
            fontSize: '14px', color: 'var(--color-text-muted)',
            lineHeight: 1.6, margin: '0 0 20px',
          }}>
            We hit an unexpected error rendering this view. Your analysis is still safe - try again or start over.
          </p>
          {import.meta.env.DEV && this.state.error?.message && (
            <p style={{
              fontSize: '12px', color: 'var(--color-text-light)',
              fontFamily: 'monospace', padding: '10px',
              background: 'var(--color-bg)', borderRadius: 'var(--radius-md)',
              margin: '0 0 20px', textAlign: 'left',
              wordBreak: 'break-word',
            }}>
              {this.state.error.message}
            </p>
          )}
          <button
            onClick={this.handleReset}
            className="btn btn-primary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <RotateCcw size={14} />
            Try Again
          </button>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
