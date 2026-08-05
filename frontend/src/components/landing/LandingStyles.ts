export const LANDING_STYLES = `        .landing-root {
          background: var(--color-bg);
          font-family: var(--font-body);
        }
        .landing-root h1, .landing-root h2, .landing-root h3, .landing-root h4 {
          font-family: var(--font-display);
        }

        /* Mission Control Grid Lines */
        .mc-grid-bg {
          position: absolute;
          inset: 0;
          pointer-events: none;
          background-image:
            linear-gradient(rgba(10, 22, 40, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(10, 22, 40, 0.04) 1px, transparent 1px);
          background-size: 40px 40px;
          mask-image: radial-gradient(ellipse 60% 50% at 50% 30%, black 0%, transparent 80%);
          -webkit-mask-image: radial-gradient(ellipse 60% 50% at 50% 30%, black 0%, transparent 80%);
          opacity: 0.6;
        }

        .mc-status {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 5px 12px;
          border-radius: var(--radius-full);
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          font-family: var(--font-display);
        }
        .mc-status-active {
          background: var(--green-50);
          color: var(--color-success);
          border: 1px solid var(--green-100);
        }
        .mc-status-active::before {
          content: '';
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--color-success);
          animation: mc-pulse 2s infinite;
        }
        @keyframes mc-pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.2); }
        }

        .mc-card {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-2xl);
          position: relative;
          overflow: hidden;
          transition: all 300ms cubic-bezier(0.22, 1, 0.36, 1);
        }
        .mc-card::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0;
          height: 3px;
          background: linear-gradient(90deg, var(--color-secondary), var(--color-success));
          opacity: 0;
          transition: opacity 300ms ease;
        }
        .mc-card:hover {
          transform: translateY(-4px);
          box-shadow: var(--shadow-card-hover);
          border-color: var(--navy-200);
        }
        .mc-card:hover::before {
          opacity: 1;
        }

        .mc-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
          background: var(--navy-950);
          border-bottom: 1px solid var(--navy-800);
        }
        .mc-header-dots {
          display: flex;
          gap: 6px;
        }
        .mc-header-dots span {
          width: 10px; height: 10px;
          border-radius: 50%;
        }
        .mc-header-dots span:nth-child(1) { background: #ef4444; }
        .mc-header-dots span:nth-child(2) { background: #f59e0b; }
        .mc-header-dots span:nth-child(3) { background: #22c55e; }
        .mc-header-title {
          font-family: var(--font-display);
          font-size: 11px; font-weight: 600;
          color: rgba(255,255,255,0.6);
          letter-spacing: 0.1em; text-transform: uppercase;
        }
        .mc-header-status {
          display: flex; align-items: center; gap: 6px;
          font-size: 10px; color: var(--color-success); font-weight: 600;
        }
        .mc-header-status::before {
          content: '';
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--color-success);
          animation: mc-pulse 2s infinite;
        }

        .mc-gradient {
          background: linear-gradient(135deg, var(--color-secondary) 0%, #ff8a5c 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .mc-step {
          position: relative;
          padding: 24px;
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-xl);
          transition: all 300ms ease;
        }
        .mc-step:hover {
          border-color: var(--navy-200);
          box-shadow: var(--shadow-md);
        }
        .mc-step-num {
          font-family: var(--font-display);
          font-size: 40px; font-weight: 700;
          color: var(--navy-100); line-height: 1;
          margin-bottom: 16px;
        }
        .mc-step:hover .mc-step-num {
          color: var(--orange-300);
        }

        .mc-bento {
          display: grid;
          grid-template-columns: 1fr;
          gap: 16px;
        }
        @media (min-width: 720px) {
          .mc-bento { grid-template-columns: repeat(2, 1fr); }
        }
        @media (min-width: 1024px) {
          .mc-bento { grid-template-columns: repeat(3, 1fr); }
        }

        .mc-feature {
          padding: 24px;
          position: relative;
        }
        .mc-feature-icon {
          width: 48px; height: 48px;
          border-radius: 12px;
          display: flex; align-items: center; justify-content: center;
          margin-bottom: 16px;
          background: var(--navy-950);
          color: var(--orange-400);
        }
        .mc-feature-status {
          position: absolute;
          top: 16px; right: 16px;
          font-family: var(--font-display);
          font-size: 9px; font-weight: 700;
          letter-spacing: 0.1em;
          color: var(--navy-300);
          text-transform: uppercase;
        }

        .mc-btn {
          display: inline-flex;
          align-items: center; gap: 10px;
          padding: 16px 28px;
          background: var(--color-secondary);
          color: white;
          border-radius: var(--radius-xl);
          font-family: var(--font-display);
          font-weight: 700; font-size: 15px;
          text-decoration: none;
          transition: all 300ms cubic-bezier(0.22, 1, 0.36, 1);
          box-shadow: var(--shadow-button);
          border: none; cursor: pointer;
        }
        .mc-btn:hover {
          transform: translateY(-2px) scale(1.02);
          box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
          color: white;
        }
        .mc-btn-secondary {
          background: var(--color-surface);
          color: var(--color-text);
          border: 2px solid var(--color-border);
          box-shadow: none;
        }
        .mc-btn-secondary:hover {
          background: var(--navy-50);
          border-color: var(--navy-200);
          box-shadow: none;
          color: var(--color-text);
        }

        .mc-stats {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }
        @media (min-width: 640px) {
          .mc-stats { grid-template-columns: repeat(4, 1fr); }
        }
        .mc-stat {
          padding: 16px;
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          text-align: center;
        }
        .mc-stat-value {
          font-family: var(--font-display);
          font-size: 28px; font-weight: 700;
          color: var(--color-text); line-height: 1;
        }
        .mc-stat-label {
          font-size: 11px; color: var(--color-text-muted);
          text-transform: uppercase; letter-spacing: 0.08em;
          margin-top: 4px;
        }

        .mc-mock {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-2xl);
          overflow: hidden;
          box-shadow: var(--shadow-lg);
        }

        .mc-faq {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-xl);
          overflow: hidden;
        }
        .mc-faq-item {
          border-bottom: 1px solid var(--color-border);
        }
        .mc-faq-item:last-child {
          border-bottom: none;
        }
        .mc-faq-trigger {
          width: 100%;
          display: flex; align-items: center; justify-content: space-between;
          gap: 16px; padding: 20px 24px;
          background: none; border: none;
          text-align: left; cursor: pointer;
          font-family: var(--font-body); font-weight: 600;
          color: var(--color-text);
          transition: background 200ms ease;
        }
        .mc-faq-trigger:hover {
          background: var(--navy-50);
        }
        .mc-faq-content {
          max-height: 0; overflow: hidden;
          transition: max-height 300ms cubic-bezier(0.22, 1, 0.36, 1);
        }
        .mc-faq-content-inner {
          padding: 0 24px 20px;
          color: var(--color-text-muted);
          font-size: 15px; line-height: 1.7;
        }

        .mc-float {
          position: absolute;
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-xl);
          padding: 12px 16px;
          box-shadow: var(--shadow-lg);
          display: flex; align-items: center; gap: 10px;
          font-size: 12px;
        }

        .mc-doodle {
          position: absolute;
          font-family: 'Comic Sans MS', cursive;
          color: var(--color-secondary);
          font-size: 12px;
          transform: rotate(-5deg);
          opacity: 0;
          transition: opacity 300ms ease;
          pointer-events: none;
        }
        .mc-card:hover .mc-doodle {
          opacity: 1;
        }

        .mc-hero-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 48px;
          align-items: center;
        }
        @media (min-width: 1024px) {
          .mc-hero-grid { grid-template-columns: 1.1fr 0.9fr; gap: 64px; }
        }

        .mc-cta {
          position: relative;
          background: var(--navy-950);
          border-radius: var(--radius-3xl);
          padding: 64px 32px;
          overflow: hidden;
          color: white;
        }
        .mc-cta::before {
          content: '';
          position: absolute; inset: 0;
          background:
            radial-gradient(600px circle at 20% 30%, rgba(255, 107, 53, 0.15), transparent 50%),
            radial-gradient(400px circle at 80% 70%, rgba(34, 197, 94, 0.1), transparent 50%);
          pointer-events: none;
        }
        .mc-cta > * {
          position: relative;
        }

        .mc-divider {
          height: 1px;
          background: linear-gradient(90deg, transparent, var(--color-border), transparent);
        }

        .mc-pill {
          display: inline-flex;
          align-items: center; gap: 8px;
          padding: 8px 16px;
          border-radius: var(--radius-full);
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          font-size: 13px; font-weight: 500;
          color: var(--color-text-muted);
        }`;
