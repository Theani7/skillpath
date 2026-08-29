import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/analysis.dart';
import '../router.dart';
import '../services/api_client.dart';
import '../theme.dart';

class ResultScreen extends StatefulWidget {
  const ResultScreen({super.key});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _loading = true;
  String? _error;
  Analysis? _analysis;
  Map<String, dynamic> _raw = {};
  List<List<String>> _phaseTasks = const [];
  Map<String, bool> _progress = const {};
  List<dynamic> _plans = [];
  Map<String, dynamic>? _subscription;
  bool _billingLoading = true;

  @override
  void initState() {
    super.initState();
    _load();
    _loadBilling();
  }

  Future<void> _loadBilling() async {
    try {
      final plansRes = await Api.instance.dio.get('/api/billing/plans');
      final subRes = await Api.instance.dio.get('/api/billing/subscription');
      if (!mounted) return;
      setState(() {
        _plans = (plansRes.data is Map ? (plansRes.data as Map)['plans'] : null) as List? ?? [];
        _subscription = subRes.data is Map ? (subRes.data as Map)['subscription'] as Map<String, dynamic>? ?? (subRes.data as Map).cast<String, dynamic>() : null;
        _billingLoading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _billingLoading = false);
    }
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final res = await Api.instance.dio.get('/api/user/latest-analysis');
      final map = (res.data is Map) ? Map<String, dynamic>.from(res.data as Map) : <String, dynamic>{};
      final analysis = map['found'] == true ? Analysis.fromLatest(map) : null;
      final tasks = _extractPhaseTasks(map);
      var progress = const <String, bool>{};
      final id = analysis?.id;
      if (id != null && analysis != null) {
        try {
          final pRes = await Api.instance.dio.get('/api/user/roadmap-progress', queryParameters: {'analysis_id': id});
          final raw = (pRes.data is Map) ? (pRes.data as Map)['progress'] : null;
          if (raw is Map) progress = raw.map((k, v) => MapEntry(k.toString(), v == true));
        } catch (_) {}
      }
      if (!mounted) return;
      setState(() {
        _analysis = analysis;
        _raw = map;
        _phaseTasks = tasks;
        _progress = progress;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = Api.errorMessage(e);
        _loading = false;
      });
    }
  }

  static List<List<String>> _extractPhaseTasks(Map<String, dynamic> map) {
    final payload = (map['analysis'] as Map?)?.cast<String, dynamic>() ?? map;
    final roadmap = payload['roadmap'];
    if (roadmap is! List) return const [];
    return [
      for (final step in roadmap)
        if (step is Map) [for (final item in (step['action_items'] as List? ?? const [])) item.toString()],
    ];
  }

  Future<void> _toggleTask(int phaseIndex, int taskIndex, bool newVal) async {
    final id = _analysis?.id;
    if (id == null) return;
    final key = '$phaseIndex:$taskIndex';
    final previous = _progress[key] ?? false;
    setState(() => _progress = {..._progress, key: newVal});
    try {
      await Api.instance.dio.put('/api/user/roadmap-progress', data: {
        'analysis_id': id,
        'phase_index': phaseIndex,
        'task_index': taskIndex,
        'completed': newVal,
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _progress = {..._progress, key: previous});
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(Api.errorMessage(e))));
    }
  }

  Future<void> _rewrite() async {
    final analysis = _analysis;
    if (analysis == null) return;
    showDialog(context: context, barrierDismissible: false, builder: (_) => const Center(child: CircularProgressIndicator(color: T.secondary)));
    try {
      final resumeData = (_raw['analysis'] is Map ? (_raw['analysis'] as Map)['data'] : null) ?? {'skills': analysis.skills, 'experience': analysis.skills};
      final res = await Api.instance.dio.post('/api/rewrite-resume', data: {'target_role': analysis.targetRole, 'resume_data': resumeData});
      if (!mounted) return;
      Navigator.pop(context);
      final bullets = (res.data is Map ? (res.data as Map)['rewritten_bullets'] : null) as List?;
      showModalBottomSheet(context: context, isScrollControlled: true, backgroundColor: T.surface, shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(T.radiusXl))), builder: (ctx) => DraggableScrollableSheet(expand: false, initialChildSize: 0.7, maxChildSize: 0.9, builder: (_, sc) => ListView(controller: sc, padding: const EdgeInsets.fromLTRB(20, 16, 20, 24), children: [
            Row(children: [Container(height: 32, width: 32, decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.auto_fix_high, size: 16, color: Color(0xFF2563EB))), const SizedBox(width: 10), const Text('Rewritten Bullets', style: TextStyle(fontWeight: FontWeight.w800, color: T.text))]),
            const SizedBox(height: 12),
            if (bullets == null || bullets.isEmpty) const Text('No bullets returned', style: TextStyle(color: T.textMuted)),
            for (final b in (bullets ?? []))
              Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: T.bg, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: T.border)),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  if (b is Map && b['before'] != null) Text('Before: ${b['before']}', style: const TextStyle(fontSize: 12, color: T.textLight, decoration: TextDecoration.lineThrough)),
                  if (b is Map && b['after'] != null) ...[const SizedBox(height: 6), Text(b['after'].toString(), style: const TextStyle(fontSize: 13, color: T.text, fontWeight: FontWeight.w600))],
                ]),
              ),
          ])));
    } catch (e) {
      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(Api.errorMessage(e))));
      }
    }
  }

  Future<void> _jdCompare() async {
    final analysis = _analysis;
    if (analysis == null) return;
    final ctrl = TextEditingController();
    final jd = await showDialog<String>(context: context, builder: (ctx) => AlertDialog(
          title: const Text('JD Compare'),
          content: TextField(controller: ctrl, maxLines: 6, decoration: const InputDecoration(hintText: 'Paste job description…', border: OutlineInputBorder())),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusXl)),
          actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(ctx, ctrl.text.trim()), style: FilledButton.styleFrom(backgroundColor: T.primary), child: const Text('Compare', style: TextStyle(color: Colors.white)))],
        ));
    if (jd == null || jd.isEmpty) return;
    showDialog(context: context, barrierDismissible: false, builder: (_) => const Center(child: CircularProgressIndicator(color: T.secondary)));
    try {
      final res = await Api.instance.dio.post('/api/jd/compare', data: {'resume_skills': analysis.skills, 'job_description': jd});
      if (!mounted) return;
      Navigator.pop(context);
      final data = res.data as Map? ?? {};
      final cov = data['coverage_score']?.toString() ?? '0';
      final matched = (data['matched_keywords'] as List? ?? []).cast<String>();
      final missing = (data['missing_keywords'] as List? ?? []).cast<String>();
      showModalBottomSheet(context: context, backgroundColor: T.surface, shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(T.radiusXl))), builder: (ctx) => Padding(padding: const EdgeInsets.fromLTRB(20, 16, 20, 24), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [Container(height: 32, width: 32, decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.fact_check_outlined, size: 16, color: T.success)), const SizedBox(width: 10), Text('Coverage $cov%', style: const TextStyle(fontWeight: FontWeight.w800, color: T.text)), const Spacer(), ClipRRect(borderRadius: BorderRadius.circular(100), child: LinearProgressIndicator(value: (int.tryParse(cov) ?? 0) / 100, minHeight: 6, backgroundColor: T.borderLight, valueColor: AlwaysStoppedAnimation(int.parse(cov) >= 70 ? T.success : T.error)))]),
            const SizedBox(height: 12),
            if (matched.isNotEmpty) ...[const Text('Matched', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: T.success)), const SizedBox(height: 6), Wrap(spacing: 6, runSpacing: 6, children: [for (final m in matched.take(12)) Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: T.successLight, borderRadius: BorderRadius.circular(100)), child: Text(m, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF166534))))]), const SizedBox(height: 10)],
            if (missing.isNotEmpty) ...[const Text('Missing', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: T.error)), const SizedBox(height: 6), Wrap(spacing: 6, runSpacing: 6, children: [for (final m in missing.take(12)) Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: T.errorLight, borderRadius: BorderRadius.circular(100)), child: Text(m, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: T.error)))])],
          ])));
    } catch (e) {
      if (mounted) { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(Api.errorMessage(e)))); }
    }
  }

  Future<void> _projects() async {
    final analysis = _analysis;
    if (analysis == null) return;
    showDialog(context: context, barrierDismissible: false, builder: (_) => const Center(child: CircularProgressIndicator(color: T.secondary)));
    try {
      final res = await Api.instance.dio.post('/api/projects/recommend', data: {'target_role': analysis.targetRole, 'missing_skills': analysis.missingSkills.map((m) => m.name).toList()});
      if (!mounted) return;
      Navigator.pop(context);
      final projs = (res.data is Map ? (res.data as Map)['projects'] : null) as List? ?? [];
      showModalBottomSheet(context: context, isScrollControlled: true, backgroundColor: T.surface, shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(T.radiusXl))), builder: (ctx) => DraggableScrollableSheet(expand: false, initialChildSize: 0.6, maxChildSize: 0.9, builder: (_, sc) => ListView(controller: sc, padding: const EdgeInsets.fromLTRB(20, 16, 20, 24), children: [
            Row(children: [Container(height: 32, width: 32, decoration: BoxDecoration(color: const Color(0xFFFFEDD5), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.lightbulb_outline, size: 16, color: T.secondaryDark)), const SizedBox(width: 10), const Text('Recommended Projects', style: TextStyle(fontWeight: FontWeight.w800, color: T.text))]),
            const SizedBox(height: 12),
            for (final p in projs)
              Container(margin: const EdgeInsets.only(bottom: 10), padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: T.bg, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: T.border)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text((p as Map)['title']?.toString() ?? '', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: T.text)),
                    const SizedBox(height: 4),
                    Text((p['objective'] ?? '').toString(), style: const TextStyle(fontSize: 12, color: T.textMuted)),
                    const SizedBox(height: 6),
                    Text('${p['estimated_weeks'] ?? 2} weeks', style: const TextStyle(fontSize: 11, color: T.textLight, fontWeight: FontWeight.w700)),
                  ])),
          ])));
    } catch (e) {
      if (mounted) { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(Api.errorMessage(e)))); }
    }
  }

  Future<void> _subscribe(String plan) async {
    try {
      await Api.instance.dio.post('/api/billing/subscribe', data: {'plan': plan});
      _loadBilling();
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Subscribed to $plan')));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(Api.errorMessage(e))));
    }
  }

  String get _level {
    final s = (_analysis?.resumeScore ?? 0).clamp(0, 100);
    if (s >= 85) return 'excellent';
    if (s >= 70) return 'good';
    if (s >= 50) return 'fair';
    return 'low';
  }

  Color get _levelColor => switch (_level) {
        'excellent' => T.success,
        'good' => const Color(0xFF2563EB),
        'fair' => const Color(0xFFD97706),
        _ => T.error,
      };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          Positioned(
            top: -120, right: -100,
            child: Container(
              width: 360, height: 360,
              decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.primary.withValues(alpha: 0.06), Colors.transparent])),
            ),
          ),
          Positioned(
            bottom: -140, left: -140,
            child: Container(
              width: 380, height: 380,
              decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.secondary.withValues(alpha: 0.05), Colors.transparent])),
            ),
          ),
          SafeArea(
            child: RefreshIndicator(
              onRefresh: _load,
              color: T.secondary,
              child: _buildBody(context),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
        children: [
          const SizedBox(height: 40),
          Center(
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
              child: const Column(
                children: [
                  SizedBox(height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2.5, color: T.secondary)),
                  SizedBox(height: 12),
                  Text('Loading your results…', style: TextStyle(fontSize: 13, color: T.textMuted, fontWeight: FontWeight.w600)),
                ],
              ),
            ),
          ),
        ],
      );
    }
    if (_error != null) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        children: [
          const SizedBox(height: 80),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
            child: Column(
              children: [
                Container(height: 48, width: 48, decoration: const BoxDecoration(color: T.errorLight, shape: BoxShape.circle), child: const Icon(Icons.cloud_off_outlined, color: T.error)),
                const SizedBox(height: 12),
                Text(_error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: T.text)),
                const SizedBox(height: 16),
                FilledButton.tonalIcon(onPressed: _load, icon: const Icon(Icons.refresh, size: 18), label: const Text('Retry')),
              ],
            ),
          ),
        ],
      );
    }
    final analysis = _analysis;
    if (analysis == null) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        children: [
          const SizedBox(height: 32),
          Container(
            padding: const EdgeInsets.fromLTRB(20, 28, 20, 28),
            decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
            child: Column(
              children: [
                Container(
                  height: 64, width: 64,
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(18), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                  child: ClipRRect(borderRadius: BorderRadius.circular(10), child: Image.asset('assets/icon.png', fit: BoxFit.contain)),
                ),
                const SizedBox(height: 16),
                Text('No analysis yet', style: displayStyle(context, 20)),
                const SizedBox(height: 8),
                const Text('Upload a resume to get your AI-powered report', textAlign: TextAlign.center, style: TextStyle(fontSize: 13.5, color: T.textMuted, height: 1.5)),
                const SizedBox(height: 20),
                FilledButton.icon(onPressed: () => context.go(Routes.home), icon: const Icon(Icons.cloud_upload_outlined, size: 18, color: Colors.white), label: const Text('Upload a resume', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)), style: FilledButton.styleFrom(backgroundColor: T.primary, foregroundColor: Colors.white, minimumSize: const Size.fromHeight(46), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)))),
              ],
            ),
          ),
        ],
      );
    }

    final clamped = analysis.resumeScore.clamp(0.0, 100.0);
    final label = clamped == clamped.roundToDouble() ? clamped.toStringAsFixed(0) : clamped.toStringAsFixed(1);

    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      children: [
        // ── header eyebrow
        Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
            decoration: BoxDecoration(color: T.navy100.withValues(alpha: 0.6), borderRadius: BorderRadius.circular(100), border: Border.all(color: T.navy100)),
            child: const Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.insights, size: 11, color: T.primary),
              SizedBox(width: 6),
              Text('YOUR RESULTS • AI-POWERED', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.08 * 11, color: T.primary)),
            ]),
          ),
        ),
        const SizedBox(height: 14),
        Text('Your Report', textAlign: TextAlign.center, style: displayStyle(context, 28)),
        const SizedBox(height: 6),
        Text('${analysis.predictedField.isNotEmpty ? '${analysis.predictedField} • ' : ''}Target: ${analysis.targetRole}',
            textAlign: TextAlign.center, style: const TextStyle(fontSize: 13, color: T.textMuted, fontWeight: FontWeight.w600)),
        const SizedBox(height: 18),

        // ── Hero score card
        Container(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 18),
          decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
          child: Row(
            children: [
              SizedBox(
                width: 110, height: 110,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    SizedBox(width: 110, height: 110, child: CircularProgressIndicator(value: clamped / 100, strokeWidth: 8, strokeCap: StrokeCap.round, backgroundColor: T.borderLight, valueColor: AlwaysStoppedAnimation(_levelColor))),
                    Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('$label%', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: T.text, letterSpacing: -0.02 * 22)),
                        const SizedBox(height: 2),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(color: _levelColor.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(100), border: Border.all(color: _levelColor.withValues(alpha: 0.2))),
                          child: Text(_level.toUpperCase(), style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, letterSpacing: 0.08 * 9, color: _levelColor)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 18),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Resume Score', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: T.text)),
                    const SizedBox(height: 4),
                    const Text('How well your resume matches your target role.',
                        style: TextStyle(fontSize: 12.5, color: T.textMuted, height: 1.4)),
                    const SizedBox(height: 10),
                    Wrap(spacing: 6, runSpacing: 6, children: [
                      if (analysis.predictedField.isNotEmpty) _Pill(text: analysis.predictedField, bg: const Color(0xFFF0F4F8), fg: T.primary),
                      _Pill(text: 'Target: ${analysis.targetRole}', bg: T.successLight, fg: const Color(0xFF166534)),
                    ]),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 10),
        // meta line
        if (analysis.pdfName != null || analysis.timestamp != null)
          Row(
            children: [
              const Icon(Icons.insert_drive_file_outlined, size: 13, color: T.textLight),
              const SizedBox(width: 6),
              Expanded(child: Text([if (analysis.pdfName != null) analysis.pdfName!, if (analysis.timestamp != null) analysis.timestamp!].join(' • '), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w600))),
            ],
          ),
        const SizedBox(height: 16),

        // Existing skills
        if (analysis.skills.isNotEmpty) ...[
          _SectionCard(
            icon: Icons.check_circle_outline, iconBg: const Color(0xFFDCFCE7), iconColor: T.success,
            title: 'Existing Skills', subtitle: '${analysis.skills.length} strengths detected',
            child: Wrap(spacing: 8, runSpacing: 8, children: [for (final s in analysis.skills) Chip(label: Text(s, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)), backgroundColor: T.navy100, side: BorderSide.none, visualDensity: VisualDensity.compact, padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2))]),
          ),
          const SizedBox(height: 12),
        ],

        // Missing skills
        if (analysis.missingSkills.isNotEmpty) ...[
          _SectionCard(
            icon: Icons.priority_high, iconBg: T.errorLight, iconColor: T.error,
            title: 'Skill Gaps', subtitle: '${analysis.missingSkills.length} gaps to close • focus here',
            child: Wrap(spacing: 8, runSpacing: 8, children: [
              for (final m in analysis.missingSkills)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(color: T.errorLight, borderRadius: BorderRadius.circular(100), border: Border.all(color: const Color(0xFFFECACA))),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    const Icon(Icons.priority_high_rounded, size: 12, color: T.error),
                    const SizedBox(width: 4),
                    Text(m.name, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: T.error)),
                  ]),
                ),
            ]),
          ),
          const SizedBox(height: 12),
        ],

        // Score breakdown — horizontal cards like web (ScoreBreakdown.tsx)
        if (analysis.scoreBreakdown.isNotEmpty) ...[
          _SectionCard(
            icon: Icons.bar_chart_rounded, iconBg: const Color(0xFFFFEDD5), iconColor: T.secondaryDark,
            title: 'Score Breakdown', subtitle: 'Weighted dimensions',
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  for (final e in analysis.scoreBreakdown.entries)
                    Builder(builder: (context) {
                      final dynamic raw = e.value;
                      num score = 0;
                      num weight = 0;
                      String status = 'present';
                      if (raw is Map) {
                        score = (raw['score'] as num?) ?? 0;
                        weight = (raw['weight'] as num?) ?? 0;
                        status = raw['status']?.toString() ?? 'present';
                      } else if (raw is num) {
                        score = raw;
                      }
                      final present = status == 'present';
                      final label = e.key.replaceAll('_', ' ');
                      final pct = weight > 0 ? (score / weight).clamp(0.0, 1.0) : (score / 100).clamp(0.0, 1.0);
                      return Container(
                        width: 132,
                        margin: const EdgeInsets.only(right: 10),
                        padding: const EdgeInsets.fromLTRB(12, 12, 12, 12),
                        decoration: BoxDecoration(color: T.bg, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: T.border)),
                        child: Column(
                          children: [
                            Text(score.toStringAsFixed(score.truncateToDouble() == score ? 0 : 1), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: T.primary)),
                            const SizedBox(height: 2),
                            Text(label, textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 0.04 * 10, color: T.textMuted)),
                            const SizedBox(height: 8),
                            ClipRRect(borderRadius: BorderRadius.circular(100), child: LinearProgressIndicator(value: pct, minHeight: 4, backgroundColor: T.borderLight, valueColor: AlwaysStoppedAnimation(present ? T.success : T.error))),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(color: present ? const Color(0xFFDCFCE7) : T.errorLight, borderRadius: BorderRadius.circular(100)),
                              child: Text(present ? 'Optimal' : 'Missing', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: present ? const Color(0xFF166534) : T.error)),
                            ),
                          ],
                        ),
                      );
                    }),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
        ],

        // Roadmap
        if (analysis.roadmap.isNotEmpty) ...[
          _SectionCard(
            icon: Icons.map_outlined, iconBg: const Color(0xFFF0F4F8), iconColor: T.primary,
            title: 'AI Career Roadmap', subtitle: 'Personalized learning path to close your gaps',
            child: Column(children: [
              for (var i = 0; i < analysis.roadmap.length; i++)
                _RoadmapStepTile(
                  phaseIndex: i,
                  step: analysis.roadmap[i],
                  tasks: i < _phaseTasks.length ? _phaseTasks[i] : const [],
                  progress: _progress,
                  onToggle: _toggleTask,
                ),
            ]),
          ),
          const SizedBox(height: 12),
        ],

        // Toolkit
        _SectionCard(
          icon: Icons.build_outlined, iconBg: const Color(0xFFFFEDD5), iconColor: T.secondaryDark,
          title: 'Career Toolkit', subtitle: 'AI-powered actions for this report',
          child: Wrap(spacing: 8, runSpacing: 8, children: [
            _ToolkitChip(icon: Icons.auto_fix_high, label: 'Rewrite Resume', onTap: _rewrite),
            _ToolkitChip(icon: Icons.fact_check_outlined, label: 'JD Compare', onTap: _jdCompare),
            _ToolkitChip(icon: Icons.lightbulb_outline, label: 'Projects', onTap: _projects),
          ]),
        ),
        const SizedBox(height: 12),

        // Paywall teaser
        Container(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [T.primary, Color(0xFF1A2D4A)], begin: Alignment.topLeft, end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(T.radiusXl),
            boxShadow: T.cardShadow,
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Container(height: 28, width: 28, decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.workspace_premium, size: 14, color: Colors.white)),
              const SizedBox(width: 8),
              const Expanded(child: Text('Go Pro — unlock everything', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Colors.white))),
              if (!_billingLoading && _subscription != null)
                Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3), decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.14), borderRadius: BorderRadius.circular(100)), child: Text((_subscription!['plan'] ?? 'free').toString().toUpperCase(), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white))),
            ]),
            const SizedBox(height: 8),
            const Text('Advanced rewrite, interview packs, team ranking and priority support.', style: TextStyle(fontSize: 12, color: Colors.white70, height: 1.4)),
            const SizedBox(height: 12),
            if (_billingLoading)
              const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
            else
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(children: [
                  for (final p in _plans)
                    Container(
                      width: 150,
                      margin: const EdgeInsets.only(right: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(T.radiusLg)),
                      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Text((p['id'] ?? '').toString().toUpperCase(), style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.06 * 11, color: T.primary)),
                        const SizedBox(height: 4),
                        Text('\$${p['price_usd_month'] ?? 0}/mo', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: T.text)),
                        const SizedBox(height: 6),
                        Text(((p['features'] as List? ?? []).take(2).join(' • ')), maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10, color: T.textMuted)),
                        const SizedBox(height: 8),
                        SizedBox(
                          width: double.infinity,
                          child: FilledButton(
                            onPressed: () => _subscribe((p['id'] ?? 'free').toString()),
                            style: FilledButton.styleFrom(backgroundColor: p['id'] == 'pro' ? T.secondary : T.primary, padding: const EdgeInsets.symmetric(vertical: 8), minimumSize: Size.zero, tapTargetSize: MaterialTapTargetSize.shrinkWrap, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
                            child: Text(p['id'] == (_subscription?['plan'] ?? 'free') ? 'Current' : 'Upgrade', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.white)),
                          ),
                        ),
                      ]),
                    ),
                ]),
              ),
          ]),
        ),
        const SizedBox(height: 12),

        // Actions
        Row(
          children: [
            Expanded(child: OutlinedButton.icon(onPressed: () => context.go(Routes.home), icon: const Icon(Icons.refresh, size: 16), label: const Text('Re-analyze'))),
            const SizedBox(width: 10),
            Expanded(child: FilledButton.icon(onPressed: _load, icon: const Icon(Icons.analytics_outlined, size: 16, color: Colors.white), label: const Text('Refresh', style: TextStyle(color: Colors.white)), style: FilledButton.styleFrom(backgroundColor: T.primary))),
          ],
        ),
        const SizedBox(height: 8),
      ],
    );
  }
}

class _Pill extends StatelessWidget {
  final String text;
  final Color bg;
  final Color fg;
  const _Pill({required this.text, required this.bg, required this.fg});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(100), border: Border.all(color: fg.withValues(alpha: 0.15))),
      child: Text(text, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: fg)),
    );
  }
}

class _ToolkitChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _ToolkitChip({required this.icon, required this.label, required this.onTap});
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(100),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(color: T.primary, borderRadius: BorderRadius.circular(100)),
        child: Row(mainAxisSize: MainAxisSize.min, children: [Icon(icon, size: 14, color: Colors.white), const SizedBox(width: 6), Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Colors.white))]),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String title;
  final String subtitle;
  final Widget child;
  const _SectionCard({required this.icon, required this.iconBg, required this.iconColor, required this.title, required this.subtitle, required this.child});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(height: 30, width: 30, decoration: BoxDecoration(color: iconBg, borderRadius: BorderRadius.circular(8)), child: Icon(icon, size: 16, color: iconColor)),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title, style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w800, color: T.text)),
              Text(subtitle, style: const TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w500)),
            ])),
          ]),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }
}

String _durationLabel(Object? durationWeeks) {
  if (durationWeeks == null) return '';
  final s = durationWeeks.toString();
  if (s.isEmpty || s.toLowerCase().contains('week')) return s;
  return '$s weeks';
}

Future<void> launchExternal(BuildContext context, String url) async {
  final uri = Uri.tryParse(url);
  if (uri == null || !uri.hasScheme) return;
  try {
    await launchUrl(uri, mode: LaunchMode.externalApplication);
  } catch (_) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not open $url')));
  }
}

class _RoadmapStepTile extends StatelessWidget {
  final int phaseIndex;
  final RoadmapStep step;
  final List<String> tasks;
  final Map<String, bool> progress;
  final void Function(int phaseIndex, int taskIndex, bool completed) onToggle;
  const _RoadmapStepTile({required this.phaseIndex, required this.step, required this.tasks, required this.progress, required this.onToggle});
  @override
  Widget build(BuildContext context) {
    var doneCount = 0;
    for (var i = 0; i < tasks.length; i++) {
      if (progress['$phaseIndex:$i'] == true) doneCount++;
    }
    final subtitleParts = [if (_durationLabel(step.durationWeeks).isNotEmpty) _durationLabel(step.durationWeeks), if (tasks.isNotEmpty) '$doneCount/${tasks.length} tasks'];
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(color: T.bg, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: T.border)),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
        childrenPadding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
        collapsedShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
        title: Text(step.title.isEmpty ? 'Phase ${phaseIndex + 1}' : step.title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: T.text)),
        subtitle: subtitleParts.isEmpty ? null : Text(subtitleParts.join(' • '), style: const TextStyle(fontSize: 11, color: T.textMuted, fontWeight: FontWeight.w600)),
        children: [
          if (step.description.isNotEmpty) Align(alignment: Alignment.centerLeft, child: Text(step.description, style: const TextStyle(fontSize: 12.5, color: T.textMuted, height: 1.5))),
          if (step.skills.isNotEmpty) ...[
            const SizedBox(height: 10),
            Align(alignment: Alignment.centerLeft, child: Wrap(spacing: 6, runSpacing: 6, children: [for (final s in step.skills) Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: T.navy100, borderRadius: BorderRadius.circular(100)), child: Text(s, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: T.navy900)))])),
          ],
          if (tasks.isNotEmpty) ...[
            const Divider(height: 20, color: T.borderLight),
            const Align(alignment: Alignment.centerLeft, child: Text('Action items', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.06 * 11, color: T.textMuted))),
            for (var t = 0; t < tasks.length; t++)
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                dense: true,
                controlAffinity: ListTileControlAffinity.leading,
                title: Text(tasks[t], style: TextStyle(fontSize: 12.5, color: progress['$phaseIndex:$t'] == true ? T.textLight : T.text, decoration: progress['$phaseIndex:$t'] == true ? TextDecoration.lineThrough : null)),
                value: progress['$phaseIndex:$t'] == true,
                activeColor: T.primary,
                onChanged: (v) => onToggle(phaseIndex, t, v ?? false),
              ),
          ],
          if (step.resources.isNotEmpty) ...[
            const Divider(height: 20, color: T.borderLight),
            for (final r in step.resources)
              ListTile(
                contentPadding: EdgeInsets.zero,
                dense: true,
                leading: Container(height: 28, width: 28, decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(6), border: Border.all(color: T.border)), child: const Icon(Icons.link, size: 14, color: T.textMuted)),
                title: Text(r.title, style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600, color: T.text)),
                trailing: const Icon(Icons.open_in_new, size: 14, color: T.textLight),
                onTap: () => launchExternal(context, r.url),
              ),
          ],
        ],
      ),
    );
  }
}
