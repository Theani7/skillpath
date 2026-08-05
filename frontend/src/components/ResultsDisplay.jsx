import { useState } from 'react';
import { motion } from 'framer-motion';
import api from '../services/api';
import HeaderRow from './results/HeaderRow';
import TitleBlock from './results/TitleBlock';
import ScoreOverview from './results/ScoreOverview';
import TargetMatching from './results/TargetMatching';
import MarketInsights from './results/MarketInsights';
import ScoreBreakdown from './results/ScoreBreakdown';
import MatchedSkills from './results/MatchedSkills';
import MissingSkills from './results/MissingSkills';
import MarketTrendsCard from './results/MarketTrendsCard';
import RoadmapCard from './results/RoadmapCard';
import ResourcesCard from './results/ResourcesCard';
import FeedbackList from './results/FeedbackList';
import FeedbackForm from './results/FeedbackForm';

const gridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
  gap: '20px',
  marginBottom: '20px',
};

const ResultsDisplay = ({ data, onReset }) => {
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rating, setRating] = useState(5);
  const [hoverRating, setHoverRating] = useState(0);

  if (!data) return null;
  const {
    data: resumeInfo,
    target_role,
    predicted_field,
    match_score,
    missing_skill_names,
    resume_score,
    feedback,
    videos,
    roadmap,
    trends,
    score_breakdown,
  } = data;

  const missingSkills = Array.isArray(missing_skill_names) ? missing_skill_names : [];
  const matchedSkills = Array.isArray(resumeInfo?.skills) ? resumeInfo.skills : [];
  const feedbackMsgs = Array.isArray(feedback) ? feedback : [];
  const tutorials = Array.isArray(videos?.tutorials) ? videos.tutorials : [];

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    setLoading(true);
    try {
      const res = await api.post('/api/feedback', {
        name: resumeInfo?.name || 'Anonymous',
        email: resumeInfo?.email || 'N/A',
        score: rating.toString(),
        comments: fd.get('comments') || '',
      });
      if (res.status === 200 || res.status === 201) setFeedbackSent(true);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '40px 16px 80px',
      }}
    >
      <HeaderRow onReset={onReset} targetRole={target_role} />
      <TitleBlock targetRole={target_role} />

      <ScoreOverview
        resumeScore={resume_score}
        feedbackMsgs={feedbackMsgs}
        predictedField={predicted_field}
        resumeInfo={resumeInfo}
      />

      <div style={gridStyle}>
        <TargetMatching matchScore={match_score} targetRole={target_role} />
        <MarketInsights trends={trends} />
      </div>

      {score_breakdown && Object.keys(score_breakdown).length > 0 && (
        <ScoreBreakdown scoreBreakdown={score_breakdown} />
      )}

      <div style={gridStyle}>
        <MatchedSkills matchedSkills={matchedSkills} />
        <MissingSkills missingSkills={missingSkills} />
      </div>

      {trends && (trends.growth || trends.top_skills) && (
        <MarketTrendsCard trends={trends} targetRole={target_role} />
      )}

      {Array.isArray(roadmap) && roadmap.length > 0 && (
        <RoadmapCard roadmap={roadmap} />
      )}

      {tutorials.length > 0 && (
        <ResourcesCard tutorials={tutorials} />
      )}

      {feedbackMsgs.length > 1 && (
        <FeedbackList feedbackMsgs={feedbackMsgs} />
      )}

      <FeedbackForm
        feedbackSent={feedbackSent}
        loading={loading}
        rating={rating}
        hoverRating={hoverRating}
        onRate={setRating}
        onHover={setHoverRating}
        onSubmit={handleFeedbackSubmit}
      />
    </motion.div>
  );
};

export default ResultsDisplay;
