import { ArrowRight, BookOpen } from 'lucide-react';
import { pill, PLATFORM_STYLES, detectPlatform } from './analysisUtils';
import type { YoutubeLink } from '../../types';

type Props = {
  tutorials: YoutubeLink[];
};

const TUTORIAL_LABEL = 'Tutorial';

const ResourcesTab = ({ tutorials }: Props) => {
  if (!Array.isArray(tutorials) || tutorials.length === 0) {
    return (
      <div className="card analysis-empty">
        <BookOpen size={24} color="var(--color-text-light)" />
        <h3>No resources yet</h3>
        <p>Once you identify skill gaps, we'll surface tutorials to close them.</p>
      </div>
    );
  }
  return (
    <div className="card analysis-resources-card">
      <div className="analysis-card-head">
        <div className="analysis-card-icon" style={{ background: 'var(--indigo-50)', color: 'var(--color-primary)' }}>
          <BookOpen size={18} />
        </div>
        <div>
          <h3>Learning resources</h3>
          <p className="analysis-card-sub">Curated tutorials to close your skill gaps.</p>
        </div>
        <span style={pill('var(--indigo-50)', 'var(--color-primary)')}>
          {tutorials.length} tutorial{tutorials.length === 1 ? '' : 's'}
        </span>
      </div>
      <div className="analysis-resources-grid">
        {tutorials.slice(0, 9).map((video, i) => {
          const platform = detectPlatform(video.url);
          const style = PLATFORM_STYLES[platform];
          return (
            <a
              key={i}
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="analysis-resource-card"
            >
              <div className="analysis-resource-thumb" style={{ background: style.gradient }}>
                <PlayCircle size={22} color="white" />
                <span style={{
                  position: 'absolute',
                  bottom: '8px',
                  left: '10px',
                  fontSize: '10px',
                  fontWeight: 600,
                  color: 'rgba(255,255,255,0.9)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}>
                  {style.label}
                </span>
              </div>
              <div className="analysis-resource-meta">
                <span className="analysis-resource-tag">{TUTORIAL_LABEL}</span>
                <h4 className="analysis-resource-title">{video.title}</h4>
                <div className="analysis-resource-foot">
                  Watch on {style.label}
                  <ArrowRight size={12} />
                </div>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
};

const PlayCircle = ({ size, color }: { size: number; color: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polygon points="10 8 16 12 10 16 10 8" />
  </svg>
);

export { ResourcesTab };
