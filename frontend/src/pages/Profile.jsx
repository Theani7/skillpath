import { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import ResultsDisplay from '../components/ResultsDisplay';
import PageLoader from '../components/Skeleton';
import { Header, StatsRow, ProfileCard, PrefsCard, ScoreChart, SkillTrends, HistoryList } from '../components/profile';

const Profile = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedResult, setSelectedResult] = useState(null);
  const savedTimer = useRef(null);

  useEffect(() => () => { if (savedTimer.current) clearTimeout(savedTimer.current); }, []);

  const [profile, setProfile] = useState({
    full_name: '', phone: '', location: '', bio: '',
    current_role: '', experience_years: '',
    linkedin_url: '', github_url: '',
  });
  const [preferences, setPreferences] = useState({
    target_role: '', timeline_months: 6,
    preferred_location: '', salary_target: 0,
  });

  const [editingProfile, setEditingProfile] = useState(false);
  const [editingPrefs, setEditingPrefs] = useState(false);
  const [profileDraft, setProfileDraft] = useState(profile);
  const [prefsDraft, setPrefsDraft] = useState(preferences);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPrefs, setSavingPrefs] = useState(false);
  const [savedProfile, setSavedProfile] = useState(false);
  const [savedPrefs, setSavedPrefs] = useState(false);
  const [profileError, setProfileError] = useState('');
  const [prefsError, setPrefsError] = useState('');
  const [skillTrends, setSkillTrends] = useState(null);

  useEffect(() => {
    if (!user) return;
    const controller = new AbortController();
    const { signal } = controller;
    const fetchData = async () => {
      try {
        const [historyRes, profileRes, prefRes, trendsRes] = await Promise.all([
          api.get('/api/user/history', { signal }),
          api.get('/api/user/profile', { signal }),
          api.get('/api/user/preferences', { signal }),
          api.get('/api/user/skill-trends', { signal }),
        ]);
        const sorted = (historyRes.data.history || []).sort(
          (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
        );
        setHistory(sorted);
        const p = {
          full_name: profileRes.data.profile?.full_name || user?.full_name || user?.username || '',
          phone: profileRes.data.profile?.phone || '',
          location: profileRes.data.profile?.location || '',
          bio: profileRes.data.profile?.bio || '',
          current_role: profileRes.data.profile?.current_role || '',
          experience_years: profileRes.data.profile?.experience_years || '',
          linkedin_url: profileRes.data.profile?.linkedin_url || '',
          github_url: profileRes.data.profile?.github_url || '',
        };
        const pr = {
          target_role: prefRes.data.preferences?.target_role || '',
          timeline_months: prefRes.data.preferences?.timeline_months || 6,
          preferred_location: prefRes.data.preferences?.preferred_location || '',
          salary_target: prefRes.data.preferences?.salary_target || 0,
        };
        setProfile(p);
        setProfileDraft(p);
        setPreferences(pr);
        setPrefsDraft(pr);
        setSkillTrends(trendsRes.data);
      } catch (err) {
        if (err?.name !== 'CanceledError' && err?.code !== 'ERR_CANCELED') {
          console.error(err);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    return () => controller.abort();
  }, [user]);

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    setProfileError('');
    try {
      await api.put('/api/user/profile', profileDraft);
      setProfile(profileDraft);
      setEditingProfile(false);
      setSavedProfile(true);
      if (savedTimer.current) clearTimeout(savedTimer.current);
      savedTimer.current = setTimeout(() => setSavedProfile(false), 2200);
    } catch (err) {
      console.error(err);
      setProfileError('Failed to save profile. Please try again.');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleSavePrefs = async () => {
    setSavingPrefs(true);
    setPrefsError('');
    try {
      const payload = {
        ...prefsDraft,
        salary_target: Number(prefsDraft.salary_target) || 0,
        timeline_months: Number(prefsDraft.timeline_months) || 6,
      };
      await api.put('/api/user/preferences', payload);
      setPreferences(payload);
      setEditingPrefs(false);
      setSavedPrefs(true);
      if (savedTimer.current) clearTimeout(savedTimer.current);
      savedTimer.current = setTimeout(() => setSavedPrefs(false), 2200);
    } catch (err) {
      console.error(err);
      setPrefsError('Failed to save preferences. Please try again.');
    } finally {
      setSavingPrefs(false);
    }
  };

  if (loading) return <PageLoader />;

  if (selectedResult) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: '32px 16px' }}>
        <div className="container" style={{ maxWidth: '900px' }}>
          <button
            onClick={() => setSelectedResult(null)}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '6px',
              background: 'transparent', border: 'none', cursor: 'pointer',
              color: 'var(--color-text-muted)', fontSize: '14px', fontWeight: 500,
              padding: '8px 12px', borderRadius: 'var(--radius-md)',
              marginBottom: '16px',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--color-bg)';
              e.currentTarget.style.color = 'var(--color-text)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--color-text-muted)';
            }}
          >
            <ArrowRight size={16} style={{ transform: 'rotate(180deg)' }} /> Back to Profile
          </button>
          <ResultsDisplay data={selectedResult} onReset={() => setSelectedResult(null)} />
        </div>
      </motion.div>
    );
  }

  const chartData = history.map((item) => ({
    date: new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    score: Math.round(item.resume_score || 0),
  }));

  const latestScore = history.length > 0 ? Math.round(history[history.length - 1].resume_score) : 0;
  const avgScore = history.length > 0
    ? Math.round(history.reduce((a, b) => a + (b.resume_score || 0), 0) / history.length)
    : 0;
  const totalAnalyses = history.length;
  const bestScore = history.length > 0
    ? Math.round(Math.max(...history.map((h) => h.resume_score || 0)))
    : 0;

  const getScoreColor = (s) => {
    if (s >= 75) return 'var(--color-success)';
    if (s >= 50) return '#D97706';
    return 'var(--color-error)';
  };

  const avatarLetter = (profile.full_name || user?.username || 'U').charAt(0).toUpperCase();

  return (
    <div style={{
      minHeight: '100%',
      background: 'var(--color-bg)',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '-180px', right: '-150px', width: '480px', height: '480px',
        borderRadius: '50%', opacity: 0.05, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-primary) 0%, transparent 70%)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-220px', left: '-180px', width: '500px', height: '500px',
        borderRadius: '50%', opacity: 0.04, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-secondary) 0%, transparent 70%)',
      }} />

      <div className="container" style={{ position: 'relative', zIndex: 1, maxWidth: '1100px' }}>
        <Header
          user={user} profile={profile} avatarLetter={avatarLetter}
          savedProfile={savedProfile} savedPrefs={savedPrefs}
          profileError={profileError} prefsError={prefsError}
          setProfileError={setProfileError} setPrefsError={setPrefsError}
        />

        <StatsRow
          hasHistory={history.length > 0}
          latestScore={latestScore} bestScore={bestScore}
          avgScore={avgScore} totalAnalyses={totalAnalyses}
          getScoreColor={getScoreColor}
        />

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
          gap: '16px', marginBottom: '24px',
        }}>
          <ProfileCard
            profile={profile} profileDraft={profileDraft}
            editingProfile={editingProfile} savingProfile={savingProfile}
            setEditingProfile={setEditingProfile} setProfileDraft={setProfileDraft}
            handleSaveProfile={handleSaveProfile}
          />
          <PrefsCard
            preferences={preferences} prefsDraft={prefsDraft}
            editingPrefs={editingPrefs} savingPrefs={savingPrefs}
            setEditingPrefs={setEditingPrefs} setPrefsDraft={setPrefsDraft}
            handleSavePrefs={handleSavePrefs}
          />
        </div>

        {history.length > 0 && <ScoreChart chartData={chartData} />}

        {skillTrends && skillTrends.trends && skillTrends.trends.length > 0 && (
          <SkillTrends skillTrends={skillTrends} />
        )}

        <HistoryList history={history} getScoreColor={getScoreColor} onSelect={setSelectedResult} />
      </div>
    </div>
  );
};

export default Profile;
