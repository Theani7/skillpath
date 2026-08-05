import {  Layers, Target, GraduationCap, Briefcase, Compass, TrendingUp, BookOpen,} from 'lucide-react';const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  visible: (i = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.45, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] },
  }),
};

const stagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const TABS = [
  { id: 'overview',  label: 'Overview',  icon: Layers },
  { id: 'skills',    label: 'Skills',    icon: Target },
  { id: 'courses',   label: 'Courses',   icon: GraduationCap },
  { id: 'matches',   label: 'Matches',   icon: Briefcase },
  { id: 'roadmap',   label: 'Roadmap',   icon: Compass },
  { id: 'market',    label: 'Market',    icon: TrendingUp },
  { id: 'resources', label: 'Resources', icon: BookOpen },
];

const relativeTime = (timestamp) => {
  if (!timestamp) return '';
  const cleaned = String(timestamp).replace(' ', 'T');
  const then = new Date(cleaned).getTime();
  if (Number.isNaN(then)) return timestamp;
  const seconds = Math.floor((Date.now() - then) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? '' : 's'} ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} day${days === 1 ? '' : 's'} ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months} month${months === 1 ? '' : 's'} ago`;
  return `${Math.floor(months / 12)} year ago`;
};

const fullDate = (timestamp) => {
  if (!timestamp) return '';
  const cleaned = String(timestamp).replace(' ', 'T');
  const d = new Date(cleaned);
  if (Number.isNaN(d.getTime())) return timestamp;
  return d.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
};

const pill = (bg, fg) => ({
  display: 'inline-flex', alignItems: 'center', gap: 4,
  padding: '4px 10px', borderRadius: 'var(--radius-full)',
  fontSize: 11, fontWeight: 600,
  background: bg, color: fg, lineHeight: 1,
});

const PLATFORM_STYLES = {
  udemy: {
    gradient: 'linear-gradient(135deg, #a435f0, #6b21a8)',
    label: 'Udemy',
  },
  coursera: {
    gradient: 'linear-gradient(135deg, #0056d2, #1a365d)',
    label: 'Coursera',
  },
  edx: {
    gradient: 'linear-gradient(135deg, #c41230, #7f1d1d)',
    label: 'edX',
  },
  pluralsight: {
    gradient: 'linear-gradient(135deg, #e11d48, #9f1239)',
    label: 'Pluralsight',
  },
  linkedin: {
    gradient: 'linear-gradient(135deg, #0077b5, #004182)',
    label: 'LinkedIn Learning',
  },
  youtube: {
    gradient: 'linear-gradient(135deg, #ff0000, #991b1b)',
    label: 'YouTube',
  },
  default: {
    gradient: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
    label: 'Course',
  },
};

const detectPlatform = (url) => {
  if (!url) return 'default';
  const lower = url.toLowerCase();
  if (lower.includes('udemy.com')) return 'udemy';
  if (lower.includes('coursera.org') || lower.includes('coursera.com')) return 'coursera';
  if (lower.includes('edx.org')) return 'edx';
  if (lower.includes('pluralsight.com')) return 'pluralsight';
  if (lower.includes('linkedin.com/learning')) return 'linkedin';
  if (lower.includes('youtube.com') || lower.includes('youtu.be')) return 'youtube';
  return 'default';
};

const EXPIRY_OPTIONS = [
  { label: '1 hour', hours: 1 },
  { label: '24 hours', hours: 24 },
  { label: '7 days', hours: 7 * 24 },
  { label: '30 days', hours: 30 * 24 },
];
export { fadeUp, stagger, TABS, relativeTime, fullDate, pill, PLATFORM_STYLES, detectPlatform, EXPIRY_OPTIONS };
