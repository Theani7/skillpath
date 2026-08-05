import { Sparkles } from 'lucide-react';

const AnalyzerHeader = () => {
  return (
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '6px',
              padding: '4px 12px', borderRadius: 'var(--radius-full)',
              fontSize: 'var(--text-xs)', fontWeight: 'var(--font-semibold)',
              color: 'var(--color-primary)', background: 'var(--indigo-50)',
              border: '1px solid var(--indigo-100)',
              marginBottom: '20px',
            }}>
              <Sparkles size={11} />
              AI-Powered Analysis
            </div>
            <h1 style={{
              fontSize: 'clamp(28px, 4vw, 36px)',
              fontWeight: 'var(--font-extrabold)',
              letterSpacing: 'var(--tracking-tight)',
              color: 'var(--color-text)',
              marginBottom: '12px',
            }}>
              Resume Intelligence
            </h1>
            <p style={{
              fontSize: 'var(--text-base)',
              color: 'var(--color-text-muted)',
              lineHeight: 1.6,
              maxWidth: '480px',
              margin: '0 auto',
            }}>
              Upload your resume and let our AI identify skill gaps and recommend a personalized learning path.
            </p>
          </div>
  );
};

export default AnalyzerHeader;
