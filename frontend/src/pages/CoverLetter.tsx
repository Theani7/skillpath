import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, Copy, Check, RefreshCw, Sparkles, Building2,
  Briefcase, MessageSquare, AlertCircle, ChevronRight,
  Pencil, Save, X, Download, User,
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import api from '../services/api';

interface CoverLetterData {
  error?: boolean;
  missing_fields?: string[];
  message?: string;
  header_name?: string;
  header_email?: string;
  header_phone?: string;
  header_date?: string;
  greeting?: string;
  opening_paragraph?: string;
  body_paragraph_1?: string;
  body_paragraph_2?: string;
  closing_paragraph?: string;
  sign_off?: string;
  signature?: string;
  full_text?: string;
  target_role?: string;
  company_name?: string;
}

const CoverLetter = () => {
  const navigate = useNavigate();
  const [resumeData, setResumeData] = useState<Record<string, string | number | string[] | object> | null>(null);
  const [targetRole, setTargetRole] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [hiringManager, setHiringManager] = useState('');
  const [result, setResult] = useState<CoverLetterData | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingResume, setLoadingResume] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState('');
  const [isEdited, setIsEdited] = useState(false);
  const [missingFields, setMissingFields] = useState<string[]>([]);

  const loadLatestAnalysis = useCallback(async () => {
    setLoadingResume(true);
    try {
      const res = await api.get('/api/user/latest-analysis', { _skipAuthRedirect: true } as never);
      if (res.data?.found && res.data?.analysis?.data) {
        setResumeData(res.data.analysis.data);
        if (res.data.target_role || res.data.analysis?.target_role) {
          setTargetRole(res.data.target_role || res.data.analysis.target_role);
        }
      }
    } catch {
      // User may not have an analysis yet
    } finally {
      setLoadingResume(false);
    }
  }, []);

  useEffect(() => { loadLatestAnalysis(); }, [loadLatestAnalysis]);

  const handleGenerate = async () => {
    if (!targetRole.trim()) {
      setError('Please enter a target role');
      return;
    }
    if (!resumeData) {
      setError('No resume data found. Please analyze your resume first.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    setIsEditing(false);
    setIsEdited(false);
    try {
      const res = await api.post('/api/cover-letter/generate', {
        resume_data: resumeData,
        target_role: targetRole,
        company_name: companyName,
        job_description: jobDescription,
        hiring_manager: hiringManager,
      });
      if (res.data?.error) {
        setError(res.data.message || 'Missing required information. Please update your profile.');
        setMissingFields(res.data.missing_fields || []);
      } else if (res.data?.full_text) {
        setResult(res.data);
      } else {
        setError('Failed to generate cover letter. Please try again.');
      }
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    const textToCopy = isEditing ? editText : result?.full_text;
    if (!textToCopy) return;
    await navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadPDF = () => {
    if (!result && !isEditing) return;

    const candidateName = result?.header_name || 'Candidate';
    const role = result?.target_role || targetRole || 'Cover-Letter';
    const email = result?.header_email || '';
    const phone = result?.header_phone || '';
    const dateStr = result?.header_date || '';

    const doc = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'letter' });
    const margin = 72;
    const maxWidth = doc.internal.pageSize.getWidth() - margin * 2;
    let y = margin;

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(16);
    doc.setTextColor(0);
    doc.text(candidateName, margin, y);
    y += 18;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(100);
    const contact = [email, phone].filter(Boolean).join(' | ');
    if (contact) {
      doc.text(contact, margin, y);
      y += 14;
    }

    if (dateStr) {
      doc.text(dateStr, margin, y);
      y += 28;
    } else {
      y += 14;
    }

    doc.setTextColor(0);
    doc.setFontSize(11);

    let letterBody = '';
    if (isEditing) {
      letterBody = editText;
    } else if (result) {
      const parts = [
        result.greeting,
        result.opening_paragraph,
        result.body_paragraph_1,
        result.body_paragraph_2,
        result.closing_paragraph,
      ].filter(Boolean);
      letterBody = parts.join('\n\n');
    }

    const lines = doc.splitTextToSize(letterBody, maxWidth);
    for (const line of lines) {
      if (y > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += 16;
    }

    y += 24;
    doc.setFont('helvetica', 'normal');
    doc.text('Sincerely,', margin, y);
    y += 18;
    doc.setFont('helvetica', 'bold');
    doc.text(candidateName, margin, y);

    const fileName = `${candidateName.replace(/\s+/g, '-')}-${role.replace(/\s+/g, '-')}.pdf`;
    doc.save(fileName.toLowerCase());
  };

  const handleStartEdit = () => {
    if (!result) return;
    const fullLetter = `${result.greeting || 'Dear Hiring Manager,'}\n\n${result.opening_paragraph || ''}\n\n${result.body_paragraph_1 || ''}${result.body_paragraph_2 ? '\n\n' + result.body_paragraph_2 : ''}\n\n${result.closing_paragraph || ''}\n\n${result.sign_off || 'Sincerely,'}\n${result.signature || ''}`;
    setEditText(fullLetter);
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    if (!result) return;
    const updated = { ...result, full_text: editText };
    setResult(updated);
    setIsEdited(true);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditText('');
  };

  if (loadingResume) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--color-secondary)' }} />
          <p style={{ marginTop: 12, color: 'var(--color-text-muted)' }}>Loading your resume data...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{ maxWidth: 800, margin: '0 auto' }}
    >
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 12 }}>
          <FileText size={28} style={{ color: 'var(--color-secondary)' }} />
          Cover Letter Generator
          <span style={{
            fontSize: 11, fontWeight: 600, padding: '3px 8px', borderRadius: 6,
            background: 'var(--orange-100)', color: 'var(--color-secondary)',
            verticalAlign: 'middle', lineHeight: 1,
          }}>
            BETA
          </span>
        </h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: 15 }}>
          Generate a tailored cover letter based on your resume and profile.
        </p>
      </div>

      {!resumeData && (
        <div style={{
          padding: '16px 20px', borderRadius: 12,
          background: 'var(--color-surface-elevated)',
          border: '1px solid var(--color-border)',
          display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24,
        }}>
          <AlertCircle size={20} style={{ color: 'var(--color-warning)', flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <span style={{ fontSize: 14, color: 'var(--color-text-muted)' }}>
              No resume data found.{' '}
              <button
                onClick={() => navigate('/app')}
                style={{
                  background: 'none', border: 'none', color: 'var(--color-secondary)',
                  cursor: 'pointer', fontSize: 14, padding: 0, textDecoration: 'underline',
                }}
              >
                Analyze your resume first
              </button>
            </span>
          </div>
        </div>
      )}

      <div style={{
        padding: 24, borderRadius: 16,
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)', marginBottom: 24,
      }}>
        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--color-text-muted)' }}>
            <Briefcase size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Target Role *
          </label>
          <input
            type="text" value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Senior Software Engineer"
            style={inputStyle}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--color-text-muted)' }}>
            <Building2 size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Company Name (optional)
          </label>
          <input
            type="text" value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g. Google"
            style={inputStyle}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--color-text-muted)' }}>
            <User size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Hiring Manager (optional)
          </label>
          <input
            type="text" value={hiringManager}
            onChange={(e) => setHiringManager(e.target.value)}
            placeholder="e.g. John Smith"
            style={inputStyle}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--color-text-muted)' }}>
            <FileText size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Job Description (optional)
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here for a more tailored letter..."
            rows={4}
            style={{ ...inputStyle, resize: 'vertical', fontFamily: 'inherit' }}
          />
        </div>

        {error && (
          <div style={{
            padding: '12px 16px', borderRadius: 8, marginBottom: 16,
            background: 'var(--color-error-subtle)', border: '1px solid var(--color-error)',
            fontSize: 13,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-error)' }}>
              <AlertCircle size={16} />
              {error}
            </div>
            {missingFields.length > 0 && (
              <div style={{ marginTop: 8, color: 'var(--color-text-muted)' }}>
                Go to your{' '}
                <button
                  onClick={() => navigate('/profile')}
                  style={{
                    background: 'none', border: 'none', color: 'var(--color-secondary)',
                    cursor: 'pointer', fontSize: 13, padding: 0, textDecoration: 'underline',
                  }}
                >
                  Profile
                </button>
                {' '}to update your information.
              </div>
            )}
          </div>
        )}

        <button
          onClick={handleGenerate}
          disabled={loading || !resumeData}
          style={{
            width: '100%', padding: '12px 24px', borderRadius: 10,
            border: 'none', background: 'var(--color-secondary)',
            color: '#fff', fontSize: 15, fontWeight: 600,
            cursor: loading || !resumeData ? 'not-allowed' : 'pointer',
            opacity: loading || !resumeData ? 0.6 : 1,
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            boxShadow: '0 4px 14px 0 rgba(255, 107, 53, 0.3)',
          }}
        >
          {loading ? (
            <><RefreshCw size={18} className="spin" /> Generating...</>
          ) : (
            <><Sparkles size={18} /> Generate Cover Letter</>
          )}
        </button>
      </div>

      <AnimatePresence>
        {result && !result.error && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.3 }}
            style={{
              padding: 24, borderRadius: 16,
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
              <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0 }}>
                {isEditing ? 'Edit Cover Letter' : 'Your Cover Letter'}
              </h2>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {isEditing ? (
                  <>
                    <button onClick={handleCancelEdit} style={btnSecondaryStyle}>
                      <X size={14} /> Cancel
                    </button>
                    <button onClick={handleSaveEdit} style={{ ...btnSecondaryStyle, background: 'var(--color-success)', border: 'none', color: '#fff' }}>
                      <Save size={14} /> Save
                    </button>
                  </>
                ) : (
                  <>
                    <button onClick={handleGenerate} disabled={loading} style={btnSecondaryStyle}>
                      <RefreshCw size={14} /> Regenerate
                    </button>
                    <button onClick={handleStartEdit} style={btnSecondaryStyle}>
                      <Pencil size={14} /> Edit
                    </button>
                    <button onClick={handleDownloadPDF} style={btnSecondaryStyle}>
                      <Download size={14} /> Download PDF
                    </button>
                    <button onClick={handleCopy} style={{ ...btnSecondaryStyle, background: copied ? 'var(--color-success)' : 'var(--color-secondary)', border: 'none', color: '#fff' }}>
                      {copied ? <Check size={14} /> : <Copy size={14} />}
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                  </>
                )}
              </div>
            </div>

            {isEditing ? (
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                rows={16}
                style={{
                  width: '100%', padding: 20, borderRadius: 12,
                  background: 'var(--color-bg)', border: '2px solid var(--color-secondary)',
                  fontFamily: 'Georgia, serif', lineHeight: 1.7,
                  color: 'var(--color-text)', fontSize: 14,
                  resize: 'vertical', boxSizing: 'border-box', outline: 'none',
                }}
              />
            ) : isEdited ? (
              <div style={letterContainerStyle}>
                {result.full_text}
              </div>
            ) : (
              <div style={letterContainerStyle}>
                {(result.header_name || result.header_email || result.header_phone) && (
                  <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--color-border)' }}>
                    {result.header_name && <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 4 }}>{result.header_name}</div>}
                    {(result.header_email || result.header_phone) && (
                      <div style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
                        {[result.header_email, result.header_phone].filter(Boolean).join(' | ')}
                      </div>
                    )}
                    {result.header_date && <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginTop: 4 }}>{result.header_date}</div>}
                  </div>
                )}
                {result.greeting && <div style={{ marginBottom: 16 }}>{result.greeting}</div>}
                {result.opening_paragraph && <div style={{ marginBottom: 16 }}>{result.opening_paragraph}</div>}
                {result.body_paragraph_1 && <div style={{ marginBottom: 16 }}>{result.body_paragraph_1}</div>}
                {result.body_paragraph_2 && <div style={{ marginBottom: 16 }}>{result.body_paragraph_2}</div>}
                {result.closing_paragraph && <div style={{ marginBottom: 24 }}>{result.closing_paragraph}</div>}
                <div>
                  {result.sign_off && <div style={{ marginBottom: 4 }}>{result.sign_off}</div>}
                  {result.signature && <div style={{ fontWeight: 600 }}>{result.signature}</div>}
                </div>
              </div>
            )}

            <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--color-text-muted)' }}>
              <ChevronRight size={14} />
              <span>
                {isEditing
                  ? 'Make your changes above. Click Save to keep them or Cancel to discard.'
                  : 'Tip: Click Edit to customize the letter or Regenerate for a fresh version.'}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '10px 14px', borderRadius: 8,
  border: '1px solid var(--color-border)', background: 'var(--color-bg)',
  color: 'var(--color-text)', fontSize: 14, outline: 'none', boxSizing: 'border-box',
};

const btnSecondaryStyle: React.CSSProperties = {
  padding: '8px 14px', borderRadius: 8, fontSize: 13,
  border: '1px solid var(--color-border)', background: 'var(--color-bg)',
  color: 'var(--color-text-muted)', cursor: 'pointer',
  display: 'flex', alignItems: 'center', gap: 6,
};

const letterContainerStyle: React.CSSProperties = {
  padding: 20, borderRadius: 12,
  background: 'var(--color-bg)',
  border: '1px solid var(--color-border)',
  fontFamily: 'Georgia, serif', lineHeight: 1.7,
  color: 'var(--color-text)', whiteSpace: 'pre-wrap',
};

export default CoverLetter;
