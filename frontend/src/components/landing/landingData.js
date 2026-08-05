import { FileText, Target, BookOpen, Sparkles, Clock, Shield, Upload, Brain, Map, CheckCircle } from 'lucide-react';

export const matchSkills = ['React', 'TypeScript', 'Node.js', 'PostgreSQL', 'AWS', 'REST APIs'];
export const gapSkills = ['Kubernetes', 'Terraform'];

export const features = [
  {
    icon: FileText,
    title: 'Resume analysis in seconds',
    body: 'Drop a PDF or DOCX. We extract every skill, project, and signal, then score your fit against the role you want.',
    status: 'ACTIVE',
  },
  {
    icon: Target,
    title: 'Skill gap detection',
    body: 'See exactly which skills you are missing, ranked by how much each one moves your match score.',
    status: 'SCANNING',
  },
  {
    icon: BookOpen,
    title: 'Personalized learning roadmap',
    body: 'A step-by-step plan with courses, projects, and resources to close each gap.',
    status: 'READY',
  },
  {
    icon: Sparkles,
    title: 'Role-fit recommendations',
    body: 'See job-role matches based on your current skills and the gaps that matter most.',
    status: 'ANALYZING',
  },
  {
    icon: Clock,
    title: 'Progress history',
    body: 'Track resume scores over time and revisit earlier analyses whenever you need.',
    status: 'TRACKING',
  },
  {
    icon: Shield,
    title: 'Private by default',
    body: 'Your resume stays in your account. We never sell your data, and you can delete everything in one click.',
    status: 'SECURED',
  },
];

export const steps = [
  { num: '01', icon: Upload, title: 'Upload your resume', body: 'PDF or DOCX. We parse it locally first, then enrich with AI when needed.' },
  { num: '02', icon: Brain, title: 'Pick a target role', body: 'Choose from a list or write your own. We benchmark your skills against it.' },
  { num: '03', icon: Map, title: 'Get your roadmap', body: 'A personalized plan with the exact skills to learn, in what order, with what resources.' },
  { num: '04', icon: CheckCircle, title: 'Measure progress', body: 'Upload again later and compare your new score, gaps, and recommendations.' },
];
