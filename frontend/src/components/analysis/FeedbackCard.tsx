import { useState, type FormEvent } from 'react';
import { Check, Send, Star } from 'lucide-react';
import api from '../../services/api';
import type { ResumeData } from '../../types';

type Props = {
  resumeInfo: ResumeData | undefined;
  onSent?: () => void;
};

const FeedbackCard = ({ resumeInfo, onSent }: Props) => {
  const [rating, setRating] = useState<number>(5);
  const [hover, setHover] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [sent, setSent] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const fd = new FormData(e.currentTarget);
      await api.post('/api/feedback', {
        name: resumeInfo?.name || 'Anonymous',
        email: resumeInfo?.email || 'N/A',
        score: rating.toString(),
        comments: fd.get('comments') || '',
      });
      setSent(true);
      onSent?.();
    } catch (_err) {
      setError('Failed to submit feedback. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="analysis-feedback">
      {!sent ? (
        <>
          <div className="analysis-feedback-header">
            <h3>How useful was this analysis?</h3>
            <p>Your feedback helps us improve the AI for everyone.</p>
          </div>
          <div className="analysis-stars">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                onMouseEnter={() => setHover(star)}
                onMouseLeave={() => setHover(0)}
                aria-label={`Rate ${star} out of 5`}
                className="analysis-star-btn"
              >
                <Star
                  size={28}
                  fill={(hover || rating) >= star ? 'var(--color-primary)' : 'transparent'}
                  color={(hover || rating) >= star ? 'var(--color-primary)' : 'var(--color-border)'}
                />
              </button>
            ))}
          </div>
          {rating > 0 && (
            <div className="analysis-rating-label">
              {rating === 1 && 'Not useful'}
              {rating === 2 && 'Slightly useful'}
              {rating === 3 && 'Moderately useful'}
              {rating === 4 && 'Very useful'}
              {rating === 5 && 'Extremely useful'}
            </div>
          )}
          <form onSubmit={handleSubmit} className="analysis-feedback-form">
            {error && (
              <div style={{
                padding: '8px 12px', marginBottom: '12px',
                background: 'var(--color-error-light)', color: 'var(--color-error)',
                borderRadius: 'var(--radius-md)', fontSize: '13px', fontWeight: 'var(--font-semibold)',
              }}>
                {error}
              </div>
            )}
            <textarea
              name="comments"
              placeholder="Any suggestions to improve the analysis?"
              className="analysis-feedback-input"
            />
            <button type="submit" disabled={loading || !rating} className="analysis-feedback-submit">
              {loading ? (
                <><span className="analysis-spinner" /> Sending...</>
              ) : (
                <><Send size={15} /> Submit feedback</>
              )}
            </button>
          </form>
        </>
      ) : (
        <div className="analysis-feedback-sent">
          <div className="analysis-feedback-sent-icon">
            <Check size={28} color="white" />
          </div>
          <h3>Thanks for the feedback!</h3>
          <p>It helps us improve the AI for everyone.</p>
        </div>
      )}
    </div>
  );
};

export { FeedbackCard };
