import { Plus } from 'lucide-react';
import { DataTable } from './DataTable';
import { fieldStyle, truncate } from './adminUtils';

const CoursesTab = ({ courses, jobRoles, newCourse, editingCourse, onNewCourseChange, onEditingCourseChange, onAdd, onSave, onCancelEdit, onEdit, onDelete }) => (
          <div>
            <div className="card" style={{ padding: '24px', marginBottom: '20px' }}>
              <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Plus size={16} color="var(--color-primary)" /> {editingCourse ? 'Edit course' : 'Add course recommendation'}
              </h3>
              <form onSubmit={(e) => { e.preventDefault(); editingCourse ? onSave() : onAdd(e); }} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
                <select
                  value={editingCourse ? editingCourse.field : newCourse.field}
                  onChange={(e) => editingCourse ? onEditingCourseChange({ ...editingCourse, field: e.target.value }) : onNewCourseChange({ ...newCourse, field: e.target.value })}
                  aria-label="Job Role"
                  style={{ ...fieldStyle(false), cursor: 'pointer' }}
                >
                  <option value="">Select job role...</option>
                  {jobRoles.map((role) => (
                    <option key={role.id} value={role.title}>{role.title}</option>
                  ))}
                </select>
                <input
                  type="text" placeholder="Course name"
                  value={editingCourse ? editingCourse.course_name : newCourse.course_name}
                  onChange={(e) => editingCourse ? onEditingCourseChange({ ...editingCourse, course_name: e.target.value }) : onNewCourseChange({ ...newCourse, course_name: e.target.value })}
                  aria-label="Course name"
                  style={fieldStyle(false)}
                />
                <input
                  type="url" placeholder="https://..."
                  value={editingCourse ? editingCourse.course_url : newCourse.course_url}
                  onChange={(e) => editingCourse ? onEditingCourseChange({ ...editingCourse, course_url: e.target.value }) : onNewCourseChange({ ...newCourse, course_url: e.target.value })}
                  aria-label="Course URL"
                  style={fieldStyle(false)}
                />
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button type="submit" className="btn btn-primary" style={{ height: '44px', flex: 1 }}>
                    {editingCourse ? 'Save' : <><Plus size={14} style={{ marginRight: '6px' }} /> Add</>}
                  </button>
                  {editingCourse && (
                    <button type="button" onClick={() => onCancelEdit()} style={{ height: '44px', padding: '0 16px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', background: 'var(--color-surface)', color: 'var(--color-text)', cursor: 'pointer' }}>
                      Cancel
                    </button>
                  )}
                </div>
              </form>
            </div>

            <DataTable
              columns={[
                { label: 'Field', render: (c) => c.field },
                { label: 'Course', render: (c) => c.course_name, nowrap: true },
                { label: 'URL', render: (c) => <a href={c.course_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-primary)' }}>{truncate(c.course_url, 40)}</a>, mono: true, nowrap: true },
                {
                  label: '',
                  render: (c) => (
                    <button type="button" onClick={() => onEdit(c)} style={{ padding: '4px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '12px', cursor: 'pointer' }}>
                      Edit
                    </button>
                  ),
                },
              ]}
              rows={courses}
              keyField="id"
              empty="No courses yet."
              onDelete={onDelete}
              deleteLabel="Delete course"
            />
          </div>
);
export { CoursesTab };
