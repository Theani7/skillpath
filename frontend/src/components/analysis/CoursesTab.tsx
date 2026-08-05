import { ArrowRight, Check, GraduationCap, Lightbulb } from 'lucide-react';
import { pill, PLATFORM_STYLES, detectPlatform } from './analysisUtils';
import type { CourseRef } from '../../types';

type CourseLike = Partial<CourseRef> & {
  course_name?: string;
  course_url?: string;
};

type Props = {
  courses: CourseLike[];
  recommendedSkills: string[];
  targetRole: string;
};

const CoursesTab = ({ courses, recommendedSkills, targetRole }: Props) => {
  if (!Array.isArray(courses) || courses.length === 0) {
    return (
      <div className="card analysis-empty">
        <GraduationCap size={24} color="var(--color-text-light)" />
        <h3>No courses available</h3>
        <p>Course recommendations will appear here once your resume is analyzed.</p>
      </div>
    );
  }

  return (
    <div className="card analysis-resources-card">
      <div className="analysis-card-head">
        <div className="analysis-card-icon" style={{ background: 'var(--indigo-50)', color: 'var(--color-primary)' }}>
          <GraduationCap size={18} />
        </div>
        <div>
          <h3>Recommended courses</h3>
          <p className="analysis-card-sub">
            {targetRole ? `Curated courses for ${targetRole}` : 'Curated courses to boost your skills'}
          </p>
        </div>
        <span style={pill('var(--indigo-50)', 'var(--color-primary)')}>
          {courses.length} course{courses.length === 1 ? '' : 's'}
        </span>
      </div>

      {recommendedSkills && recommendedSkills.length > 0 && (
        <div style={{ padding: '0 20px 16px', borderBottom: '1px solid var(--color-border)' }}>
          <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '0 0 8px' }}>
            <Lightbulb size={14} style={{ display: 'inline', verticalAlign: '-2px', marginRight: '4px' }} />
            Because you're targeting <strong>{targetRole}</strong>, focus on these skills:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {recommendedSkills.slice(0, 8).map((skill) => (
              <span key={skill} style={pill('var(--emerald-50)', 'var(--color-success)')}>
                <Check size={10} /> {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="analysis-resources-grid">
        {courses.map((course, i) => {
          const url = course.url || course.course_url;
          const platform = detectPlatform(url);
          const style = PLATFORM_STYLES[platform];
          return (
            <a
              key={i}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="analysis-resource-card"
            >
              <div className="analysis-resource-thumb" style={{ background: style.gradient }}>
                <GraduationCap size={22} color="white" />
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
                <span className="analysis-resource-tag">Course</span>
                <h4 className="analysis-resource-title">{course.name || course.course_name}</h4>
                <div className="analysis-resource-foot">
                  View course
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

export { CoursesTab };
