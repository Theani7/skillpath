import { Briefcase } from 'lucide-react';
import Roadmap from '../Roadmap';

const RoadmapCard = (roadmap) => {
  return (
        <div className="card" style={{ padding: '28px', marginBottom: '20px' }}>
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
              <Briefcase size={16} />
            </span>
            AI Career Roadmap
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginBottom: '24px' }}>
            A personalized learning path to close your skill gaps.
          </p>
          <Roadmap path={roadmap} />
        </div>
  );
};

export default RoadmapCard;
