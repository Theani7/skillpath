import { ArrowRight, FileText, UploadCloud } from 'lucide-react';import { motion } from 'framer-motion';import { fadeUp, stagger } from './analysisUtils';const Skeleton = () => (
  <div className="analysis-skeleton">
    <div className="analysis-skeleton-line analysis-skeleton-line-lg" />
    <div className="analysis-skeleton-hero">
      <div className="analysis-skeleton-circle" />
      <div className="analysis-skeleton-stack">
        <div className="analysis-skeleton-line analysis-skeleton-line-md" />
        <div className="analysis-skeleton-line analysis-skeleton-line-sm" />
      </div>
    </div>
    <div className="analysis-skeleton-grid">
      <div className="analysis-skeleton-card" />
      <div className="analysis-skeleton-card" />
      <div className="analysis-skeleton-card analysis-skeleton-card-wide" />
    </div>
  </div>
);

const EmptyState = ({ onUpload }) => (
  <motion.div
    initial="hidden" animate="visible" variants={stagger}
    className="analysis-empty-state"
  >
    <motion.div variants={fadeUp} className="analysis-empty-state-icon">
      <FileText size={32} color="var(--color-primary)" />
    </motion.div>
    <motion.h2 variants={fadeUp} className="analysis-empty-state-title">
      No analysis yet
    </motion.h2>
    <motion.p variants={fadeUp} className="analysis-empty-state-text">
      Upload your resume to get a personalized match score, skill gap analysis, and learning roadmap.
    </motion.p>
    <motion.button
      variants={fadeUp}
      onClick={onUpload}
      className="btn btn-primary"
      style={{ minHeight: '48px', padding: '12px 24px', fontSize: '15px' }}
    >
      <UploadCloud size={16} /> Upload a resume
      <ArrowRight size={16} />
    </motion.button>
  </motion.div>
);
export { Skeleton, EmptyState };
