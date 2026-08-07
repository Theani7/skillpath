import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import AnalyzerHeader from '../components/analyzer/AnalyzerHeader';
import StepsIndicator from '../components/analyzer/StepsIndicator';
import LoadingBar from '../components/analyzer/LoadingBar';
import UploadForm from '../components/analyzer/UploadForm';
import AnalyzingState from '../components/analyzer/AnalyzingState';

const defaultRoles = [
  'Software Engineering', 'Frontend Development', 'Backend Development',
  'Data Science', 'DevOps', 'Mobile Development', 'Full Stack Development',
  'Cybersecurity',
];

const Analyzer = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState<string>('Software Engineering');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [targetRoles, setTargetRoles] = useState<string[]>(defaultRoles);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const res = await api.get('/api/job-roles');
        if (res.data?.roles?.length > 0) {
          setTargetRoles(res.data.roles);
        }
      } catch {
        // use defaults
      }
    };
    fetchRoles();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    validateAndSetFile(selected);
  };

  const handleDragOver = (e: React.DragEvent) => { e.preventDefault(); setIsDragOver(true); };
  const handleDragLeave = () => { setIsDragOver(false); };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    validateAndSetFile(e.dataTransfer.files[0]);
  };

  const validateAndSetFile = (selected: File | undefined) => {
    if (!selected) return;
    if (selected.type === 'application/pdf' || selected.name.toLowerCase().endsWith('.pdf') ||
        selected.name.toLowerCase().endsWith('.docx')) {
      setFile(selected);
      setError('');
    } else {
      setError('Please upload a valid PDF or DOCX file.');
      setFile(null);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_role', targetRole);
    try {
      const res = await api.post('/api/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      if (res.data?.error) {
        setError(res.data.error);
        setLoading(false);
        return;
      }
      navigate('/analysis', { replace: true });
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100%',
      background: 'var(--color-bg)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '-160px', right: '-160px', width: '500px', height: '500px',
        borderRadius: '50%', opacity: 0.06, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-primary) 0%, transparent 70%)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-200px', left: '-200px', width: '500px', height: '500px',
        borderRadius: '50%', opacity: 0.05, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-secondary) 0%, transparent 70%)',
      }} />

      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ maxWidth: '720px', margin: '0 auto' }}
        >
          <AnalyzerHeader />
          <StepsIndicator />

          <div className="card" style={{ overflow: 'hidden', position: 'relative' }}>
            <LoadingBar loading={loading} />

            <div style={{ padding: '32px' }}>
              <AnimatePresence mode="wait">
                {!loading ? (
                  <motion.div
                    key="upload"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    <UploadForm
                      targetRole={targetRole}
                      targetRoles={targetRoles}
                      error={error}
                      file={file}
                      isDragOver={isDragOver}
                      fileInputRef={fileInputRef}
                      onSelectRole={setTargetRole}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      onBrowse={() => !file && fileInputRef.current?.click()}
                      onRemoveFile={handleRemoveFile}
                      onFileChange={handleFileChange}
                      onAnalyze={handleAnalyze}
                    />
                  </motion.div>
                ) : (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    style={{
                      padding: '40px 0', textAlign: 'center',
                    }}
                  >
                    <AnalyzingState targetRole={targetRole} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Analyzer;
