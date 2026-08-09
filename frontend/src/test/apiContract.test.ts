import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

/**
 * Guards against frontend/backend field-name drift.
 *
 * Two production bugs came from this: the admin tables keyed rows on `ID`
 * while Postgres returns lowercase `id` (every React key was undefined), and
 * the profile page mixed `current_role` with `current_job_role`. Neither the
 * type checker nor the linter can see across the HTTP boundary, so assert on
 * the backend source directly.
 */

const repo = join(__dirname, '..', '..', '..');
const read = (p: string) => readFileSync(join(repo, p), 'utf8');
const srcRead = (p: string) => readFileSync(join(__dirname, '..', p), 'utf8');

describe('API contract: user_data / user_feedback id casing', () => {
  const userRoutes = read('api/routes/user.py');
  const adminRoutes = read('api/routes/admin.py');

  it('backend selects lowercase id from user_data', () => {
    // `ID BIGSERIAL PRIMARY KEY` is unquoted, so Postgres folds it to `id`.
    // Selecting bare `ID` and reading row['ID'] raises KeyError.
    // Case-sensitive on purpose: lowercase `SELECT id,` is the correct form.
    expect(userRoutes).not.toMatch(/SELECT\s+ID\s*,/);
    expect(adminRoutes).not.toMatch(/SELECT\s+ID\s*,/);
    expect(userRoutes).not.toMatch(/row\['ID'\]|row\["ID"\]/);
    expect(adminRoutes).not.toMatch(/row\['ID'\]|row\["ID"\]/);
  });

  it('frontend never keys admin tables on uppercase ID', () => {
    for (const f of [
      'components/admin/ResumesTab.tsx',
      'components/admin/FeedbackTab.tsx',
      'components/admin/UsersTab.tsx',
      'components/admin/CoursesTab.tsx',
    ]) {
      expect(srcRead(f), `${f} must use keyField="id"`).not.toMatch(/keyField="ID"/);
    }
  });

  it('AdminUserRow declares lowercase id', () => {
    const types = srcRead('types/index.ts');
    const block = types.slice(types.indexOf('interface AdminUserRow'));
    const body = block.slice(0, block.indexOf('}'));
    expect(body).toMatch(/\bid:\s*number/);
    expect(body).not.toMatch(/\bID:\s*number/);
  });
});

describe('API contract: profile role field', () => {
  it('backend exposes current_role, aliasing the current_job_role column', () => {
    const userRoutes = read('api/routes/user.py');
    // The column is current_job_role; the JSON field is current_role. The GET
    // must alias it or the frontend reads undefined.
    expect(userRoutes).toMatch(/current_job_role\s+AS\s+current_role/i);
  });

  it('frontend reads current_role everywhere', () => {
    for (const f of [
      'pages/Profile.tsx',
      'components/profile/Header.tsx',
      'components/profile/ProfileCard.tsx',
      'types/index.ts',
    ]) {
      expect(srcRead(f), `${f} should not read current_job_role`).not.toMatch(/current_job_role/);
    }
  });
});

describe('API contract: user export completeness', () => {
  it('export returns every table the account deletion clears', () => {
    const userRoutes = read('api/routes/user.py');
    const exportFn = userRoutes.slice(userRoutes.indexOf('def export_my_data'));
    const body = exportFn.slice(0, exportFn.indexOf('\n@router'));
    // If delete removes it, export must hand it over first.
    for (const table of [
      'user_profiles',
      'user_preferences',
      'user_data',
      'user_roadmap_progress',
      'shared_reports',
      'notifications',
    ]) {
      expect(body, `export must include ${table}`).toContain(table);
    }
  });

  it('frontend export calls the single aggregate endpoint', () => {
    const settings = srcRead('pages/Settings.tsx');
    expect(settings).toContain('/api/user/export');
  });
});

describe('API contract: profile field validation', () => {
  const userRoutes = read('api/routes/user.py');

  it('phone field has a format pattern', () => {
    expect(userRoutes).toMatch(/phone.*pattern/);
  });

  it('experience_years field has a numeric pattern', () => {
    expect(userRoutes).toMatch(/experience_years.*pattern/);
  });

  it('URL fields have format patterns', () => {
    expect(userRoutes).toMatch(/linkedin_url.*pattern/);
    expect(userRoutes).toMatch(/github_url.*pattern/);
  });
});
