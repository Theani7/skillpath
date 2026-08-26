/// Resume analysis payload as returned by POST /api/analyze and
/// GET /api/user/latest-analysis (`analysis` field).
///
/// All fields are tolerant of missing keys — old rows synthesize partials.
class Analysis {
  final int? id;
  final String? timestamp;
  final String? pdfName;
  final String targetRole;
  final String predictedField;
  final double resumeScore;
  final String name;
  final String email;
  final List<String> skills;
  final List<String> recommendedSkills;
  final List<MissingSkill> missingSkills;
  final List<RoadmapStep> roadmap;
  final Map<String, dynamic> scoreBreakdown;

  const Analysis({
    this.id,
    this.timestamp,
    this.pdfName,
    required this.targetRole,
    required this.predictedField,
    required this.resumeScore,
    required this.name,
    required this.email,
    required this.skills,
    required this.recommendedSkills,
    required this.missingSkills,
    required this.roadmap,
    required this.scoreBreakdown,
  });

  static List<T> _listOf<T>(Object? raw, T Function(Object?) map) =>
      raw is List ? raw.map(map).whereType<T>().toList() : const [];

  factory Analysis.fromLatest(Map<String, dynamic> j) {
    final payload = (j['analysis'] as Map?)?.cast<String, dynamic>() ?? j;
    return Analysis._build(j, payload);
  }

  factory Analysis.fromAnalyze(Object? raw) =>
      Analysis._build(null, (raw as Map).cast<String, dynamic>());

  factory Analysis._build(Map<String, dynamic>? top, Map<String, dynamic> p) {
    final data = (p['data'] as Map?)?.cast<String, dynamic>() ?? const {};
    final score = top?['resume_score'] ?? p['resume_score'];
    return Analysis(
      id: top?['id'] as int?,
      timestamp: top?['timestamp'] as String?,
      pdfName: (top?['pdf_name'] ?? p['pdf_name']) as String?,
      targetRole:
          ((top?['target_role'] ?? p['target_role']) ?? 'General') as String,
      predictedField:
          ((top?['predicted_field'] ?? p['predicted_field']) ?? '') as String,
      resumeScore: score is num ? score.toDouble() : 0,
      name: (data['name'] ?? '') as String,
      email: (data['email'] ?? '') as String,
      skills: _listOf(data['skills'], (s) => s.toString()),
      recommendedSkills: _listOf(p['recommended_skills'], (s) => s.toString()),
      missingSkills: _listOf(
        p['missing_skill_names'],
        (s) => MissingSkill(name: s.toString()),
      ),
      roadmap: _listOf(p['roadmap'], (step) => RoadmapStep.fromJson(step)),
      scoreBreakdown:
          (p['score_breakdown'] as Map?)?.cast<String, dynamic>() ?? const {},
    );
  }
}

class MissingSkill {
  final String name;
  const MissingSkill({required this.name});
}

class RoadmapStep {
  final String title;
  final String description;
  final Object? durationWeeks;
  final List<String> skills;
  final List<ResourceLink> resources;

  const RoadmapStep({
    required this.title,
    required this.description,
    this.durationWeeks,
    required this.skills,
    required this.resources,
  });

  factory RoadmapStep.fromJson(Object? raw) {
    final m = (raw as Map?)?.cast<String, dynamic>() ?? const {};
    final resources = Analysis._listOf(m['resources'], (r) {
      if (r is Map && r['title'] != null && r['url'] != null) {
        return ResourceLink(
          title: r['title'].toString(),
          url: r['url'].toString(),
        );
      }
      // Backend also sends plain "Skill1,Skill2" strings in some paths.
      return null;
    }).whereType<ResourceLink>().toList();
    return RoadmapStep(
      title: (m['title'] ?? '').toString(),
      description: (m['description'] ?? '').toString(),
      durationWeeks: m['duration_weeks'],
      skills: Analysis._listOf(m['skills'], (s) => s.toString()),
      resources: resources,
    );
  }
}

class ResourceLink {
  final String title;
  final String url;
  const ResourceLink({required this.title, required this.url});
}
