import { motion, AnimatePresence } from 'framer-motion';
import { Target, MapPin, Calendar, DollarSign, Edit2, Save, X } from 'lucide-react';
import { CardHeader, PrimaryButton, SecondaryButton, EditableField, DetailRow } from './ui';

const PrefsCard = ({ preferences, prefsDraft, editingPrefs, savingPrefs, setEditingPrefs, setPrefsDraft, handleSavePrefs }) => (

          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.15 }}
            className="card"
            style={{ padding: '24px' }}
          >
            <CardHeader
              icon={Target}
              title="Career Preferences"
              subtitle="Powers AI matches and job recommendations."
              action={
                editingPrefs ? (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <SecondaryButton onClick={() => { setEditingPrefs(false); setPrefsDraft(preferences); }}>
                      <X size={13} /> Cancel
                    </SecondaryButton>
                    <PrimaryButton onClick={handleSavePrefs} disabled={savingPrefs}>
                      <Save size={13} /> {savingPrefs ? 'Saving…' : 'Save'}
                    </PrimaryButton>
                  </div>
                ) : (
                  <SecondaryButton onClick={() => setEditingPrefs(true)}>
                    <Edit2 size={13} /> Edit
                  </SecondaryButton>
                )
              }
            />

            <AnimatePresence mode="wait">
              {editingPrefs ? (
                <motion.div
                  key="edit-prefs"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
                >
                  <EditableField
                    label="Target Role" icon={Target}
                    value={prefsDraft.target_role}
                    onChange={(v) => setPrefsDraft({ ...prefsDraft, target_role: v })}
                    placeholder="e.g., Senior Frontend Engineer"
                  />
                  <EditableField
                    label="Preferred Location" icon={MapPin}
                    value={prefsDraft.preferred_location}
                    onChange={(v) => setPrefsDraft({ ...prefsDraft, preferred_location: v })}
                    placeholder="e.g., Remote, Berlin"
                  />
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
                    <EditableField
                      label="Timeline (months)" icon={Calendar} type="number"
                      value={prefsDraft.timeline_months}
                      onChange={(v) => setPrefsDraft({ ...prefsDraft, timeline_months: v })}
                      placeholder="6"
                    />
                    <EditableField
                      label="Salary Target (USD)" icon={DollarSign} type="number"
                      value={prefsDraft.salary_target}
                      onChange={(v) => setPrefsDraft({ ...prefsDraft, salary_target: v })}
                      placeholder="120000"
                    />
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="view-prefs"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
                >
                  <DetailRow icon={Target} label="Target Role" value={preferences.target_role || '—'} />
                  <DetailRow icon={MapPin} label="Preferred Location" value={preferences.preferred_location || '—'} />
                  <DetailRow icon={Calendar} label="Timeline" value={`${preferences.timeline_months} months`} />
                  <DetailRow
                    icon={DollarSign}
                    label="Salary Target"
                    value={preferences.salary_target ? `$${Number(preferences.salary_target).toLocaleString()}` : '—'}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>);

export default PrefsCard;
