/// User profile as returned by GET /api/auth/me.
class UserProfile {
  final String username;
  final String role;
  final String fullName;

  const UserProfile({
    required this.username,
    required this.role,
    required this.fullName,
  });

  factory UserProfile.fromJson(Map<String, dynamic> j) => UserProfile(
    username: (j['username'] ?? '') as String,
    role: (j['role'] ?? 'user') as String,
    fullName: (j['full_name'] ?? j['username'] ?? '') as String,
  );
}
