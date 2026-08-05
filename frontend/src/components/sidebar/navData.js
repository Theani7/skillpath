import {
  Sparkles, FileSearch, MessageSquare, BarChart3, Settings,
  LayoutDashboard, Activity, Users, MessageSquareText, BookOpen, Briefcase, Database,
} from 'lucide-react';

export const SECTIONS = [
  {
    label: 'Analyze',
    items: [
      { path: '/app', icon: Sparkles, label: 'Resume Analyzer' },
      { path: '/analysis', icon: FileSearch, label: 'Latest Analysis' },
      { path: '/mock-interview', icon: MessageSquare, label: 'Mock Interview' },
    ],
  },
  {
    label: 'Track',
    items: [
      { path: '/profile', icon: BarChart3, label: 'Profile' },
    ],
  },
];

export const BOTTOM_LINKS = [
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const ADMIN_SECTION = {
  label: 'Manage',
  items: [
    { path: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/admin/resumes', icon: Activity, label: 'Resume Logs' },
    { path: '/admin/users', icon: Users, label: 'Users' },
    { path: '/admin/feedback', icon: MessageSquareText, label: 'Feedback' },
    { path: '/admin/courses', icon: BookOpen, label: 'Courses' },
    { path: '/admin/job-roles', icon: Briefcase, label: 'Job Roles' },
    { path: '/admin/ai-monitoring', icon: Database, label: 'AI Monitoring' },
  ],
};
