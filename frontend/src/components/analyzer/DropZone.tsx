import { FileText, CheckCircle2, X, UploadCloud } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import formatFileSize from './utils';

type Props = {
  file: File | null;
  isDragOver: boolean;
  onDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragLeave: (e: React.DragEvent<HTMLDivElement>) => void;
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  onBrowse: () => void;
  onRemove: () => void;
};

const DropZone = ({ file, isDragOver, onDragOver, onDragLeave, onDrop, onBrowse, onRemove }: Props) => {
  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={onBrowse}
      style={{
        borderRadius: 'var(--radius-xl)',
        padding: file ? '20px' : '48px 24px',
        textAlign: 'center',
        cursor: file ? 'default' : 'pointer',
        transition: 'all 200ms ease',
        border: `2px dashed ${
          isDragOver ? 'var(--color-primary)' :
          file ? 'var(--color-success)' : 'var(--color-border)'
        }`,
        background: isDragOver ? 'var(--indigo-50)' :
                    file ? 'var(--emerald-50)' : 'var(--color-bg)',
        marginBottom: '20px',
      }}
    >
      <AnimatePresence mode="wait">
        {file ? (
          <motion.div
            key="file"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            style={{
              display: 'flex', alignItems: 'center', gap: '14px',
              textAlign: 'left',
            }}
          >
            <div style={{
              width: '44px', height: '44px', borderRadius: 'var(--radius-lg)',
              background: 'var(--color-success)', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <FileText size={20} color="white" />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: 'var(--text-sm)', fontWeight: 'var(--font-semibold)',
                color: 'var(--color-text)',
                whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              }}>
                {file.name}
              </div>
              <div style={{
                fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)',
                marginTop: '2px',
                display: 'flex', alignItems: 'center', gap: '4px',
              }}>
                <CheckCircle2 size={12} color="var(--color-success)" />
                {formatFileSize(file.size)} &middot; ready to analyze
              </div>
            </div>
            <button
              type="button"
              onClick={onRemove}
              style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                padding: '6px',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'var(--color-text-muted)',
                flexShrink: 0,
              }}
              title="Remove file"
            >
              <X size={14} />
            </button>
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div style={{
              width: '56px', height: '56px', borderRadius: 'var(--radius-xl)',
              background: 'var(--indigo-50)', color: 'var(--color-primary)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 16px',
              transition: 'transform 200ms ease',
              transform: isDragOver ? 'scale(1.1)' : 'scale(1)',
            }}>
              <UploadCloud size={26} />
            </div>
            <h3 style={{
              fontSize: 'var(--text-base)', fontWeight: 'var(--font-semibold)',
              color: 'var(--color-text)', marginBottom: '4px',
            }}>
              {isDragOver ? 'Drop your resume here' : 'Click or drag your resume'}
            </h3>
            <p style={{
              fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)',
              margin: 0,
            }}>
              PDF or DOCX &middot; up to 10MB
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DropZone;
