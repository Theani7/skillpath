import { Zap, Clock } from 'lucide-react';
import TargetRoleSelect from './TargetRoleSelect';
import DropZone from './DropZone';

const UploadForm = ({ targetRole, targetRoles, error, file, isDragOver, fileInputRef,
  onSelectRole, onDragOver, onDragLeave, onDrop, onBrowse,
  onRemoveFile, onFileChange, onAnalyze }) => {
  return (
  <>
      <TargetRoleSelect targetRoles={targetRoles} targetRole={targetRole} onSelect={onSelectRole} />
      <DropZone
        file={file}
        isDragOver={isDragOver}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onBrowse={onBrowse}
        onRemove={onRemoveFile}
      />
                    <input
                      type="file"
                      accept="application/pdf,.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                      ref={fileInputRef}
                      style={{ display: 'none' }}
                      onChange={onFileChange}
                    />
                    {error && (
                      <div style={{
                        background: 'var(--color-error-light)',
                        color: 'var(--color-error)',
                        fontSize: '13px', fontWeight: 500,
                        padding: '10px 14px', borderRadius: 'var(--radius-lg)',
                        marginBottom: '20px', textAlign: 'center',
                      }}>
                        {error}
                      </div>
                    )}
                    <button
                      onClick={onAnalyze}
                      disabled={!file}
                      style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                        width: '100%', height: '46px', padding: '0 20px',
                        borderRadius: 'var(--radius-lg)', border: 'none',
                        background: file ? 'var(--color-text)' : 'var(--color-border)',
                        color: file ? 'white' : 'var(--color-text-light)',
                        fontWeight: 'var(--font-semibold)', fontSize: 'var(--text-sm)',
                        cursor: file ? 'pointer' : 'not-allowed',
                        transition: 'background 150ms ease',
                      }}
                    >
                      <Zap size={16} />
                      Analyze My Resume
                    </button>
                    <p style={{
                      textAlign: 'center', fontSize: 'var(--text-xs)',
                      color: 'var(--color-text-light)', margin: '16px 0 0',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                    }}>
                      <Clock size={11} />
                      Analysis usually takes 5&ndash;10 seconds
                    </p>
    </>
  );
};

export default UploadForm;
