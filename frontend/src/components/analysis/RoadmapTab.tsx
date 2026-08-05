import { BookOpen, Briefcase } from 'lucide-react';
import Roadmap from '../Roadmap';
import type { RoadmapPhase } from '../../types';

type Props = {
  roadmap: RoadmapPhase[];
  analysisId?: number;
};

const RoadmapTab = ({ roadmap, analysisId }: Props) => {
  if (!Array.isArray(roadmap) || roadmap.length === 0) {
    return (
      <div className="card analysis-empty">
        <BookOpen size={24} color="var(--color-text-light)" />
        <h3>No roadmap generated</h3>
        <p>This analysis did not include a learning roadmap.</p>
      </div>
    );
  }
  return (
    <div className="card analysis-roadmap-card">
      <div className="analysis-card-head">
        <div className="analysis-card-icon" style={{ background: 'var(--indigo-50)', color: 'var(--color-primary)' }}>
          <Briefcase size={18} />
        </div>
        <div>
          <h3>AI career roadmap</h3>
          <p className="analysis-card-sub">A step-by-step plan to close your skill gaps.</p>
        </div>
      </div>
      <Roadmap path={roadmap} analysisId={analysisId} />
    </div>
  );
};

export { RoadmapTab };
