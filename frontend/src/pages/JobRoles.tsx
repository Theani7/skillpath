import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Briefcase, ChevronDown, ChevronRight, ExternalLink, Plus, Trash2, X, CheckCircle, AlertTriangle,
} from 'lucide-react';
import api from '../services/api';
import PageLoader from '../components/Skeleton';
import type { AdminCourse } from '../types';

type ToastItem = { type: 'success' | 'error'; message: string };
type Role = { id: number; title: string; category?: string; description?: string; skills: { id: number; skill_name: string }[]; roadmap_count: number };

const inputStyle = {
  width: '100%', height: '36px', padding: '0 10px',
  border: '1px solid var(--color-border)', borderRadius: '8px',
  fontSize: '13px', color: 'var(--color-text)', background: 'var(--color-surface)', outline: 'none',
};

const JobRoles = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [roles, setRoles] = useState<Role[]>([]);
  const [expandedRole, setExpandedRole] = useState<number | null>(null);
  const [roleCourses, setRoleCourses] = useState<Record<number, AdminCourse[]>>({});
  const [toast, setToast] = useState<ToastItem | null>(null);
  const [showAddCourse, setShowAddCourse] = useState<number | null>(null);
  const [newCourse, setNewCourse] = useState<{ course_name: string; course_url: string }>({ course_name: '', course_url: '' });

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchRoles = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/admin/job-roles');
      setRoles(res.data.job_roles || []);
    } catch {
      showToast('error', 'Failed to load roles.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchRoles(); }, [fetchRoles]);

  const fetchCourses = async (roleId: number) => {
    try {
      const res = await api.get(`/api/admin/courses?field=${encodeURIComponent(roles.find(r => r.id === roleId)?.title || '')}`);
      setRoleCourses((prev) => ({ ...prev, [roleId]: res.data.courses || [] }));
    } catch {
      try {
        const res = await api.get('/api/admin/courses');
        const all = res.data.courses || [];
        const roleName = roles.find(r => r.id === roleId)?.title || '';
        setRoleCourses((prev) => ({ ...prev, [roleId]: all.filter((c: AdminCourse) => c.field === roleName) }));
      } catch {
        showToast('error', 'Failed to load courses.');
      }
    }
  };

  const handleExpandRole = (roleId: number) => {
    if (expandedRole === roleId) {
      setExpandedRole(null);
    } else {
      setExpandedRole(roleId);
      fetchCourses(roleId);
    }
  };

  const handleAddCourse = async (roleId: number) => {
    if (!newCourse.course_name.trim() || !newCourse.course_url.trim()) {
      showToast('error', 'Name and URL required.');
      return;
    }
    const roleName = roles.find(r => r.id === roleId)?.title || '';
    try {
      await api.post('/api/admin/courses', {
        field: roleName,
        course_name: newCourse.course_name,
        course_url: newCourse.course_url,
      });
      showToast('success', 'Course added.');
      setNewCourse({ course_name: '', course_url: '' });
      setShowAddCourse(null);
      fetchCourses(roleId);
    } catch {
      showToast('error', 'Failed to add course.');
    }
  };

  const handleDeleteCourse = async (courseId: number, roleId: number) => {
    if (!confirm('Delete this course?')) return;
    try {
      await api.delete(`/api/admin/courses/${courseId}`);
      showToast('success', 'Course deleted.');
      fetchCourses(roleId);
    } catch {
      showToast('error', 'Failed to delete course.');
    }
  };

  if (loading) return <PageLoader />;

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--color-text)', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Briefcase size={22} color="var(--color-primary)" /> Job Roles
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>Predefined career roles, their skills, and associated courses.</p>
      </div>

      {roles.length === 0 ? (
        <div className="card" style={{ padding: '48px', textAlign: 'center' }}>
          <Briefcase size={40} color="var(--color-text-light)" style={{ marginBottom: '12px' }} />
          <p style={{ color: 'var(--color-text-muted)', margin: 0 }}>No job roles found.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {roles.map((role) => (
            <div key={role.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div
                style={{ display: 'flex', alignItems: 'center', padding: '16px 20px', gap: '12px', cursor: 'pointer' }}
                onClick={() => handleExpandRole(role.id)}
              >
                <div style={{ color: 'var(--color-text-muted)' }}>
                  {expandedRole === role.id ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: '600', fontSize: '15px', color: 'var(--color-text)' }}>{role.title}</span>
                    {role.category && (
                      <span style={{ padding: '2px 8px', borderRadius: '10px', background: 'var(--color-bg)', fontSize: '11px', color: 'var(--color-text-muted)' }}>{role.category}</span>
                    )}
                  </div>
                  {role.description && (
                    <p style={{ margin: '4px 0 0', fontSize: '12px', color: 'var(--color-text-muted)' }}>{role.description}</p>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: 'var(--color-text-muted)' }}>
                  <span>{role.skills?.length || 0} skills</span>
                  <span>{role.roadmap_count || 0} roadmaps</span>
                </div>
              </div>

              <AnimatePresence>
                {expandedRole === role.id && (
                  <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} style={{ overflow: 'hidden', borderTop: '1px solid var(--color-border)' }}>
                    <div style={{ padding: '16px 20px' }}>
                      {role.skills?.length > 0 && (
                        <div style={{ marginBottom: '20px' }}>
                          <p style={{ fontSize: '12px', fontWeight: '600', color: 'var(--color-text-muted)', margin: '0 0 8px' }}>Required Skills</p>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {role.skills.map((s) => (
                              <span key={s.id} style={{ padding: '4px 10px', borderRadius: '12px', background: 'var(--color-bg)', fontSize: '12px', color: 'var(--color-text)' }}>{s.skill_name}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                          <p style={{ fontSize: '13px', fontWeight: '600', color: 'var(--color-text)', margin: 0 }}>Courses</p>
                          <button
                            onClick={() => { setShowAddCourse(showAddCourse === role.id ? null : role.id); setNewCourse({ course_name: '', course_url: '' }); }}
                            style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '4px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: 'var(--color-text)', cursor: 'pointer', fontSize: '11px' }}
                          >
                            <Plus size={12} /> Add Course
                          </button>
                        </div>

                        <AnimatePresence>
                          {showAddCourse === role.id && (
                            <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} style={{ overflow: 'hidden', marginBottom: '10px' }}>
                              <div style={{ padding: '10px', borderRadius: '8px', background: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
                                <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                                  <input placeholder="Course name" value={newCourse.course_name} onChange={(e) => setNewCourse({ ...newCourse, course_name: e.target.value })} style={{ ...inputStyle, flex: 1, height: '32px', fontSize: '12px' }} />
                                  <input placeholder="Course URL" value={newCourse.course_url} onChange={(e) => setNewCourse({ ...newCourse, course_url: e.target.value })} style={{ ...inputStyle, flex: 1, height: '32px', fontSize: '12px' }} />
                                </div>
                                <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                                  <button onClick={() => setShowAddCourse(null)} style={{ padding: '4px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', cursor: 'pointer', fontSize: '11px' }}>Cancel</button>
                                  <button onClick={() => handleAddCourse(role.id)} style={{ padding: '4px 10px', borderRadius: '6px', border: 'none', background: 'var(--color-primary)', color: 'white', cursor: 'pointer', fontSize: '11px', fontWeight: '600' }}>Add</button>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>

                        {roleCourses[role.id]?.length > 0 ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                            {roleCourses[role.id].map((course) => (
                              <div key={course.id} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 12px', borderRadius: '6px', background: 'var(--color-bg)' }}>
                                <div style={{ flex: 1 }}>
                                  <span style={{ fontSize: '13px', fontWeight: '500' }}>{course.course_name}</span>
                                  <span style={{ marginLeft: '8px', fontSize: '11px', color: 'var(--color-text-muted)' }}>{course.platform || 'Course'}</span>
                                </div>
                                <a href={course.course_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-primary)', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px' }}>
                                  View <ExternalLink size={10} />
                                </a>
                                <button onClick={() => handleDeleteCourse(course.id, role.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-error)', padding: 0 }}>
                                  <Trash2 size={12} />
                                </button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: 0 }}>No courses yet.</p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      )}

      <AnimatePresence>
        {toast && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} style={{ position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)', background: toast.type === 'success' ? 'var(--color-success)' : 'var(--color-error)', color: 'white', padding: '12px 20px', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-lg)', fontSize: '14px', fontWeight: '600', zIndex: 50, display: 'flex', alignItems: 'center', gap: '8px' }}>
            {toast.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default JobRoles;
