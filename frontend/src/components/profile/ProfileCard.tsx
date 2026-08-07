import { motion, AnimatePresence } from 'framer-motion';
import {
  User, Phone, MapPin, Briefcase, Clock, Linkedin, Github, FileText,
  Edit2, Save, X,
} from 'lucide-react';
import { CardHeader, PrimaryButton, SecondaryButton, EditableField, DetailRow } from './ui';
import type { UserProfile } from '../../types';

type Props = {
  profile: UserProfile;
  profileDraft: UserProfile;
  editingProfile: boolean;
  savingProfile: boolean;
  setEditingProfile: (v: boolean) => void;
  setProfileDraft: (v: UserProfile) => void;
  handleSaveProfile: () => void;
};

const ProfileCard = ({ profile, profileDraft, editingProfile, savingProfile, setEditingProfile, setProfileDraft, handleSaveProfile }: Props) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.1 }}
    className="card"
    style={{ padding: '24px' }}
  >
    <CardHeader
      icon={User}
      title="Personal Information"
      subtitle="How you appear on the platform."
      action={
        editingProfile ? (
          <div style={{ display: 'flex', gap: '8px' }}>
            <SecondaryButton onClick={() => { setEditingProfile(false); setProfileDraft(profile); }}>
              <X size={13} /> Cancel
            </SecondaryButton>
            <PrimaryButton onClick={handleSaveProfile} disabled={savingProfile}>
              <Save size={13} /> {savingProfile ? 'Saving…' : 'Save'}
            </PrimaryButton>
          </div>
        ) : (
          <SecondaryButton onClick={() => setEditingProfile(true)}>
            <Edit2 size={13} /> Edit
          </SecondaryButton>
        )
      }
    />

    <AnimatePresence mode="wait">
      {editingProfile ? (
        <motion.div
          key="edit"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
        >
          <EditableField
            label="Full Name" icon={User}
            value={profileDraft.full_name}
            onChange={(v: string) => setProfileDraft({ ...profileDraft, full_name: v })}
            placeholder="Your full name"
          />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
            <EditableField
              label="Phone" icon={Phone} type="tel"
              value={profileDraft.phone}
              onChange={(v: string) => setProfileDraft({ ...profileDraft, phone: v })}
              placeholder="+1 (555) 000-0000"
            />
            <EditableField
              label="Location" icon={MapPin}
              value={profileDraft.location}
              onChange={(v: string) => setProfileDraft({ ...profileDraft, location: v })}
              placeholder="City, Country"
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
            <EditableField
              label="Current Role" icon={Briefcase}
              value={profileDraft.current_role}
              onChange={(v: string) => setProfileDraft({ ...profileDraft, current_role: v })}
              placeholder="e.g., Software Engineer"
            />
            <EditableField
              label="Experience (years)" icon={Clock}
              value={profileDraft.experience_years}
              onChange={(v: string) => setProfileDraft({ ...profileDraft, experience_years: v })}
              placeholder="e.g., 3"
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
            <EditableField
              label="LinkedIn" icon={Linkedin}
              value={profileDraft.linkedin_url}
              onChange={(v: string) => setProfileDraft({ ...profileDraft, linkedin_url: v })}
              placeholder="https://linkedin.com/in/…"
            />
            <EditableField
              label="GitHub" icon={Github}
              value={profileDraft.github_url}
              onChange={(v: string) => setProfileDraft({ ...profileDraft, github_url: v })}
              placeholder="https://github.com/…"
            />
          </div>
          <EditableField
            label="Bio" icon={FileText} as="textarea"
            value={profileDraft.bio}
            onChange={(v: string) => setProfileDraft({ ...profileDraft, bio: v })}
            placeholder="A short intro that travels with your applications."
          />
        </motion.div>
      ) : (
        <motion.div
          key="view"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
        >
          <DetailRow icon={User} label="Full Name" value={profile.full_name || '—'} />
          <DetailRow icon={Phone} label="Phone" value={profile.phone || '—'} />
          <DetailRow icon={MapPin} label="Location" value={profile.location || '—'} />
          <DetailRow icon={Briefcase} label="Current Role" value={profile.current_role || '—'} />
          <DetailRow icon={Clock} label="Experience" value={profile.experience_years ? `${profile.experience_years} years` : '—'} />
          <DetailRow icon={Linkedin} label="LinkedIn" value={profile.linkedin_url} link />
          <DetailRow icon={Github} label="GitHub" value={profile.github_url} link />
          <DetailRow icon={FileText} label="Bio" value={profile.bio || '—'} multiline />
        </motion.div>
      )}
    </AnimatePresence>
  </motion.div>
);

export default ProfileCard;
