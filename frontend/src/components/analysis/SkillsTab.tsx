import { Check, CheckCircle, Circle, ListChecks, Search, Target, XCircle } from 'lucide-react';

type MatchedSkill = { skill: string; is_required: boolean } | string;
type RoleSkill = { skill: string; is_required: boolean };

type Props = {
  matched: MatchedSkill[];
  gaps: string[];
  filter: string;
  setFilter: (value: string) => void;
  roleSkills: RoleSkill[];
  targetRole: string;
};

const SkillsTab = ({ matched, gaps, filter, setFilter, roleSkills, targetRole }: Props) => {
  const filterMatch = (s: MatchedSkill): boolean => {
    const name = typeof s === 'string' ? s : s.skill;
    return name.toLowerCase().includes(filter.toLowerCase());
  };
  const visibleMatched = filter ? matched.filter(filterMatch) : matched;
  const visibleGaps = filter ? gaps.filter(filterMatch) : gaps;

  const totalRoleSkills = roleSkills.length;
  const matchedCount = matched.length;
  const gapCount = gaps.length;
  const coreSkills = roleSkills.filter(r => r.is_required);
  const niceSkills = roleSkills.filter(r => !r.is_required);
  const matchedNames = new Set(matched.map(m => (typeof m === 'string' ? m : m.skill).toLowerCase()));
  const coreMatched = coreSkills.filter(s => matchedNames.has(s.skill.toLowerCase())).length;
  const niceMatched = niceSkills.filter(s => matchedNames.has(s.skill.toLowerCase())).length;
  const coveragePct = totalRoleSkills > 0 ? Math.round((matchedCount / totalRoleSkills) * 100) : 0;

  const allRoleSkills = roleSkills.map(rs => ({
    name: rs.skill,
    isRequired: rs.is_required,
    matched: matchedNames.has(rs.skill.toLowerCase()),
  })).sort((a, b) => {
    if (a.isRequired !== b.isRequired) return a.isRequired ? -1 : 1;
    if (a.matched !== b.matched) return a.matched ? -1 : 1;
    return a.name.localeCompare(b.name);
  });

  const donutSize = 140;
  const donutStroke = 14;
  const donutRadius = (donutSize - donutStroke) / 2;
  const donutCircumference = 2 * Math.PI * donutRadius;
  const donutOffset = donutCircumference * (1 - coveragePct / 100);

  return (
    <div className="analysis-skills">
      <div className="analysis-search">
        <Search size={16} color="var(--color-text-light)" />
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter skills..."
          aria-label="Filter skills"
        />
        {filter && (
          <button
            type="button"
            onClick={() => setFilter('')}
            className="analysis-search-clear"
            aria-label="Clear filter"
          >
            <XCircle size={14} />
          </button>
        )}
      </div>

      <div className="analysis-skills-coverage">
        <div className="analysis-skills-donut-wrap">
          <svg width={donutSize} height={donutSize} viewBox={`0 0 ${donutSize} ${donutSize}`}>
            <circle
              cx={donutSize / 2}
              cy={donutSize / 2}
              r={donutRadius}
              fill="none"
              stroke="var(--color-border)"
              strokeWidth={donutStroke}
            />
            <circle
              cx={donutSize / 2}
              cy={donutSize / 2}
              r={donutRadius}
              fill="none"
              stroke={coveragePct >= 70 ? 'var(--color-success)' : coveragePct >= 40 ? 'var(--color-secondary)' : 'var(--color-error)'}
              strokeWidth={donutStroke}
              strokeDasharray={donutCircumference}
              strokeDashoffset={donutOffset}
              strokeLinecap="round"
              transform={`rotate(-90 ${donutSize / 2} ${donutSize / 2})`}
              style={{ transition: 'stroke-dashoffset 600ms ease' }}
            />
          </svg>
          <div className="analysis-skills-donut-text">
            <span className="analysis-skills-donut-pct">{coveragePct}%</span>
            <span className="analysis-skills-donut-label">coverage</span>
          </div>
        </div>

        <div className="analysis-skills-stats">
          <div className="analysis-skills-stat-item">
            <span className="analysis-skills-stat-num">{totalRoleSkills}</span>
            <span className="analysis-skills-stat-label">Total Skills</span>
          </div>
          <div className="analysis-skills-stat-item analysis-skills-stat-match">
            <span className="analysis-skills-stat-num">{matchedCount}</span>
            <span className="analysis-skills-stat-label">Matched</span>
          </div>
          <div className="analysis-skills-stat-item analysis-skills-stat-gap">
            <span className="analysis-skills-stat-num">{gapCount}</span>
            <span className="analysis-skills-stat-label">Gaps</span>
          </div>
          <div className="analysis-skills-stat-divider" />
          <div className="analysis-skills-stat-item">
            <span className="analysis-skills-stat-num" style={{ color: 'var(--color-secondary)' }}>{coreMatched}</span>
            <span className="analysis-skills-stat-label">Core Matched</span>
          </div>
          <div className="analysis-skills-stat-item">
            <span className="analysis-skills-stat-num" style={{ color: 'var(--color-primary)' }}>{niceMatched}</span>
            <span className="analysis-skills-stat-label">Nice-to-Have Matched</span>
          </div>
        </div>
      </div>

      {!filter && allRoleSkills.length > 0 && (
        <div className="card analysis-skills-card">
          <div className="analysis-skills-head">
            <ListChecks size={18} color="var(--color-primary)" />
            <h3>All Role Skills for {targetRole || 'Your Role'}</h3>
            <span className="analysis-skills-count" style={{ background: 'var(--indigo-50)', color: 'var(--color-primary)' }}>
              {matchedCount}/{totalRoleSkills}
            </span>
          </div>
          <div className="analysis-skills-checklist">
            {allRoleSkills.map(s => (
              <div key={s.name} className={`analysis-skills-checkitem ${s.matched ? 'analysis-skills-checkitem--matched' : 'analysis-skills-checkitem--gap'}`}>
                <div className="analysis-skills-checkicon">
                  {s.matched ? <CheckCircle size={16} color="var(--color-success)" /> : <Circle size={16} color="var(--color-text-light)" />}
                </div>
                <span className="analysis-skills-checkname">{s.name}</span>
                {s.isRequired && <span className="analysis-tag-badge">Core</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="analysis-skills-grid">
        <div className="card analysis-skills-card">
          <div className="analysis-skills-head analysis-skills-head-match">
            <CheckCircle size={18} color="var(--color-success)" />
            <h3>Matched Skills</h3>
            <span className="analysis-skills-count analysis-skills-count-match">
              {visibleMatched.length}{filter ? ` / ${matched.length}` : ''}
            </span>
          </div>
          <div className="analysis-skills-body">
            {visibleMatched.length === 0 ? (
              <p className="analysis-empty-text">
                {filter ? 'No matches for that filter.' : 'No matched skills identified yet.'}
              </p>
            ) : (
              <div className="analysis-tags">
                {visibleMatched.map((s) => {
                  const name = typeof s === 'string' ? s : s.skill;
                  const isRequired = typeof s === 'object' && s.is_required;
                  return (
                    <span key={name} className={`analysis-tag analysis-tag-match${isRequired ? ' analysis-tag-core' : ''}`}>
                      <Check size={11} /> {name}
                      {isRequired && <span className="analysis-tag-badge">Core</span>}
                    </span>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        <div className="card analysis-skills-card">
          <div className="analysis-skills-head analysis-skills-head-gap">
            <XCircle size={18} color="var(--color-error)" />
            <h3>Skill Gaps</h3>
            <span className="analysis-skills-count analysis-skills-count-gap">
              {visibleGaps.length}{filter ? ` / ${gaps.length}` : ''}
            </span>
          </div>
          <div className="analysis-skills-body">
            {visibleGaps.length === 0 ? (
              <p className="analysis-empty-text">
                {filter ? 'No matches for that filter.' : 'All clear — no major gaps identified.'}
              </p>
            ) : (
              <div className="analysis-tags">
                {visibleGaps.map((s) => (
                  <span key={s} className="analysis-tag analysis-tag-gap">
                    <Target size={11} /> {s}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {!filter && (
        <div className="analysis-skills-legend">
          <span className="analysis-skills-legend-title">Skill Types:</span>
          <span className="analysis-skills-legend-item">
            <span className="analysis-skills-legend-dot analysis-skills-legend-dot--core" />
            Core (required) — counts 2x toward match score
          </span>
          <span className="analysis-skills-legend-item">
            <span className="analysis-skills-legend-dot analysis-skills-legend-dot--nice" />
            Nice-to-have — adds incremental match points
          </span>
        </div>
      )}
    </div>
  );
};

export { SkillsTab };
