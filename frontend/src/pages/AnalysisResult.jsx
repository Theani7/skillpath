import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle, Calendar, CheckCircle, FileText, RefreshCw,
  Share2, Sparkles, Trash2, Trophy, Briefcase, Target, TrendingUp,
} from 'lucide-react';
import api from '../services/api';
import {
  OverviewTab, SkillsTab, CoursesTab, MatchesTab, RoadmapTab,
  MarketTab, ResourcesTab, FeedbackCard, ShareModal, Skeleton, EmptyState,
} from '../components/analysis';
import { TABS, fadeUp, stagger, relativeTime, fullDate } from '../components/analysis/analysisUtils';
const AnalysisResult = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [skillFilter, setSkillFilter] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showShare, setShowShare] = useState(false);

  const loadAnalysis = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(
        `/api/user/latest-analysis?_t=${Date.now()}`,
        { _skipAuthRedirect: true }
      );
      if (res.data?.found) {
        setData(res.data);
      } else {
        setData(null);
      }
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/', { replace: true });
        return;
      }
      setError('Could not load your analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => { loadAnalysis(); }, [loadAnalysis]);

  useEffect(() => {
    const onVisible = () => { if (document.visibilityState === 'visible') loadAnalysis(); };
    document.addEventListener('visibilitychange', onVisible);
    return () => document.removeEventListener('visibilitychange', onVisible);
  }, [loadAnalysis]);

  const analysis = data?.analysis;
  const resumeInfo = analysis?.data || {};
  const targetRole = analysis?.target_role || data?.target_role;
  const predictedField = analysis?.predicted_field || data?.predicted_field;
  const matchScore = analysis?.match_score;
  const resumeScore = analysis?.resume_score ?? data?.resume_score ?? 0;
  const missingSkills = Array.isArray(analysis?.missing_skill_names) ? analysis.missing_skill_names : [];
  const roleSkills = Array.isArray(data?.role_skills) ? data.role_skills : [];
  const roleSkillNames = new Set(roleSkills.map(rs => rs.skill.toLowerCase()));
  const roleSkillsMap = Object.fromEntries(roleSkills.map(rs => [rs.skill.toLowerCase(), rs.is_required]));
  let matchedSkills = Array.isArray(analysis?.data?.matched_role_skills) && analysis.data.matched_role_skills.length > 0
    ? analysis.data.matched_role_skills
    : [];
  // If matched_role_skills is empty (old analysis), compute from resume skills filtered to role
  if (matchedSkills.length === 0 && Array.isArray(resumeInfo?.skills)) {
    matchedSkills = resumeInfo.skills
      .filter(s => roleSkillNames.has(s.toLowerCase()))
      .map(s => ({ skill: s, is_required: roleSkillsMap[s.toLowerCase()] || false }));
  }
  // If still plain strings, annotate
  if (matchedSkills.length > 0 && typeof matchedSkills[0] === 'string') {
    matchedSkills = matchedSkills.map(s => ({
      skill: s,
      is_required: roleSkillsMap[s.toLowerCase()] || false,
    }));
  }
  const feedbackMsgs = Array.isArray(analysis?.feedback) ? analysis.feedback : [];
  const tutorials = Array.isArray(analysis?.videos?.tutorials) ? analysis.videos.tutorials : [];
  const roadmap = analysis?.roadmap;
  const trends = analysis?.trends;
  const scoreBreakdown = analysis?.score_breakdown;
  const courses = Array.isArray(analysis?.recommended_courses) ? analysis.recommended_courses : [];
  const recommendedSkills = Array.isArray(analysis?.recommended_skills) ? analysis.recommended_skills : [];
  const jobMatches = Array.isArray(analysis?.job_matches) ? analysis.job_matches : [];

  const handleDelete = async () => {
    if (!data?.id) return;
    setDeleting(true);
    try {
      await api.delete(`/api/user/analysis/${data.id}`, { _skipAuthRedirect: true });
      setData(null);
      setDeleteConfirm(false);
      navigate('/app', { replace: true });
    } catch (_err) {
      setDeleteConfirm(false);
      setError('Could not delete the analysis. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="analysis-page">
        <Skeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-page">
        <div className="card analysis-error">
          <AlertTriangle size={20} color="var(--color-error)" />
          <p>{error}</p>
          <button onClick={loadAnalysis} className="btn btn-secondary">
            <RefreshCw size={14} /> Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="analysis-page">
        <EmptyState onUpload={() => navigate('/app')} />
      </div>
    );
  }

  const analyzedLabel = relativeTime(data.timestamp);
  const analyzedFull = fullDate(data.timestamp);

  return (
    <div className="analysis-page">
      {/* Header */}
      <div className="analysis-header">
        <div>
          <div className="analysis-eyebrow">
            <Sparkles size={12} />
            Your career analysis
          </div>
          <h1 className="analysis-title">Career Analysis</h1>
          <div className="analysis-meta">
            <span className="analysis-meta-item">
              <Calendar size={13} />
              <span title={analyzedFull}>Analyzed {analyzedLabel}</span>
            </span>
            {data.pdf_name && (
              <span className="analysis-meta-item">
                <FileText size={13} />
                <span>{data.pdf_name}</span>
              </span>
            )}
            {predictedField && (
              <span className="analysis-meta-item">
                <Trophy size={13} />
                <span>{predictedField}</span>
              </span>
            )}
          </div>
        </div>
        <div className="analysis-actions">
          <button
            onClick={() => navigate('/app')}
            className="btn btn-primary analysis-cta"
          >
            <RefreshCw size={14} /> Re-analyze
          </button>
          <button
            onClick={() => setShowShare(true)}
            className="analysis-icon-btn"
            aria-label="Share this analysis"
            title="Share"
          >
            <Share2 size={16} />
          </button>
          <button
            onClick={() => setDeleteConfirm(true)}
            className="analysis-icon-btn analysis-icon-btn-danger"
            aria-label="Delete this analysis"
            title="Delete"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Hero card */}
      <motion.div
        initial="hidden" animate="visible" variants={stagger}
        className="analysis-hero"
      >
        <div className="analysis-hero-grid" />
        <motion.div variants={fadeUp} className="analysis-hero-score">
          <div className="analysis-hero-score-ring">
            <div className="analysis-hero-score-ring-track" />
            <div
              className="analysis-hero-score-ring-fill"
              style={{ '--p': `${Math.max(0, Math.min(100, resumeScore))}%` }}
            />
            <div className="analysis-hero-score-inner">
              <div className="analysis-hero-score-num">{Math.round(resumeScore)}</div>
              <div className="analysis-hero-score-denom">/ 100</div>
            </div>
          </div>
          <div className="analysis-hero-score-label">Resume score</div>
          <div
            className="analysis-hero-score-level"
            data-level={resumeScore >= 80 ? 'excellent' : resumeScore >= 60 ? 'good' : resumeScore >= 40 ? 'fair' : 'low'}
          >
            <Trophy size={11} />
            {resumeScore >= 80 ? 'Excellent' : resumeScore >= 60 ? 'Strong' : resumeScore >= 40 ? 'Getting there' : 'Needs work'}
          </div>
        </motion.div>

        <motion.div variants={fadeUp} className="analysis-hero-info">
          {resumeInfo?.name && (
            <div className="analysis-hero-identity">
              <div className="analysis-hero-avatar" aria-hidden="true">
                {resumeInfo.name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase() || '?'}
              </div>
              <div className="analysis-hero-identity-text">
                <div className="analysis-hero-name">{resumeInfo.name}</div>
                {resumeInfo.email && <div className="analysis-hero-email">{resumeInfo.email}</div>}
              </div>
            </div>
          )}

          <div className="analysis-hero-label">Target role</div>
          <h2 className="analysis-hero-role">
            {targetRole || predictedField || 'Your target role'}
          </h2>

          {predictedField && (
            <div className="analysis-hero-field-pill">
              <Sparkles size={12} /> {predictedField}
            </div>
          )}

          <div className="analysis-hero-stats">
            <div className="analysis-hero-stat" data-tone="success">
              <div className="analysis-hero-stat-icon"><CheckCircle size={16} /></div>
              <div className="analysis-hero-stat-body">
                <div className="analysis-hero-stat-value">{matchedSkills.length}</div>
                <div className="analysis-hero-stat-label">Matched skills</div>
              </div>
            </div>
            <div className="analysis-hero-stat" data-tone={missingSkills.length > 0 ? 'danger' : 'success'}>
              <div className="analysis-hero-stat-icon"><Target size={16} /></div>
              <div className="analysis-hero-stat-body">
                <div className="analysis-hero-stat-value">{missingSkills.length}</div>
                <div className="analysis-hero-stat-label">Skill gaps</div>
              </div>
            </div>
            <div className="analysis-hero-stat" data-tone="primary">
              <div className="analysis-hero-stat-icon"><Briefcase size={16} /></div>
              <div className="analysis-hero-stat-body">
                <div className="analysis-hero-stat-value">{Array.isArray(roadmap) ? roadmap.length : 0}</div>
                <div className="analysis-hero-stat-label">Roadmap steps</div>
              </div>
            </div>
            <div className="analysis-hero-stat" data-tone={matchScore >= 70 ? 'success' : matchScore >= 40 ? 'warning' : 'danger'}>
              <div className="analysis-hero-stat-icon"><TrendingUp size={16} /></div>
              <div className="analysis-hero-stat-body">
                <div className="analysis-hero-stat-value">{matchScore ?? 0}<span className="analysis-hero-stat-pct">%</span></div>
                <div className="analysis-hero-stat-label">Role match</div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Tabs */}
      <div className="analysis-tabs" role="tablist">
        {TABS.map((t) => {
          const Icon = t.icon;
          const active = activeTab === t.id;
          return (
            <button
              key={t.id}
              role="tab"
              aria-selected={active}
              onClick={() => setActiveTab(t.id)}
              className={`analysis-tab ${active ? 'analysis-tab-active' : ''}`}
            >
              <Icon size={15} />
              <span>{t.label}</span>
              {active && (
                <motion.div
                  layoutId="analysis-tab-underline"
                  className="analysis-tab-underline"
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
          className="analysis-tab-panel"
        >
          {activeTab === 'overview' && (
            <OverviewTab
              analysis={analysis}
              resumeInfo={resumeInfo}
              targetRole={targetRole}
              predictedField={predictedField}
              matchScore={matchScore}
              scoreBreakdown={scoreBreakdown}
              feedbackMsgs={feedbackMsgs}
              missingSkills={missingSkills}
            />
          )}
          {activeTab === 'skills' && (
            <SkillsTab
              matched={matchedSkills}
              gaps={missingSkills}
              filter={skillFilter}
              setFilter={setSkillFilter}
              roleSkills={roleSkills}
              targetRole={targetRole}
            />
          )}
          {activeTab === 'courses' && (
            <CoursesTab
              courses={courses}
              recommendedSkills={recommendedSkills}
              targetRole={targetRole}
            />
          )}
          {activeTab === 'matches' && (
            <MatchesTab
              matches={jobMatches}
              targetRole={targetRole}
            />
          )}
          {activeTab === 'roadmap' && <RoadmapTab roadmap={roadmap} analysisId={data?.id} />}
          {activeTab === 'market' && <MarketTab trends={trends} targetRole={targetRole} />}
          {activeTab === 'resources' && <ResourcesTab tutorials={tutorials} />}
        </motion.div>
      </AnimatePresence>

      {/* Feedback */}
      <FeedbackCard resumeInfo={resumeInfo} />

      {/* Delete confirm modal */}
      <AnimatePresence>
        {deleteConfirm && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="analysis-modal-backdrop"
            onClick={() => !deleting && setDeleteConfirm(false)}
          >
            <motion.div
              role="dialog"
              aria-modal="true"
              aria-labelledby="delete-analysis-title"
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
              className="analysis-modal"
            >
              <div className="analysis-modal-icon analysis-modal-icon-danger">
                <Trash2 size={20} color="white" />
              </div>
              <h3 id="delete-analysis-title" className="analysis-modal-title">
                Delete this analysis?
              </h3>
              <p className="analysis-modal-text">
                This will remove the current analysis from your account. Your other historical analyses are kept.
              </p>
              <div className="analysis-modal-actions">
                <button
                  onClick={() => setDeleteConfirm(false)}
                  disabled={deleting}
                  className="btn btn-secondary"
                  style={{ minHeight: '40px', flex: 1 }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="analysis-modal-danger"
                >
                  {deleting ? (
                    <><span className="analysis-spinner" /> Deleting...</>
                  ) : (
                    <><Trash2 size={14} /> Delete</>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showShare && (
          <ShareModal
            analysisId={data?.id}
            targetRole={targetRole}
            resumeName={resumeInfo?.name || data?.filename}
            onClose={() => setShowShare(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default AnalysisResult;
