import AnimatedScore from '../AnimatedScore';
import badge from './badge';
import type { ResumeData } from '../../types';

type Props = {
  resumeScore: number;
  feedbackMsgs: string[];
  predictedField: string;
  resumeInfo: ResumeData | null;
};

const ScoreOverview = ({ resumeScore, feedbackMsgs, predictedField, resumeInfo }: Props) => {
  return (
    <div className="card" style={{ padding: '40px 24px', marginBottom: '20px' }}>
      <div style={{
        display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center',
        gap: '40px',
      }}>
        <div>
          <AnimatedScore score={resumeScore} />
          <p style={{
            textAlign: 'center', marginTop: '12px',
            fontSize: '11px', fontWeight: 'var(--font-bold)',
            textTransform: 'uppercase', letterSpacing: '0.08em',
            color: 'var(--color-text-muted)',
          }}>
            Resume Score
          </p>
        </div>
        <div style={{ flex: '1 1 280px', maxWidth: '420px' }}>
          <h2 style={{
            fontSize: '20px', fontWeight: 'var(--font-bold)',
            color: 'var(--color-text)', marginBottom: '10px',
          }}>
            Overall Impression
          </h2>
          <p style={{
            fontSize: '14px', color: 'var(--color-text-muted)',
            lineHeight: 1.6, margin: 0,
          }}>
            {feedbackMsgs[0] ||
              'Your resume shows potential but has some key areas to improve to better align with industry standards.'}
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '16px' }}>
            {predictedField && (
              <span style={badge({ bg: 'var(--indigo-50)', fg: 'var(--color-primary)' })}>
                {predictedField}
              </span>
            )}
            <span style={badge({ bg: 'var(--emerald-50)', fg: 'var(--color-success)' })}>
              ATS Optimized
            </span>
            {resumeInfo?.parsing_method && (
              <span style={badge({ bg: 'var(--color-bg)', fg: 'var(--color-text-muted)' })}>
                {resumeInfo.parsing_method}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreOverview;
