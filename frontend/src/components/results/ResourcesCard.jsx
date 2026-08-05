import { BookOpen, PlayCircle } from 'lucide-react';
import badge from './badge';

const ResourcesCard = ({ tutorials }) => {
  return (
        <div className="card" style={{ padding: '28px', marginBottom: '20px' }}>
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
            flexWrap: 'wrap', gap: '12px', marginBottom: '20px',
          }}>
            <div>
              <h3 style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                fontSize: '16px', fontWeight: 'var(--font-bold)',
                color: 'var(--color-text)', marginBottom: '4px',
              }}>
                <span style={{
                  width: '32px', height: '32px', borderRadius: 'var(--radius-md)',
                  background: 'var(--indigo-50)', color: 'var(--color-primary)',
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <BookOpen size={16} />
                </span>
                Learning Resources
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>
                Curated tutorials to close your skill gaps.
              </p>
            </div>
            <span style={badge({ bg: 'var(--indigo-50)', fg: 'var(--color-primary)' })}>
              {tutorials.length} tutorials
            </span>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '12px',
          }}>
            {tutorials.slice(0, 6).map((video, i) => (
              <a
                key={i}
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ textDecoration: 'none' }}
              >
                <div style={{
                  padding: '16px', borderRadius: 'var(--radius-lg)',
                  border: '1px solid var(--color-border)',
                  background: 'var(--color-surface)',
                  transition: 'border-color 150ms ease, transform 150ms ease',
                  cursor: 'pointer',
                  height: '100%',
                  display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-primary)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
                >
                  <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
                    marginBottom: '10px',
                  }}>
                    <span style={badge({ bg: 'var(--indigo-50)', fg: 'var(--color-primary)' })}>
                      Tutorial
                    </span>
                    <PlayCircle size={16} color="var(--color-text-muted)" />
                  </div>
                  <h4 style={{
                    fontSize: '13px', fontWeight: 'var(--font-semibold)',
                    color: 'var(--color-text)', marginBottom: '6px', lineHeight: 1.4,
                  }}>
                    {video.title}
                  </h4>
                  <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    Watch on YouTube
                  </span>
                </div>
              </a>
            ))}
          </div>
        </div>
  );
};

export default ResourcesCard;
