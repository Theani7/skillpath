import { ReactNode } from 'react';
import type { AdminCourse } from '../../types';
import { DataTable } from './DataTable';
import { truncate } from './adminUtils';

type FeedbackItem = {
  id: number;
  feed_name: string;
  feed_email: string;
  feed_score: number | string;
  comments: string;
  Timestamp: string;
};

type FeedbackStats = {
  total: number;
  positive: number;
  neutral: number;
  negative: number;
  ratio: number | string;
  by_score: Record<number, number>;
};

type Props = {
  feedback: FeedbackItem[];
  stats: FeedbackStats | null;
  page: number;
  total: number;
  pageSize: number;
  onPageChange: (updater: (prev: number) => number) => void;
  onDelete: (id: number) => void;
};

const FeedbackTab = ({ feedback, stats, page, total, pageSize, onPageChange, onDelete }: Props) => (
  <div>
    {stats && stats.total > 0 && (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Total Reviews</span>
          <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--color-text)', fontFamily: 'var(--font-display)' }}>{stats.total}</span>
        </div>
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px', borderLeft: '3px solid #10B981' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#10B981', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Positive</span>
          <span style={{ fontSize: '28px', fontWeight: 800, color: '#10B981', fontFamily: 'var(--font-display)' }}>{stats.positive}</span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>4-5 stars</span>
        </div>
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px', borderLeft: '3px solid #F59E0B' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#F59E0B', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Neutral</span>
          <span style={{ fontSize: '28px', fontWeight: 800, color: '#F59E0B', fontFamily: 'var(--font-display)' }}>{stats.neutral}</span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>3 stars</span>
        </div>
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px', borderLeft: '3px solid #EF4444' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#EF4444', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Negative</span>
          <span style={{ fontSize: '28px', fontWeight: 800, color: '#EF4444', fontFamily: 'var(--font-display)' }}>{stats.negative}</span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>1-2 stars</span>
        </div>
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px', borderLeft: '3px solid var(--color-primary)' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Positive Ratio</span>
          <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--color-primary)', fontFamily: 'var(--font-display)' }}>{stats.ratio === '∞' ? '∞' : `${stats.ratio}:1`}</span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>positive per negative</span>
        </div>
      </div>
    )}

    {stats && stats.total > 0 && (
      <div className="card" style={{ padding: '20px', marginBottom: '20px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-text)', margin: '0 0 14px' }}>Rating Distribution</h3>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '100px' }}>
          {[5, 4, 3, 2, 1].map((score) => {
            const count = stats.by_score[score] || 0;
            const pct = stats.total > 0 ? (count / stats.total) * 100 : 0;
            const color = score >= 4 ? '#10B981' : score === 3 ? '#F59E0B' : '#EF4444';
            return (
              <div key={score} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>{count}</span>
                <div style={{ width: '100%', background: 'var(--color-border)', borderRadius: '4px', overflow: 'hidden', height: `${Math.max(pct, 4)}%`, transition: 'height 400ms ease' }}>
                  <div style={{ width: '100%', height: '100%', background: color, borderRadius: '4px' }} />
                </div>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text)' }}>{'★'.repeat(score)}</span>
              </div>
            );
          })}
        </div>
      </div>
    )}

    <DataTable
      columns={[
        { label: 'Name', render: (f) => f.feed_name as ReactNode },
        { label: 'Email', render: (f) => f.feed_email as ReactNode, mono: true },
        { label: 'Rating', render: (f) => {
          const score = Number(f.feed_score) || 0;
          const color = score >= 4 ? '#10B981' : score === 3 ? '#F59E0B' : '#EF4444';
          return <span style={{ color, fontWeight: 600 }}>{'★'.repeat(score)}<span style={{ opacity: 0.2 }}>{'★'.repeat(5 - score)}</span></span>;
        }},
        { label: 'Comments', render: (f) => truncate(f.comments as string, 80), nowrap: true },
        { label: 'When', render: (f) => f.Timestamp as ReactNode },
      ]}
      rows={feedback as unknown as Record<string, unknown>[]}
      keyField="id"
      empty="No feedback yet."
      onDelete={onDelete}
      deleteLabel="Delete feedback"
    />
    {total > pageSize && (
      <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px' }}>
        <button type="button" disabled={page === 0} onClick={() => onPageChange((p) => p - 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: page === 0 ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: page === 0 ? 'default' : 'pointer', fontSize: '13px' }}>Previous</button>
        <span style={{ padding: '6px 14px', fontSize: '13px', color: 'var(--color-text-muted)' }}>Page {page + 1} of {Math.ceil(total / pageSize)}</span>
        <button type="button" disabled={(page + 1) * pageSize >= total} onClick={() => onPageChange((p) => p + 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: (page + 1) * pageSize >= total ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: (page + 1) * pageSize >= total ? 'default' : 'pointer', fontSize: '13px' }}>Next</button>
      </div>
    )}
  </div>
);

export { FeedbackTab };
