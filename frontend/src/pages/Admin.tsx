import { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../services/api';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AnimatePresence } from 'framer-motion';
import PageLoader from '../components/Skeleton';
import type { AdminUserRow, RegisteredUser, AdminCourse } from '../types';
import type { ReactNode, FormEvent, KeyboardEvent } from 'react';
import {
  DashboardTab, ResumesTab, UsersTab, FeedbackTab, CoursesTab,
  ConfirmDialog, ResumeDetailModal, Toast,
} from '../components/admin';

type ToastItem = { type: 'success' | 'error'; message: string };
type ConfirmState = {
  title: string;
  body: string;
  confirmLabel: string;
  danger?: boolean;
  onConfirm: () => void;
};

type FeedbackStats = {
  total: number;
  positive: number;
  neutral: number;
  negative: number;
  ratio: number | string;
  by_score: Record<number, number>;
};

type QualityMetrics = {
  total_requests: number;
  server_errors: number;
  avg_latency_ms: number;
  parse_failure_rate_pct: number;
};

type UploadPoint = { date: string; count: number };
type SkillGap = { skill: string; count: number };
type RoleDist = { target_role: string; count: number };

const Admin = () => {
  const location = useLocation();
  const activeTab = location.pathname.split('/').pop() || 'dashboard';
  const [loading, setLoading] = useState<boolean>(true);
  const { user } = useAuth();
  const [resumes, setResumes] = useState<AdminUserRow[]>([]);
  const [feedback, setFeedback] = useState<Array<{ id: number; feed_name: string; feed_email: string; feed_score: number; comments: string; Timestamp: string }>>([]);
  const [registeredUsers, setRegisteredUsers] = useState<RegisteredUser[]>([]);
  const [userSearch, setUserSearch] = useState<string>('');
  const [courses, setCourses] = useState<AdminCourse[]>([]);
  const [jobRoles, setJobRoles] = useState<{ id: number; title: string }[]>([]);
  const [analytics, setAnalytics] = useState<{ most_sought_role: string; most_common_missing_skill: string }>({ most_sought_role: '', most_common_missing_skill: '' });
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null);
  const [scrapeStatus, setScrapeStatus] = useState<ReactNode>('');
  const [newCourse, setNewCourse] = useState<{ field: string; course_name: string; course_url: string }>({ field: '', course_name: '', course_url: '' });
  const [editingCourse, setEditingCourse] = useState<AdminCourse | null>(null);
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);
  const [toast, setToast] = useState<ToastItem | null>(null);
  const [resumeDetail, setResumeDetail] = useState<unknown>(null);
  const [resumePage, setResumePage] = useState<number>(0);
  const [resumeTotal, setResumeTotal] = useState<number>(0);
  const [feedbackPage, setFeedbackPage] = useState<number>(0);
  const [feedbackTotal, setFeedbackTotal] = useState<number>(0);
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);
  const [uploadsOverTime, setUploadsOverTime] = useState<UploadPoint[]>([]);
  const [skillPathGaps, setSkillPathGaps] = useState<SkillGap[]>([]);
  const [roleDistribution, setRoleDistribution] = useState<RoleDist[]>([]);
  const PAGE_SIZE = 20;
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => { if (toastTimerRef.current) clearTimeout(toastTimerRef.current); }, []);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    toastTimerRef.current = setTimeout(() => setToast(null), 3500);
  };

  const fetchAdminData = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      const [usersRes, feedbackRes, regUsersRes, coursesRes, analyticsRes, qualityRes, uploadsRes, skillPathGapsRes, roleDistRes, jobRolesRes, feedbackStatsRes] = await Promise.all([
        api.get(`/api/admin/users?limit=${PAGE_SIZE}&offset=${resumePage * PAGE_SIZE}`, { signal }),
        api.get(`/api/admin/feedback?limit=${PAGE_SIZE}&offset=${feedbackPage * PAGE_SIZE}`, { signal }),
        api.get('/api/admin/registered-users', { signal }),
        api.get('/api/admin/courses', { signal }),
        api.get('/api/admin/analytics', { signal }),
        api.get('/api/admin/quality-metrics', { signal }).catch(() => ({ data: null })),
        api.get('/api/admin/analytics/uploads-over-time', { signal }),
        api.get('/api/admin/analytics/skill-gaps', { signal }),
        api.get('/api/admin/analytics/role-distribution', { signal }),
        api.get('/api/admin/job-roles', { signal }),
        api.get('/api/admin/feedback/stats', { signal }),
      ]);
      setResumes(usersRes.data.users || []);
      setResumeTotal(usersRes.data.total || 0);
      setFeedback(feedbackRes.data.feedback || []);
      setFeedbackTotal(feedbackRes.data.total || 0);
      setRegisteredUsers(regUsersRes.data.users || []);
      setCourses(coursesRes.data.courses || []);
      setAnalytics(analyticsRes.data);
      setQualityMetrics(qualityRes.data);
      setUploadsOverTime(uploadsRes.data.data || []);
      setSkillPathGaps(skillPathGapsRes.data.data || []);
      setRoleDistribution(roleDistRes.data.data || []);
      setJobRoles(jobRolesRes.data.job_roles || []);
      setFeedbackStats(feedbackStatsRes.data);
    } catch (_err: unknown) {
      const err = _err as { name?: string; code?: string };
      if (err?.name !== 'CanceledError' && err?.code !== 'ERR_CANCELED') {
        console.error(_err);
        showToast('error', 'Failed to load admin data.');
      }
    } finally {
      setLoading(false);
    }
  }, [resumePage, feedbackPage]);

  useEffect(() => {
    if (!user?.username) return;
    const controller = new AbortController();
    fetchAdminData(controller.signal);
    return () => controller.abort();
  }, [user?.username, fetchAdminData]);

  const runAction = async (label: string, fn: () => Promise<void>, successMessage: string) => {
    try {
      await fn();
      showToast('success', successMessage);
    } catch (_err: unknown) {
      showToast('error', `Failed to ${label}.`);
    }
  };

  const handleDeleteResume = (id: number) => setConfirm({
    title: 'Delete resume log?',
    body: 'This will remove the analysis row from the database.',
    confirmLabel: 'Delete',
    onConfirm: () => runAction('delete log', async () => {
      await api.delete(`/api/admin/users/${id}`);
      setResumes((prev) => prev.filter((u) => u.id !== id));
    }, 'Resume log deleted.'),
  });

  const handleDeleteFeedback = (id: number) => setConfirm({
    title: 'Delete feedback?',
    body: 'This user-reported entry will be removed permanently.',
    confirmLabel: 'Delete',
    onConfirm: () => runAction('delete feedback', async () => {
      await api.delete(`/api/admin/feedback/${id}`);
      setFeedback((prev) => prev.filter((f) => f.id !== id));
    }, 'Feedback deleted.'),
  });

  const handleDeleteRegisteredUser = (id: number) => setConfirm({
    title: 'Ban this user?',
    body: 'All their resumes, job applications, and tokens will be deleted. This cannot be undone.',
    confirmLabel: 'Delete user',
    danger: true,
    onConfirm: () => runAction('ban user', async () => {
      await api.delete(`/api/admin/registered-users/${id}`);
      setRegisteredUsers((prev) => prev.filter((u) => u.id !== id));
    }, 'User deleted.'),
  });

  const handleUpdateRole = async (userId: number, newRole: string) => {
    await runAction('update role', async () => {
      const res = await api.patch(`/api/admin/registered-users/${userId}/role`, { role: newRole });
      setRegisteredUsers((prev) => prev.map((u) => (u.id === userId ? res.data.user : u)));
    }, 'Role updated.');
  };

  const handleUpdateStatus = async (userId: number, isActive: boolean) => {
  };

  const handleAddCourse = async (e: FormEvent) => {
    e.preventDefault();
    if (!newCourse.field.trim() || !newCourse.course_name.trim() || !newCourse.course_url.trim()) {
      showToast('error', 'Please fill all three fields.');
      return;
    }
    await runAction('add course', async () => {
      await api.post('/api/admin/courses', newCourse);
      setNewCourse({ field: '', course_name: '', course_url: '' });
      await fetchAdminData();
    }, 'Course added.');
  };

  const handleDeleteCourse = (id: number) => setConfirm({
    title: 'Delete course?',
    body: 'This recommendation will be removed from the database.',
    confirmLabel: 'Delete',
    onConfirm: () => runAction('delete course', async () => {
      await api.delete(`/api/admin/courses/${id}`);
      setCourses((prev) => prev.filter((c) => c.id !== id));
    }, 'Course deleted.'),
  });

  const handleEditCourse = (course: AdminCourse) => {
    setEditingCourse({ ...course });
  };

  const handleSaveCourse = async () => {
    if (!editingCourse) return;
    if (!editingCourse.field.trim() || !editingCourse.course_name.trim() || !editingCourse.course_url.trim()) {
      showToast('error', 'Please fill all three fields.');
      return;
    }
    await runAction('update course', async () => {
      await api.patch(`/api/admin/courses/${editingCourse.id}`, {
        field: editingCourse.field,
        course_name: editingCourse.course_name,
        course_url: editingCourse.course_url,
      });
      setEditingCourse(null);
      await fetchAdminData();
    }, 'Course updated.');
  };

  const handleViewResume = async (id: number) => {
    try {
      const res = await api.get(`/api/admin/users/${id}`);
      setResumeDetail(res.data.analysis);
    } catch {
      showToast('error', 'Failed to load resume details.');
    }
  };

  const handleTriggerScrape = () => {
    setScrapeStatus('Running simulation...');
    api.post('/api/admin/trigger-scrape')
      .then((res) => setScrapeStatus(`Success: ${res.data.message} (${res.data.timestamp})`))
      .catch(() => setScrapeStatus('Failed to run scrape.'));
  };

  useEffect(() => {
    if (!confirm) return;
    const onKey = (e: Event) => { if ((e as unknown as KeyboardEvent).key === 'Escape') setConfirm(null); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [confirm]);

  if (loading) return <PageLoader />;

  return (
    <div style={{
      minHeight: '100%',
      background: 'var(--color-bg)',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '-200px', right: '-180px', width: '500px', height: '500px',
        borderRadius: '50%', opacity: 0.04, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-primary) 0%, transparent 70%)',
      }} />

      <div style={{ position: 'relative', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '24px' }}>
          <span className="badge badge-primary" style={{ marginBottom: '12px' }}>
            <ShieldAlert size={11} /> Admin
          </span>
          <h1 style={{
            fontSize: 'var(--text-3xl)', fontWeight: 'var(--font-bold)',
            color: 'var(--color-text)', margin: '0 0 6px', letterSpacing: 'var(--tracking-tight)',
          }}>
            Control Panel
          </h1>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', margin: 0 }}>
            Manage users, feedback, and course recommendations.
          </p>
        </div>

        {activeTab === 'dashboard' && (
          <DashboardTab
            resumes={resumes}
            registeredUsers={registeredUsers}
            feedback={feedback as Parameters<typeof DashboardTab>[0]['feedback']}
            courses={courses}
            analytics={analytics}
            qualityMetrics={qualityMetrics}
            uploadsOverTime={uploadsOverTime}
            skillPathGaps={skillPathGaps}
            roleDistribution={roleDistribution}
            scrapeStatus={scrapeStatus}
            onTriggerScrape={handleTriggerScrape}
          />
        )}

        {activeTab === 'resumes' && (
          <ResumesTab
            rows={resumes}
            total={resumeTotal}
            page={resumePage}
            pageSize={PAGE_SIZE}
            onPageChange={setResumePage}
            onView={handleViewResume}
            onDelete={handleDeleteResume}
          />
        )}

        {activeTab === 'users' && (
          <UsersTab
            users={registeredUsers}
            search={userSearch}
            onSearchChange={setUserSearch}
            onRoleChange={handleUpdateRole}
            onStatusChange={handleUpdateStatus}
            onDelete={handleDeleteRegisteredUser}
          />
        )}

        {activeTab === 'feedback' && (
          <FeedbackTab
            feedback={feedback as Parameters<typeof FeedbackTab>[0]['feedback']}
            stats={feedbackStats}
            page={feedbackPage}
            total={feedbackTotal}
            pageSize={PAGE_SIZE}
            onPageChange={setFeedbackPage}
            onDelete={handleDeleteFeedback}
          />
        )}

        {activeTab === 'courses' && (
          <CoursesTab
            courses={courses}
            jobRoles={jobRoles}
            newCourse={newCourse}
            editingCourse={editingCourse}
            onNewCourseChange={setNewCourse}
            onEditingCourseChange={setEditingCourse}
            onAdd={handleAddCourse}
            onSave={handleSaveCourse}
            onCancelEdit={() => setEditingCourse(null)}
            onEdit={handleEditCourse}
            onDelete={handleDeleteCourse}
          />
        )}
      </div>

      <AnimatePresence>
        {confirm && (
          <ConfirmDialog
            title={confirm.title}
            body={confirm.body}
            confirmLabel={confirm.confirmLabel}
            danger={confirm.danger ?? false}
            onCancel={() => setConfirm(null)}
            onConfirm={() => { confirm.onConfirm(); setConfirm(null); }}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {resumeDetail ? (
          <ResumeDetailModal detail={resumeDetail as AdminUserRow} onClose={() => setResumeDetail(null)} />
        ) : null}
      </AnimatePresence>

      <AnimatePresence>
        {toast ? <Toast toast={toast} /> : null}
      </AnimatePresence>
    </div>
  );
};

export default Admin;
