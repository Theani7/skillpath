export interface ResumeData {
  name: string;
  email: string;
  mobile_number: string;
  skills: string[];
  education: string[];
  experience: string[];
  experience_blocks: ExperienceBlock[];
  education_blocks: EducationBlock[];
  roadmap: RoadmapPhase[];
  company_names: string[];
  designation: string[];
  missing_skills: string[];
  match_score: number;
  no_of_pages: number;
  matched_role_skills?: { skill: string; is_required: boolean }[];
  links?: { linkedin: string; github: string };
  summary?: string;
  certifications?: string[];
  languages?: string[];
  awards?: string[];
  confidence_score?: number;
  parsing_method?: string;
  phone?: string;
  objective?: string;
}

export interface ExperienceBlock {
  title: string;
  company: string;
  start_date: string;
  end_date: string;
  bullets: string[];
}

export interface EducationBlock {
  degree: string;
  institution: string;
  year: string;
}

export interface RoadmapPhase {
  step: number;
  title: string;
  duration: string;
  skills: string[];
  action_items: string[];
  difficulty?: string;
  resources?: LearningResource[];
}

export interface LearningResource {
  title: string;
  url: string;
  type: string;
}

export interface CourseRef {
  name: string;
  url: string;
}

export interface YoutubeLink {
  title: string;
  url: string;
}

export interface MarketTrends {
  regional_distribution?: { region: string; percentage?: number }[];
  top_skills?: { skill: string; salary: number; demand?: number }[];
  [trendType: string]: unknown;
}

export interface JobMatch {
  job_id: string;
  title: string;
  company: string;
  location: string;
  workplace_type: string;
  salary_estimate: number;
  fit_score: number;
  why_matched: string[];
}

export interface ScoreBreakdownItem {
  weight: number;
  score: number;
  status: "missing" | "present";
  evidence: string[];
}

export interface ScoreBreakdown {
  summary: ScoreBreakdownItem;
  education: ScoreBreakdownItem;
  experience: ScoreBreakdownItem;
  skills: ScoreBreakdownItem;
  contact_info: ScoreBreakdownItem;
}

export interface AnalysisResponse {
  status: string;
  data: ResumeData;
  target_role: string | null;
  predicted_field: string;
  recommended_skills: string[];
  recommended_courses: CourseRef[];
  match_score: number;
  missing_skills: YoutubeLink[];
  missing_skill_names: string[];
  roadmap: RoadmapPhase[];
  trends: MarketTrends | null;
  job_matches: JobMatch[];
  resume_score: number;
  score_breakdown: ScoreBreakdown;
  feedback: string[];
  videos: {
    resume: string[];
    interview: string[];
    tutorials: YoutubeLink[];
  };
}

export interface LoginResponse {
  role: "admin" | "user";
  full_name: string;
  username: string;
}

export interface MeResponse {
  username: string;
  role: "admin" | "user";
  full_name: string;
  email: string | null;
}

export interface RegisterResponse {
  message: string;
  otp_sent: boolean;
}

export interface LatestAnalysisResponse {
  found: boolean;
  id?: number;
  timestamp?: string;
  pdf_name?: string;
  predicted_field?: string;
  target_role?: string;
  resume_score?: number;
  analysis?: AnalysisResponse;
  role_skills?: { skill: string; is_required: boolean }[];
}

export interface HistoryItem {
  id: number;
  timestamp: string;
  predicted_field: string;
  target_role: string;
  resume_score: number;
  missing_skills: string[];
  actual_skills: string[];
  recommended_skills: string[];
  analysis_data: AnalysisResponse | null;
}

export interface HistoryResponse {
  history: HistoryItem[];
}

export interface UserProfile {
  user_id: number;
  full_name: string;
  phone: string;
  location: string;
  bio: string;
  current_job_role: string;
  experience_years: string;
  linkedin_url: string;
  github_url: string;
  updated_at: string;
}

export interface UserPreferences {
  user_id: number;
  target_role: string;
  timeline_months: number;
  preferred_location: string;
  salary_target: number;
  locale: string;
  updated_at: string;
}

export interface SkillTrend {
  type: "improved" | "gained" | "lost" | "new_gaps";
  skills: string[];
  count: number;
}

export interface SkillTrendsResponse {
  trends: SkillTrend[];
  analyses_count: number;
  latest_skills: string[];
  latest_gaps: string[];
}

export interface RoadmapProgressResponse {
  progress: Record<string, boolean>;
}

export interface InterviewQuestion {
  id: number;
  question: string;
  category: "behavioral" | "technical";
  focus_skill?: string;
  answer?: string;
}

export interface InterviewCopilotResponse {
  target_role: string;
  questions: InterviewQuestion[];
}

export interface InterviewEvaluation {
  score: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  summary: string;
}

export interface ProjectRec {
  title: string;
  objective: string;
  deliverables: string[];
  estimated_weeks: number;
}

export interface AdminUserRow {
  ID: number;
  user_id: number;
  Name: string;
  Email_ID: string;
  Timestamp: string;
  Predicted_Field: string;
  resume_score: string;
  target_role: string;
  missing_skills: string;
  Actual_skills: string;
  Recommended_skills: string;
  pdf_name: string;
}

export interface RegisteredUser {
  id: number;
  username: string;
  email: string;
  role: "admin" | "user";
  is_active: number;
}

export interface AdminCourse {
  id: number;
  field: string;
  course_name: string;
  course_url: string;
  description: string;
  instructor: string;
  rating: number;
  duration: string;
  price: string;
  platform: string;
  enrollment_count: number;
  last_scraped: string | null;
  created_at: string;
}

export interface BillingPlan {
  id: string;
  price_usd_month: number;
  features: string[];
}

export interface Notification {
  id: number;
  user_id: number;
  channel: string;
  message: string;
  status: string;
  send_at: number;
  created_at: string;
}

export interface ShareLink {
  token: string;
  analysis_id: number;
  pdf_name: string;
  target_role: string;
  expires_at: number;
  is_public: boolean;
  expired: boolean;
}

export interface AuthUser {
  role: "admin" | "user";
  username: string;
  full_name: string;
  email: string | null;
}
