import { motion } from 'framer-motion';
import {
  Award, Briefcase, FileText, Globe, GraduationCap, Lightbulb, Mail,
  Map, MessageSquare, Phone, Target, User, Zap,
} from 'lucide-react';
import type { AnalysisResponse, ResumeData, ScoreBreakdown } from '../../types';

type Props = {
  analysis: AnalysisResponse | undefined;
  resumeInfo: ResumeData | undefined;
  targetRole: string;
  predictedField: string;
  matchScore: number;
  scoreBreakdown: ScoreBreakdown | null;
  feedbackMsgs: string[];
  missingSkills: string[];
};

const OverviewTab = ({ analysis, resumeInfo, targetRole, predictedField, matchScore, scoreBreakdown, feedbackMsgs, missingSkills }: Props) => {
  const roleSkills = Array.isArray(analysis?.data?.matched_role_skills) ? analysis.data.matched_role_skills : [];
  const requiredMatched = roleSkills.filter(s => (typeof s === 'object' ? s.is_required : false)).length;
  const totalRequired = 6;
  const roadmap = Array.isArray(analysis?.roadmap) ? analysis.roadmap : [];
  const recommendedSkills = Array.isArray(analysis?.recommended_skills) ? analysis.recommended_skills : [];
  const name = resumeInfo?.name || 'Unknown';
  const email = resumeInfo?.email || '';
  const phone = resumeInfo?.mobile_number || '';
  const pages = resumeInfo?.no_of_pages;
  const summary = resumeInfo?.summary || '';
  const experience = resumeInfo?.experience_blocks || [];
  const education = resumeInfo?.education_blocks || [];
  const certifications = resumeInfo?.certifications || [];
  const languages = resumeInfo?.languages || [];
  const confidence = resumeInfo?.confidence_score;

  const breakdownEntries = scoreBreakdown ? Object.entries(scoreBreakdown) : [];
  const categoryLabels: Record<string, string> = {
    summary: 'Summary',
    education: 'Education',
    experience: 'Experience',
    skills: 'Skills',
    contact_info: 'Contact',
  };
  const categoryIcons: Record<string, typeof FileText> = {
    summary: FileText,
    education: GraduationCap,
    experience: Briefcase,
    skills: Zap,
    contact_info: Mail,
  };

  const nextSteps: { icon: typeof Target; color: string; bg: string; title: string; description: string; priority: string }[] = [];
  if (missingSkills.length > 0) {
    nextSteps.push({
      icon: Target,
      color: 'var(--color-secondary)',
      bg: '#FFF7ED',
      title: `Learn ${missingSkills[0]}`,
      description: `${missingSkills[0]} is a core skill for ${targetRole || 'your target role'}. Add it to significantly boost your match score.`,
      priority: 'high',
    });
  }
  if (feedbackMsgs.length > 0) {
    nextSteps.push({
      icon: MessageSquare,
      color: 'var(--color-primary)',
      bg: 'var(--indigo-50)',
      title: 'Improve your resume',
      description: feedbackMsgs[0],
      priority: 'medium',
    });
  }
  if (recommendedSkills.length > 0) {
    nextSteps.push({
      icon: Zap,
      color: '#059669',
      bg: '#ECFDF5',
      title: 'Build these skills',
      description: `Focus on: ${recommendedSkills.slice(0, 4).join(', ')}`,
      priority: 'medium',
    });
  }
  if (roadmap.length > 0) {
    nextSteps.push({
      icon: Map,
      color: '#7C3AED',
      bg: '#F5F3FF',
      title: 'Follow your career roadmap',
      description: `${roadmap.length}-step plan tailored to close your skill gaps for ${targetRole || 'your target role'}.`,
      priority: 'low',
    });
  }

  return (
    <div className="analysis-overview">
      <div className="card analysis-profile-card">
        <div className="analysis-card-head">
          <div className="analysis-card-icon" style={{ background: 'var(--indigo-50)', color: 'var(--color-primary)' }}>
            <User size={18} />
          </div>
          <h3>Resume profile</h3>
        </div>
        <div className="analysis-profile-grid">
          <div className="analysis-profile-main">
            <div className="analysis-profile-name">{name}</div>
            <div className="analysis-profile-contact">
              {email && <span><Mail size={13} /> {email}</span>}
              {phone && <span><Phone size={13} /> {phone}</span>}
            </div>
            {summary && <p className="analysis-profile-summary">{summary}</p>}
          </div>
          <div className="analysis-profile-meta">
            {predictedField && (
              <div className="analysis-profile-meta-item">
                <span className="analysis-profile-meta-label">Field</span>
                <span className="analysis-profile-meta-value">{predictedField}</span>
              </div>
            )}
            {targetRole && (
              <div className="analysis-profile-meta-item">
                <span className="analysis-profile-meta-label">Target</span>
                <span className="analysis-profile-meta-value">{targetRole}</span>
              </div>
            )}
            {pages && (
              <div className="analysis-profile-meta-item">
                <span className="analysis-profile-meta-label">Pages</span>
                <span className="analysis-profile-meta-value">{pages}</span>
              </div>
            )}
            {confidence != null && (
              <div className="analysis-profile-meta-item">
                <span className="analysis-profile-meta-label">Confidence</span>
                <span className="analysis-profile-meta-value">{confidence}%</span>
              </div>
            )}
          </div>
        </div>
        {(experience.length > 0 || education.length > 0 || certifications.length > 0 || languages.length > 0) && (
          <div className="analysis-profile-tags">
            {experience.length > 0 && (
              <span className="analysis-profile-tag"><Briefcase size={12} /> {experience.length} role{experience.length !== 1 ? 's' : ''}</span>
            )}
            {education.length > 0 && (
              <span className="analysis-profile-tag"><GraduationCap size={12} /> {education.length} degree{education.length !== 1 ? 's' : ''}</span>
            )}
            {certifications.length > 0 && (
              <span className="analysis-profile-tag"><Award size={12} /> {certifications.length} cert{certifications.length !== 1 ? 's' : ''}</span>
            )}
            {languages.length > 0 && (
              <span className="analysis-profile-tag"><Globe size={12} /> {languages.length} language{languages.length !== 1 ? 's' : ''}</span>
            )}
          </div>
        )}
      </div>

      <div className="analysis-overview-grid">
        <div className="card analysis-match">
          <div className="analysis-card-head">
            <div className="analysis-card-icon" style={{ background: 'var(--emerald-50)', color: 'var(--color-success)' }}>
              <Target size={18} />
            </div>
            <h3>Role match</h3>
          </div>
          <div className="analysis-match-body">
            <div className="analysis-match-ring">
              <svg viewBox="0 0 120 120" className="analysis-match-ring-svg">
                <defs>
                  <linearGradient id="matchRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="var(--color-primary)" />
                    <stop offset="100%" stopColor="var(--color-secondary)" />
                  </linearGradient>
                </defs>
                <circle cx="60" cy="60" r="50" fill="none" stroke="var(--color-border)" strokeWidth="10" />
                <motion.circle
                  cx="60" cy="60" r="50" fill="none"
                  stroke="url(#matchRingGrad)" strokeWidth="10" strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 50}
                  initial={{ strokeDashoffset: 2 * Math.PI * 50 }}
                  animate={{ strokeDashoffset: 2 * Math.PI * 50 * (1 - (matchScore ?? 0) / 100) }}
                  transition={{ duration: 1.1, ease: 'easeOut' }}
                  transform="rotate(-90 60 60)"
                />
              </svg>
              <div className="analysis-match-ring-text">
                <div className="analysis-match-ring-num">{matchScore ?? 0}<span>%</span></div>
              </div>
            </div>
            <div className="analysis-match-meta">
              <div className="analysis-match-label">
                alignment with <strong>{targetRole || 'target role'}</strong>
              </div>
              <div
                className="analysis-match-level"
                data-level={matchScore >= 75 ? 'excellent' : matchScore >= 50 ? 'good' : matchScore >= 25 ? 'fair' : 'low'}
              >
                {matchScore >= 75 ? 'Strong match' : matchScore >= 50 ? 'Good match' : matchScore >= 25 ? 'Partial match' : 'Low match'}
              </div>
              <div className="analysis-match-stats">
                <div className="analysis-match-stat">
                  <span className="analysis-match-stat-num">{requiredMatched}</span>
                  <span className="analysis-match-stat-label">of {totalRequired} core</span>
                </div>
                <div className="analysis-match-stat">
                  <span className="analysis-match-stat-num">{missingSkills.length}</span>
                  <span className="analysis-match-stat-label">gaps</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {breakdownEntries.length > 0 && (
          <div className="card analysis-breakdown-redesigned">
            <div className="analysis-card-head">
              <div className="analysis-card-icon" style={{ background: 'var(--indigo-50)', color: 'var(--color-primary)' }}>
                <Award size={18} />
              </div>
              <h3>Score breakdown</h3>
            </div>
            <div className="analysis-breakdown-cards">
              {breakdownEntries.map(([key, val], idx) => {
                const score = val.score ?? 0;
                const weight = val.weight ?? 25;
                const pct = weight > 0 ? Math.round((score / weight) * 100) : 0;
                const Icon = categoryIcons[key] || FileText;
                const status = pct >= 80 ? 'good' : pct >= 50 ? 'warn' : 'bad';
                return (
                  <motion.div
                    key={key}
                    className="analysis-breakdown-item"
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, delay: idx * 0.06 }}
                  >
                    <div className="analysis-breakdown-item-head">
                      <div className={`analysis-breakdown-item-icon analysis-breakdown-item-icon-${status}`}>
                        <Icon size={14} />
                      </div>
                      <span className="analysis-breakdown-item-label">{categoryLabels[key] || key}</span>
                      <span className="analysis-breakdown-item-score">{score}/{weight}</span>
                    </div>
                    <div className="analysis-breakdown-item-bar">
                      <motion.div
                        className={`analysis-breakdown-item-fill analysis-breakdown-item-fill-${status}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 0.7, ease: 'easeOut', delay: 0.1 + idx * 0.06 }}
                      />
                    </div>
                    {val.evidence && val.evidence.length > 0 && (
                      <div className="analysis-breakdown-evidence">
                        {val.evidence.slice(0, 2).map((e: string, i: number) => (
                          <span key={i} className="analysis-breakdown-evidence-item">{typeof e === 'string' ? e.substring(0, 60) : ''}</span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {nextSteps.length > 0 && (
        <div className="card analysis-next-steps-card">
          <div className="analysis-card-head">
            <div className="analysis-card-icon" style={{ background: '#FFF7ED', color: 'var(--color-secondary)' }}>
              <Lightbulb size={18} />
            </div>
            <h3>Recommended next steps</h3>
          </div>
          <div className="analysis-next-steps-list">
            {nextSteps.map((step, idx) => {
              const StepIcon = step.icon;
              return (
                <motion.div
                  key={idx}
                  className="analysis-next-step-item"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: idx * 0.08 }}
                >
                  <div className="analysis-next-step-icon" style={{ background: step.bg, color: step.color }}>
                    <StepIcon size={16} />
                  </div>
                  <div className="analysis-next-step-content">
                    <div className="analysis-next-step-title">{step.title}</div>
                    <div className="analysis-next-step-desc">{step.description}</div>
                  </div>
                  <span className={`analysis-next-step-priority analysis-next-step-priority-${step.priority}`}>
                    {step.priority}
                  </span>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export { OverviewTab };
