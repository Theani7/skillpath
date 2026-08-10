import type { LucideIcon } from 'lucide-react';
import {
  Sparkles, FileSearch, MessageSquare, BarChart3, Settings,
  LayoutDashboard, Activity, Users, MessageSquareText, BookOpen, Briefcase, Database, PenTool,
} from 'lucide-react';

export type NavItem = {
  path: string;
  icon: LucideIcon;
  label: string;
};

export type NavSection = {
  label: string;
  items: NavItem[];
};

export const SECTIONS: NavSection[] = [
  {
    label: 'Analyze',
    items: [
      { path: '/app', icon: Sparkles, label: 'Resume Analyzer' },
      { path: '/analysis', icon: FileSearch, label: 'Latest Analysis' },
      { path: '/cover-letter', icon: PenTool, label: 'Cover Letter' },
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

export const BOTTOM_LINKS: NavItem[] = [
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const ADMIN_SECTION: NavSection = {
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
