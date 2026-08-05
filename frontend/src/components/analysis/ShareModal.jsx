import { useState, useEffect, useCallback, useRef } from 'react';import { motion } from 'framer-motion';import {  Check, Clock, Copy, Globe, Link2, Lock, Mail, Share2, Twitter, Linkedin, X,} from 'lucide-react';import api from '../../services/api';import { EXPIRY_OPTIONS } from './analysisUtils';const ShareModal = ({ analysisId, targetRole, resumeName, onClose }) => {
  const [expiry, setExpiry] = useState(7 * 24);
  const [isPublic, setIsPublic] = useState(true);
  const [shareUrl, setShareUrl] = useState('');
  const [creating, setCreating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  const copiedTimer = useRef(null);

  useEffect(() => () => { if (copiedTimer.current) clearTimeout(copiedTimer.current); }, []);

  const createLink = useCallback(async () => {
    setCreating(true);
    setError('');
    try {
      const res = await api.post('/api/reports/share', {
        analysis_id: analysisId,
        expires_in_hours: expiry,
        is_public: isPublic,
      }, { _skipAuthRedirect: true });
      const token = res.data?.share_token;
      if (token) {
        const base = window.location.origin;
        setShareUrl(`${base}/shared/${token}`);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create share link.');
    } finally {
      setCreating(false);
    }
  }, [analysisId, expiry, isPublic]);

  const copyLink = useCallback(() => {
    if (!shareUrl) return;
    navigator.clipboard?.writeText(shareUrl).then(() => {
      setCopied(true);
      if (copiedTimer.current) clearTimeout(copiedTimer.current);
      copiedTimer.current = setTimeout(() => setCopied(false), 2000);
    }).catch(() => {});
  }, [shareUrl]);

  const shareText = `Check out my career analysis${targetRole ? ` for ${targetRole}` : ''}`;

  const socialLinks = shareUrl ? [
    { icon: Linkedin, label: 'LinkedIn', color: '#0A66C2', url: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}` },
    { icon: Twitter, label: 'Twitter', color: '#1DA1F2', url: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}` },
    { icon: Mail, label: 'Email', color: 'var(--color-text-secondary)', url: `mailto:?subject=${encodeURIComponent(`Career Analysis${targetRole ? ` - ${targetRole}` : ''}`)}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}` },
  ] : [];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="share-overlay"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ duration: 0.2 }}
        className="share-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Share Analysis"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="share-modal-header">
          <div>
            <h3 className="share-modal-title">
              <Share2 size={18} /> Share Analysis
            </h3>
            <p className="share-modal-subtitle">
              {resumeName || 'Your career analysis'}
            </p>
          </div>
          <button onClick={onClose} className="share-modal-close" aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="share-modal-body">
          {/* Expiry selector */}
          <div className="share-section">
            <label className="share-label">
              <Clock size={14} /> Link expires in
            </label>
            <div className="share-expiry-grid">
              {EXPIRY_OPTIONS.map((opt) => (
                <button
                  key={opt.hours}
                  onClick={() => setExpiry(opt.hours)}
                  className={`share-expiry-btn ${expiry === opt.hours ? 'active' : ''}`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Visibility toggle */}
          <div className="share-section">
            <label className="share-label">
              {isPublic ? <Globe size={14} /> : <Lock size={14} />}
              Visibility
            </label>
            <button
              onClick={() => setIsPublic(!isPublic)}
              className={`share-toggle ${isPublic ? 'public' : 'private'}`}
            >
              <span className="share-toggle-track">
                <span className="share-toggle-thumb" />
              </span>
              <span>{isPublic ? 'Anyone with the link can view' : 'Only you can view'}</span>
            </button>
          </div>

          {/* Generate button */}
          {!shareUrl && (
            <button
              onClick={createLink}
              disabled={creating}
              className="share-generate-btn"
            >
              {creating ? 'Generating link...' : 'Generate Share Link'}
            </button>
          )}

          {error && <div className="share-error">{error}</div>}

          {/* Link display + copy */}
          {shareUrl && (
            <div className="share-link-box">
              <div className="share-link-url">
                <Link2 size={14} />
                <input
                  readOnly
                  value={shareUrl}
                  className="share-link-input"
                  onClick={(e) => e.target.select()}
                />
              </div>
              <button onClick={copyLink} className="share-copy-btn">
                {copied ? <><Check size={14} /> Copied</> : <><Copy size={14} /> Copy</>}
              </button>
            </div>
          )}

          {/* Social share */}
          {shareUrl && (
            <div className="share-section">
              <label className="share-label">Share on</label>
              <div className="share-social-row">
                {socialLinks.map((social) => {
                  const SocialIcon = social.icon;
                  return (
                  <a
                    key={social.label}
                    href={social.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="share-social-btn"
                    style={{ '--social-color': social.color }}
                    title={`Share on ${social.label}`}
                  >
                    <SocialIcon size={16} />
                    <span>{social.label}</span>
                  </a>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};
export { ShareModal };
