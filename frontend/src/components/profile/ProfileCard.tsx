import { useState } from 'react';
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

const PATTERNS = {
  phone: '^[+]?[\\d\\s().-]*$',
  experience: '^\\d*\\.?\\d*$',
};

const FIELD_MAX = {
  full_name: 200,
  phone: 20,
  location: 200,
  bio: 500,
  current_role: 100,
  experience_years: 10,
  linkedin_url: 500,
  github_url: 500,
};

const validateField = (field: string, value: string): string | undefined => {
  if (!value) return undefined;
  switch (field) {
    case 'phone':
      if (!/^[+]?[\d\s().-]+$/.test(value)) return 'Only digits, spaces, +, -, (, ) allowed';
      if (value.replace(/\D/g, '').length < 7) return 'Phone number too short';
      if (value.replace(/\D/g, '').length > 10) return 'Phone number cannot exceed 10 digits';
      break;
    case 'experience_years':
      if (!/^\d*\.?\d*$/.test(value)) return 'Must be a number';
      if (parseFloat(value) > 80) return 'Please enter a valid number';
      break;
    case 'linkedin_url':
      if (!/^(https?:\/\/(www\.)?linkedin\.com\/.*)?$/.test(value)) return 'Must be a linkedin.com URL';
      break;
    case 'github_url':
      if (!/^(https?:\/\/(www\.)?github\.com\/.*)?$/.test(value)) return 'Must be a github.com URL';
      break;
  }
  return undefined;
};

const ProfileCard = ({ profile, profileDraft, editingProfile, savingProfile, setEditingProfile, setProfileDraft, handleSaveProfile }: Props) => {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: string, value: string) => {
    setProfileDraft({ ...profileDraft, [field]: value });
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleSave = () => {
    const newErrors: Record<string, string> = {};
    (Object.keys(PATTERNS) as Array<keyof typeof PATTERNS>).forEach((field) => {
      const err = validateField(field, (profileDraft as unknown as Record<string, string>)[field] || '');
      if (err) newErrors[field] = err;
    });
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    handleSaveProfile();
  };

  return (
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
              <SecondaryButton onClick={() => { setEditingProfile(false); setProfileDraft(profile); setErrors({}); }}>
                <X size={13} /> Cancel
              </SecondaryButton>
              <PrimaryButton onClick={handleSave} disabled={savingProfile}>
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
              onChange={(v: string) => handleChange('full_name', v)}
              placeholder="Your full name"
              maxLength={FIELD_MAX.full_name}
            />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
              <EditableField
                label="Phone" icon={Phone} type="tel"
                value={profileDraft.phone}
                onChange={(v: string) => handleChange('phone', v)}
                placeholder="+1 (555) 000-0000"
                pattern={PATTERNS.phone}
                maxLength={FIELD_MAX.phone}
                error={errors.phone}
              />
              <EditableField
                label="Location" icon={MapPin}
                value={profileDraft.location}
                onChange={(v: string) => handleChange('location', v)}
                placeholder="City, Country"
                maxLength={FIELD_MAX.location}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
              <EditableField
                label="Current Role" icon={Briefcase}
                value={profileDraft.current_role}
                onChange={(v: string) => handleChange('current_role', v)}
                placeholder="e.g., Software Engineer"
                maxLength={FIELD_MAX.current_role}
              />
              <EditableField
                label="Experience (years)" icon={Clock}
                value={profileDraft.experience_years}
                onChange={(v: string) => handleChange('experience_years', v)}
                placeholder="e.g., 3"
                pattern={PATTERNS.experience}
                maxLength={FIELD_MAX.experience_years}
                error={errors.experience_years}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
              <EditableField
                label="LinkedIn" icon={Linkedin}
                value={profileDraft.linkedin_url}
                onChange={(v: string) => handleChange('linkedin_url', v)}
                placeholder="https://linkedin.com/in/…"
                maxLength={FIELD_MAX.linkedin_url}
                error={errors.linkedin_url}
              />
              <EditableField
                label="GitHub" icon={Github}
                value={profileDraft.github_url}
                onChange={(v: string) => handleChange('github_url', v)}
                placeholder="https://github.com/…"
                maxLength={FIELD_MAX.github_url}
                error={errors.github_url}
              />
            </div>
            <EditableField
              label="Bio" icon={FileText} as="textarea"
              value={profileDraft.bio}
              onChange={(v: string) => handleChange('bio', v)}
              placeholder="A short intro that travels with your applications."
              maxLength={FIELD_MAX.bio}
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
};

export default ProfileCard;
