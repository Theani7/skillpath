import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, ChevronDown, ChevronUp, Check, Square, ExternalLink, BookOpen, Video, FileText, Award } from 'lucide-react';
import api from '../services/api';
import type { RoadmapPhase } from '../types';

type RoadmapStepProps = {
  step: RoadmapPhase;
  index: number;
  isLast: boolean;
  analysisId: number | undefined;
  progress: Record<string, boolean>;
  onToggle: (phaseIndex: number, taskIndex: number) => void;
};

const RoadmapStep = ({ step, index, isLast, progress, onToggle }: RoadmapStepProps) => {
  const [isExpanded, setIsExpanded] = useState(index === 0);

  const getTaskDone = (taskIndex: number) => {
    const key = `${index}:${taskIndex}`;
    return progress[key] || false;
  };

  return (
    <div style={{ position: 'relative', paddingLeft: '32px', marginBottom: isLast ? 0 : '20px' }}>
      {!isLast && (
        <div style={{
          position: 'absolute', left: '11px', top: '24px', bottom: '-20px',
          width: '2px', background: 'var(--color-border)',
        }} />
      )}

      <div
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          position: 'absolute', left: '4px', top: '6px',
          width: '16px', height: '16px', borderRadius: '50%',
          background: 'var(--color-primary)',
          border: '3px solid var(--color-surface)',
          boxShadow: '0 0 0 2px var(--indigo-100)',
          cursor: 'pointer', zIndex: 1,
        }}
      />

      <div
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: '14px 16px',
          cursor: 'pointer',
          background: 'var(--color-surface)',
          transition: 'border-color 150ms ease, box-shadow 150ms ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = 'var(--indigo-200)';
          e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.04)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'var(--color-border)';
          e.currentTarget.style.boxShadow = 'none';
        }}
      >
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
          gap: '12px',
        }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px',
            }}>
              <span style={{
                fontSize: '10px', fontWeight: 'var(--font-bold)',
                color: 'var(--color-primary)', textTransform: 'uppercase',
                letterSpacing: '0.06em',
              }}>
                Phase {step.step}
              </span>
              {Array.isArray(step.action_items) && step.action_items.length > 0 && (
                <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                  {step.action_items.filter((_, i) => getTaskDone(i)).length} / {step.action_items.length} tasks
                </span>
              )}
            </div>
            <h4 style={{
              fontSize: '15px', fontWeight: 'var(--font-bold)',
              color: 'var(--color-text)', margin: 0, lineHeight: 1.4,
            }}>
              {step.title}
            </h4>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
            {step.duration && (
              <span style={{
                display: 'inline-flex', alignItems: 'center', gap: '4px',
                fontSize: '11px', fontWeight: 500,
                color: 'var(--color-text-muted)',
                padding: '4px 8px', borderRadius: 'var(--radius-md)',
                background: 'var(--color-bg)',
              }}>
                <Clock size={11} /> {step.duration}
              </span>
            )}
            {isExpanded
              ? <ChevronUp size={16} color="var(--color-text-muted)" />
              : <ChevronDown size={16} color="var(--color-text-muted)" />}
          </div>
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              style={{ overflow: 'hidden' }}
            >
              <div style={{
                marginTop: '14px', paddingTop: '14px',
                borderTop: '1px solid var(--color-border)',
              }}>
                {Array.isArray(step.skills) && step.skills.length > 0 && (
                  <div style={{ marginBottom: '14px' }}>
                    <h5 style={{
                      fontSize: '10px', fontWeight: 'var(--font-bold)',
                      color: 'var(--color-text-muted)', textTransform: 'uppercase',
                      letterSpacing: '0.06em', margin: '0 0 8px',
                    }}>
                      Target Skills
                    </h5>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {step.skills.map((skill, i) => (
                        <span key={i} style={{
                          padding: '4px 10px', borderRadius: 'var(--radius-md)',
                          background: 'var(--indigo-50)', color: 'var(--color-primary)',
                          fontSize: '12px', fontWeight: 'var(--font-semibold)',
                        }}>
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {Array.isArray(step.action_items) && step.action_items.length > 0 && (
                  <div style={{ marginBottom: step.resources && step.resources.length > 0 ? '16px' : 0 }}>
                    <h5 style={{
                      fontSize: '10px', fontWeight: 'var(--font-bold)',
                      color: 'var(--color-text-muted)', textTransform: 'uppercase',
                      letterSpacing: '0.06em', margin: '0 0 8px',
                    }}>
                      Action Items
                    </h5>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {step.action_items.map((action, i) => {
                        const isDone = getTaskDone(i);
                        return (
                          <div
                            key={i}
                            onClick={(e) => { e.stopPropagation(); onToggle(index, i); }}
                            style={{
                              display: 'flex', alignItems: 'flex-start', gap: '10px',
                              padding: '10px 12px', borderRadius: 'var(--radius-md)',
                              background: isDone ? 'var(--emerald-50)' : 'var(--color-bg)',
                              border: `1px solid ${isDone ? '#A7F3D0' : 'var(--color-border)'}`,
                              cursor: 'pointer', transition: 'all 150ms ease',
                            }}
                          >
                            <div style={{ marginTop: '2px', flexShrink: 0 }}>
                              {isDone
                                ? <Check size={14} color="var(--color-success)" strokeWidth={3} />
                                : <Square size={14} color="var(--color-text-light)" />}
                            </div>
                            <span style={{
                              fontSize: '13px', lineHeight: 1.5,
                              color: isDone ? 'var(--color-text-muted)' : 'var(--color-text)',
                              textDecoration: isDone ? 'line-through' : 'none',
                            }}>
                              {action}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {Array.isArray(step.resources) && step.resources.length > 0 && (
                  <div>
                    <h5 style={{
                      fontSize: '10px', fontWeight: 'var(--font-bold)',
                      color: 'var(--color-text-muted)', textTransform: 'uppercase',
                      letterSpacing: '0.06em', margin: '0 0 8px',
                    }}>
                      Learning Resources
                    </h5>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {step.resources.map((resource, i) => {
                        const iconMap: Record<string, typeof FileText> = { docs: FileText, video: Video, course: BookOpen, cert: Award };
                        const Icon = iconMap[resource.type] || ExternalLink;
                        return (
                          <a
                            key={i}
                            href={resource.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            style={{
                              display: 'flex', alignItems: 'center', gap: '10px',
                              padding: '10px 12px', borderRadius: 'var(--radius-md)',
                              background: 'var(--color-surface)',
                              border: '1px solid var(--color-border)',
                              textDecoration: 'none', transition: 'all 150ms ease',
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.borderColor = 'var(--color-primary)';
                              e.currentTarget.style.background = 'var(--color-bg)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.borderColor = 'var(--color-border)';
                              e.currentTarget.style.background = 'var(--color-surface)';
                            }}
                          >
                            <Icon size={14} style={{ color: 'var(--color-secondary)', flexShrink: 0 }} />
                            <span style={{
                              fontSize: '13px', color: 'var(--color-text)',
                              flex: 1, lineHeight: 1.4,
                            }}>
                              {resource.title}
                            </span>
                            <ExternalLink size={12} style={{ color: 'var(--color-text-light)', flexShrink: 0 }} />
                          </a>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

type Props = {
  path: RoadmapPhase[];
  analysisId: number | undefined;
};

const Roadmap = ({ path, analysisId }: Props) => {
  const [progress, setProgress] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!analysisId) return;
    const loadProgress = async () => {
      try {
        const res = await api.get(`/api/user/roadmap-progress?analysis_id=${analysisId}`);
        setProgress(res.data.progress || {});
      } catch {
        // ignore
      }
    };
    loadProgress();
  }, [analysisId]);

  const handleToggle = useCallback(async (phaseIndex: number, taskIndex: number) => {
    const key = `${phaseIndex}:${taskIndex}`;

    setProgress(prev => {
      const newCompleted = !prev[key];
      api.put('/api/user/roadmap-progress', {
        analysis_id: analysisId,
        phase_index: phaseIndex,
        task_index: taskIndex,
        completed: newCompleted,
      }).catch(() => {
        setProgress(p => ({ ...p, [key]: !newCompleted }));
      });
      return { ...prev, [key]: newCompleted };
    });
  }, [analysisId]);

  if (!Array.isArray(path) || path.length === 0) return null;

  return (
    <div>
      {path.map((step, index) => (
        <RoadmapStep
          key={index}
          step={step}
          index={index}
          isLast={index === path.length - 1}
          analysisId={analysisId}
          progress={progress}
          onToggle={handleToggle}
        />
      ))}
    </div>
  );
};

export default Roadmap;
