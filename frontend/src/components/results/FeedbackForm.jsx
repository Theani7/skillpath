import { Check, Send, Star } from 'lucide-react';

const FeedbackForm = (feedbackSent, loading, rating, hoverRating, onRate, onHover, onSubmit) => {
  return (
      <div style={{
        borderRadius: 'var(--radius-xl)',
        padding: '40px 24px',
        background: 'linear-gradient(135deg, #0a1628 0%, #1a2d4a 100%)',
        color: 'white',
        textAlign: 'center',
      }}>
        {!feedbackSent ? (
          <>
            <h3 style={{ fontSize: '20px', fontWeight: 'var(--font-bold)', marginBottom: '8px' }}>
              Was this analysis helpful?
            </h3>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)', marginBottom: '20px' }}>
              Your feedback helps us improve the AI.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '24px' }}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => onRate(star)}
                  onMouseEnter={() => onHover(star)}
                  onMouseLeave={() => onHover(0)}
                  style={{
                    background: 'transparent', border: 'none', cursor: 'pointer',
                    padding: '4px', transition: 'transform 150ms ease',
                  }}
                  onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.9)'}
                  onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
                >
                  <Star
                    size={28}
                    fill={(hoverRating || rating) >= star ? '#F59E0B' : 'transparent'}
                    color={(hoverRating || rating) >= star ? '#F59E0B' : 'rgba(255,255,255,0.3)'}
                  />
                </button>
              ))}
            </div>
            <form onSubmit={onSubmit} style={{ maxWidth: '440px', margin: '0 auto' }}>
              <textarea
                name="comments"
                placeholder="Any suggestions to improve our AI?"
                style={{
                  width: '100%', minHeight: '90px',
                  padding: '14px', borderRadius: 'var(--radius-lg)',
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  color: 'white', fontSize: '14px',
                  fontFamily: 'inherit', resize: 'vertical',
                  outline: 'none', boxSizing: 'border-box',
                  marginBottom: '12px',
                }}
                onFocus={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.4)'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.15)'}
              />
              <button
                type="submit"
                disabled={loading}
                style={{
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                  width: '100%', height: '44px', padding: '0 20px',
                  borderRadius: 'var(--radius-lg)', border: 'none',
                  background: 'white', color: '#ffffff',
                  fontWeight: 'var(--font-semibold)', fontSize: '14px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                <Send size={16} />
                {loading ? 'Sending...' : 'Submit Feedback'}
              </button>
            </form>
          </>
        ) : (
          <div style={{ padding: '20px 0' }}>
            <div style={{
              width: '56px', height: '56px', borderRadius: '50%',
              background: 'var(--color-success)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: '16px',
            }}>
              <Check size={28} color="white" />
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: 'var(--font-bold)', marginBottom: '4px' }}>
              Thank you!
            </h3>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)', margin: 0 }}>
              Your feedback helps us improve.
            </p>
          </div>
        )}
      </div>
  );
};

export default FeedbackForm;
