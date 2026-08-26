import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/analysis.dart';
import '../router.dart';
import '../services/api_client.dart';

class ResultScreen extends StatefulWidget {
  const ResultScreen({super.key});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _loading = true;
  String? _error;
  Analysis? _analysis;

  /// Action items ("tasks") per roadmap phase, extracted from the raw
  /// payload because [Analysis] does not model them.
  List<List<String>> _phaseTasks = const [];
  Map<String, bool> _progress = const {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final res = await Api.instance.dio.get('/api/user/latest-analysis');
      final map = (res.data is Map)
          ? Map<String, dynamic>.from(res.data as Map)
          : <String, dynamic>{};
      final analysis = map['found'] == true ? Analysis.fromLatest(map) : null;

      final tasks = _extractPhaseTasks(map);

      var progress = const <String, bool>{};
      final id = analysis?.id;
      if (id != null && analysis != null) {
        try {
          final pRes = await Api.instance.dio.get(
            '/api/user/roadmap-progress',
            queryParameters: {'analysis_id': id},
          );
          final raw = (pRes.data is Map)
              ? (pRes.data as Map)['progress']
              : null;
          if (raw is Map) {
            progress = raw.map((k, v) => MapEntry(k.toString(), v == true));
          }
        } catch (_) {
          // Progress is optional — render without saved state.
        }
      }

      if (!mounted) return;
      setState(() {
        _analysis = analysis;
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

  /// Pull `action_items` per roadmap phase straight from the response map.
  static List<List<String>> _extractPhaseTasks(Map<String, dynamic> map) {
    final payload = (map['analysis'] as Map?)?.cast<String, dynamic>() ?? map;
    final roadmap = payload['roadmap'];
    if (roadmap is! List) return const [];
    return [
      for (final step in roadmap)
        if (step is Map)
          [
            for (final item in (step['action_items'] as List? ?? const []))
              item.toString(),
          ],
    ];
  }

  Future<void> _toggleTask(int phaseIndex, int taskIndex, bool newVal) async {
    final id = _analysis?.id;
    if (id == null) return;
    final key = '$phaseIndex:$taskIndex';
    final previous = _progress[key] ?? false;

    // Optimistic update.
    setState(() => _progress = {..._progress, key: newVal});
    try {
      await Api.instance.dio.put(
        '/api/user/roadmap-progress',
        data: {
          'analysis_id': id,
          'phase_index': phaseIndex,
          'task_index': taskIndex,
          'completed': newVal,
        },
      );
    } catch (e) {
      if (!mounted) return;
      // Revert on failure.
      setState(() => _progress = {..._progress, key: previous});
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(Api.errorMessage(e))));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your Results')),
      body: RefreshIndicator(onRefresh: _load, child: _buildBody(context)),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          SizedBox(height: 160),
          Center(child: CircularProgressIndicator()),
        ],
      );
    }

    if (_error != null) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        children: [
          const SizedBox(height: 120),
          Icon(
            Icons.cloud_off_outlined,
            size: 48,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: 16),
          Text(
            _error!,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          const SizedBox(height: 16),
          Center(
            child: FilledButton.tonalIcon(
              onPressed: _load,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
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
          const SizedBox(height: 120),
          Icon(
            Icons.description_outlined,
            size: 48,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: 16),
          Text(
            'No analysis yet',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            'Upload a resume to get started',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),
          Center(
            child: FilledButton.icon(
              onPressed: () => context.go(Routes.home),
              icon: const Icon(Icons.upload_file_outlined),
              label: const Text('Upload a resume'),
            ),
          ),
        ],
      );
    }

    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      children: [
        _ScoreHeader(score: analysis.resumeScore),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            if (analysis.predictedField.isNotEmpty)
              Chip(
                avatar: const Icon(Icons.category_outlined, size: 18),
                label: Text(analysis.predictedField),
              ),
            Chip(
              avatar: const Icon(Icons.work_outline, size: 18),
              label: Text('Target: ${analysis.targetRole}'),
            ),
          ],
        ),
        if (analysis.pdfName != null || analysis.timestamp != null)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Row(
              children: [
                Icon(
                  Icons.insert_drive_file_outlined,
                  size: 16,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    [
                      if (analysis.pdfName != null) analysis.pdfName!,
                      if (analysis.timestamp != null) analysis.timestamp!,
                    ].join(' • '),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ],
            ),
          ),
        if (analysis.skills.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text(
            'Existing skills',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          _SkillChips(skills: analysis.skills, highlight: false),
        ],
        if (analysis.missingSkills.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text(
            'Missing skills',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          _SkillChips(
            skills: analysis.missingSkills.map((m) => m.name).toList(),
            highlight: true,
          ),
        ],
        if (analysis.scoreBreakdown.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text(
            'Score breakdown',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Card(
            margin: EdgeInsets.zero,
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                for (final entry in analysis.scoreBreakdown.entries)
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 10,
                    ),
                    child: Row(
                      children: [
                        Expanded(child: Text(entry.key)),
                        Text(
                          entry.value.toString(),
                          style: Theme.of(context).textTheme.titleSmall
                              ?.copyWith(
                                color: Theme.of(context).colorScheme.primary,
                              ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
        if (analysis.roadmap.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text('Roadmap', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          for (var i = 0; i < analysis.roadmap.length; i++)
            _RoadmapStepTile(
              phaseIndex: i,
              step: analysis.roadmap[i],
              tasks: i < _phaseTasks.length ? _phaseTasks[i] : const [],
              progress: _progress,
              onToggle: _toggleTask,
            ),
        ],
        const SizedBox(height: 32),
      ],
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
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('Could not open $url')));
  }
}

class _ScoreHeader extends StatelessWidget {
  final double score;

  const _ScoreHeader({required this.score});

  @override
  Widget build(BuildContext context) {
    final clamped = score.clamp(0.0, 100.0);
    final label = clamped == clamped.roundToDouble()
        ? clamped.toStringAsFixed(0)
        : clamped.toStringAsFixed(1);
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            SizedBox(
              width: 96,
              height: 96,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  CircularProgressIndicator(
                    value: clamped / 100,
                    strokeWidth: 8,
                    strokeCap: StrokeCap.round,
                  ),
                  Center(
                    child: Text(
                      '$label%',
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Resume score',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'How well your resume matches your target role.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SkillChips extends StatelessWidget {
  final List<String> skills;
  final bool highlight;

  const _SkillChips({required this.skills, required this.highlight});

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final skill in skills)
          highlight
              ? Container(
                  decoration: BoxDecoration(
                    color: Theme.of(
                      context,
                    ).colorScheme.errorContainer.withValues(alpha: 0.55),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.priority_high_rounded,
                        size: 14,
                        color: Theme.of(context).colorScheme.onErrorContainer,
                      ),
                      const SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          skill,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: Theme.of(
                              context,
                            ).colorScheme.onErrorContainer,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                )
              : Chip(label: Text(skill), visualDensity: VisualDensity.compact),
      ],
    );
  }
}

class _RoadmapStepTile extends StatelessWidget {
  final int phaseIndex;
  final RoadmapStep step;
  final List<String> tasks;
  final Map<String, bool> progress;
  final void Function(int phaseIndex, int taskIndex, bool completed) onToggle;

  const _RoadmapStepTile({
    required this.phaseIndex,
    required this.step,
    required this.tasks,
    required this.progress,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    var doneCount = 0;
    for (var i = 0; i < tasks.length; i++) {
      if (progress['$phaseIndex:$i'] == true) doneCount++;
    }
    final subtitleParts = [
      if (_durationLabel(step.durationWeeks).isNotEmpty)
        _durationLabel(step.durationWeeks),
      if (tasks.isNotEmpty) '$doneCount/${tasks.length} tasks',
    ];

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      clipBehavior: Clip.antiAlias,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16),
        childrenPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 8,
        ),
        title: Text(
          step.title.isEmpty ? 'Phase ${phaseIndex + 1}' : step.title,
          style: Theme.of(
            context,
          ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
        ),
        subtitle: subtitleParts.isEmpty
            ? null
            : Text(subtitleParts.join(' • ')),
        children: [
          if (step.description.isNotEmpty)
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Text(step.description),
            ),
          if (step.skills.isNotEmpty) ...[
            const SizedBox(height: 12),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Wrap(
                spacing: 6,
                runSpacing: 6,
                children: [
                  for (final skill in step.skills)
                    Chip(
                      label: Text(skill),
                      visualDensity: VisualDensity.compact,
                    ),
                ],
              ),
            ),
          ],
          if (tasks.isNotEmpty) ...[
            const Divider(height: 24),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Text(
                'Action items',
                style: Theme.of(context).textTheme.labelLarge,
              ),
            ),
            for (var t = 0; t < tasks.length; t++)
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                dense: true,
                controlAffinity: ListTileControlAffinity.leading,
                title: Text(tasks[t]),
                value: progress['$phaseIndex:$t'] == true,
                onChanged: (value) => onToggle(phaseIndex, t, value ?? false),
              ),
          ],
          if (step.resources.isNotEmpty) ...[
            const Divider(height: 24),
            for (final resource in step.resources)
              ListTile(
                contentPadding: EdgeInsets.zero,
                dense: true,
                leading: const Icon(Icons.link),
                title: Text(resource.title),
                trailing: const Icon(Icons.open_in_new, size: 18),
                onTap: () => launchExternal(context, resource.url),
              ),
          ],
        ],
      ),
    );
  }
}
