import { MessageSquare, Send } from 'lucide-react';
import { Section } from './';

const SupportCard = (onOpen) => (
          <Section
            icon={MessageSquare}
            title="Contact Support"
            description="Need help? Send us a message."
            accent="indigo"
          >
            <button
              onClick={() => onOpen(true)}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '6px',
                height: '38px', padding: '0 18px', borderRadius: 'var(--radius-md)',
                background: 'var(--color-primary)', color: 'white',
                fontSize: '13px', fontWeight: 'var(--font-semibold)',
                border: 'none', cursor: 'pointer',
              }}
            >
              <Send size={14} /> Send Message
            </button>
          </Section>
);

export default SupportCard;
