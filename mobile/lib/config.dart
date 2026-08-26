/// Build-time configuration.
///
/// Base URL comes from `--dart-define=API_BASE_URL=...`:
///
///   flutter build apk --dart-define=API_BASE_URL=https://your-api.example.com
///
/// Placeholder default: fill before release builds.
const String kApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://REPLACE-WITH-YOUR-BACKEND.example.com',
);

const String kAppName = 'SkillPath';
