import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../services/api_client.dart';

/// One entry in the chat transcript.
class _ChatMessage {
  final String text;
  final bool isUser;

  /// Feedback cards get a distinct assistant-styled look.
  final bool isFeedback;

  const _ChatMessage(
    this.text, {
    required this.isUser,
    this.isFeedback = false,
  });
}

enum _Phase { loadingRoles, pick, chatting, evaluating, done }

class InterviewScreen extends StatefulWidget {
  const InterviewScreen({super.key});

  @override
  State<InterviewScreen> createState() => _InterviewScreenState();
}

class _InterviewScreenState extends State<InterviewScreen> {
  _Phase _phase = _Phase.loadingRoles;
  List<String> _roles = [];
  String? _selectedRole;

  String? _sessionId;
  String _currentQuestion = '';
  final List<_ChatMessage> _messages = [];
  final List<Map<String, String>> _history = [];
  final TextEditingController _answerCtrl = TextEditingController();
  final ScrollController _scrollCtrl = ScrollController();

  Map<String, dynamic> _evaluation = {};
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _loadRoles();
  }

  @override
  void dispose() {
    _answerCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadRoles() async {
    setState(() => _phase = _Phase.loadingRoles);
    try {
      final res = await Api.instance.dio.get('/api/mock-interview');
      if (res.statusCode != 200 || res.data is! Map) {
        _setError('Could not load interview roles.');
        return;
      }
      final roles = (res.data['roles'] as List? ?? [])
          .map((e) => e.toString())
          .toList();
      if (!mounted) return;
      setState(() {
        _roles = roles;
        _selectedRole = roles.isNotEmpty ? roles.first : null;
        _phase = _Phase.pick;
      });
      if (roles.isEmpty) return;
      // Best effort: preselect the user's last analyzed target role.
      try {
        final la = await Api.instance.dio.get('/api/user/latest-analysis');
        if (la.statusCode == 200 && la.data is Map) {
          final target = la.data['target_role']?.toString();
          if (target != null && roles.contains(target) && mounted) {
            setState(() => _selectedRole = target);
          }
        }
      } catch (_) {
        /* prefill is optional */
      }
    } catch (e) {
      _setError(Api.errorMessage(e));
    }
  }

  void _setError(String msg) {
    if (!mounted) return;
    setState(() => _phase = _Phase.pick);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  Future<void> _startSession() async {
    final role = _selectedRole;
    if (role == null) return;
    setState(() => _busy = true);
    try {
      final res = await Api.instance.dio.post(
        '/api/mock-interview/start',
        data: {'role': role},
      );
      if (res.statusCode != 200 || res.data is! Map) {
        _setError(_messageFrom(res) ?? 'Could not start the interview.');
        return;
      }
      final data = res.data as Map;
      final question = data['question']?.toString() ?? '';
      if (!mounted) return;
      setState(() {
        _sessionId = data['session_id']?.toString();
        _currentQuestion = question;
        _messages.clear();
        _history.clear();
        _evaluation = {};
        _messages.add(_ChatMessage(question, isUser: false));
        _phase = _Phase.chatting;
        _busy = false;
      });
      _scrollToBottom();
    } catch (e) {
      _setError(Api.errorMessage(e));
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _sendAnswer() async {
    final answer = _answerCtrl.text.trim();
    if (answer.isEmpty || _busy || _sessionId == null) return;
    final question = _currentQuestion;
    FocusManager.instance.primaryFocus?.unfocus();
    setState(() {
      _busy = true;
      _messages.add(_ChatMessage(answer, isUser: true));
      _answerCtrl.clear();
    });
    _scrollToBottom();
    try {
      final res = await Api.instance.dio.post(
        '/api/mock-interview/answer',
        data: {
          'session_id': _sessionId,
          'question': question,
          'answer': answer,
          'role': _selectedRole,
          'chat_history': _history,
        },
      );
      if (res.statusCode == 404 ||
          (res.data is Map &&
              (res.data['detail'] ?? '').toString().contains(
                'Session not found',
              ))) {
        _sessionExpired();
        return;
      }
      if (res.statusCode != 200 || res.data is! Map) {
        if (!mounted) return;
        setState(() {
          _busy = false;
          _messages.add(
            _ChatMessage(
              _messageFrom(res) ?? 'Failed to send answer.',
              isUser: false,
              isFeedback: true,
            ),
          );
        });
        _scrollToBottom();
        return;
      }
      final data = res.data as Map;
      final feedback = data['feedback']?.toString() ?? '';
      final nextQuestion = data['next_question']?.toString() ?? '';
      if (!mounted) return;
      setState(() {
        _history.add({'question': question, 'answer': answer});
        if (feedback.isNotEmpty) {
          _messages.add(
            _ChatMessage(feedback, isUser: false, isFeedback: true),
          );
        }
        if (nextQuestion.isNotEmpty) {
          _currentQuestion = nextQuestion;
          _messages.add(_ChatMessage(nextQuestion, isUser: false));
        }
        _busy = false;
      });
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _messages.add(
          _ChatMessage(Api.errorMessage(e), isUser: false, isFeedback: true),
        );
      });
      _scrollToBottom();
    }
  }

  /// 404 'Session not found' -> drop back to the role picker.
  void _sessionExpired() {
    if (!mounted) return;
    setState(() {
      _sessionId = null;
      _messages.clear();
      _history.clear();
      _currentQuestion = '';
      _evaluation = {};
      _phase = _Phase.pick;
      _busy = false;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'This interview session has expired. Please start a new one.',
        ),
      ),
    );
  }

  Future<void> _finish() async {
    if (_sessionId == null || _busy) return;
    setState(() {
      _busy = true;
      _phase = _Phase.evaluating;
    });
    try {
      final res = await Api.instance.dio.post(
        '/api/mock-interview/finish/$_sessionId',
      );
      if (res.statusCode == 404 ||
          (res.data is Map &&
              (res.data['detail'] ?? '').toString().contains(
                'Session not found',
              ))) {
        _sessionExpired();
        return;
      }
      if (res.statusCode != 200) {
        _setError(_messageFrom(res) ?? 'Could not load the evaluation.');
        return;
      }
      if (!mounted) return;
      setState(() {
        _evaluation = res.data is Map
            ? Map<String, dynamic>.from(res.data as Map)
            : {'result': res.data?.toString() ?? ''};
        _busy = false;
        _phase = _Phase.done;
      });
    } catch (e) {
      _setError(Api.errorMessage(e));
      if (mounted) setState(() => _busy = false);
    }
  }

  void _restart() {
    setState(() {
      _sessionId = null;
      _messages.clear();
      _history.clear();
      _currentQuestion = '';
      _evaluation = {};
      _answerCtrl.clear();
      _phase = _Phase.pick;
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollCtrl.hasClients) return;
      _scrollCtrl.animateTo(
        _scrollCtrl.position.maxScrollExtent,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  String? _messageFrom(Response res) {
    final data = res.data;
    if (data is Map) {
      final detail = data['detail'] ?? data['message'];
      if (detail != null && detail.toString().isNotEmpty) {
        return detail.toString();
      }
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Mock Interview'),
        actions: [
          if (_phase == _Phase.chatting)
            IconButton(
              tooltip: 'Finish & see evaluation',
              icon: const Icon(Icons.flag_outlined),
              onPressed: _busy ? null : _finish,
            ),
        ],
      ),
      body: switch (_phase) {
        _Phase.loadingRoles => const Center(child: CircularProgressIndicator()),
        _Phase.pick => _buildPicker(),
        _Phase.chatting => _buildChat(),
        _Phase.evaluating => const Center(child: CircularProgressIndicator()),
        _Phase.done => _buildEvaluation(),
      },
    );
  }

  Widget _buildPicker() {
    if (_roles.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.forum_outlined, size: 48),
              const SizedBox(height: 12),
              const Text('No interview roles available.'),
              const SizedBox(height: 16),
              FilledButton.tonal(
                onPressed: _loadRoles,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.record_voice_over_outlined, size: 56),
            const SizedBox(height: 12),
            Text(
              'Practice with an AI interviewer',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 4),
            Text(
              'Answer questions about your target role and get instant feedback.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 24),
            DropdownButtonFormField<String>(
              initialValue: _selectedRole,
              decoration: const InputDecoration(
                labelText: 'Interview role',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.work_outline),
              ),
              items: _roles
                  .map((r) => DropdownMenuItem(value: r, child: Text(r)))
                  .toList(),
              onChanged: (v) => setState(() => _selectedRole = v),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: _busy ? null : _startSession,
              icon: _busy
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.play_arrow_rounded),
              label: const Text('Start interview'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChat() {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            controller: _scrollCtrl,
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length,
            itemBuilder: (context, i) => _buildBubble(context, _messages[i]),
          ),
        ),
        SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: TextField(
                    controller: _answerCtrl,
                    minLines: 1,
                    maxLines: 5,
                    textInputAction: TextInputAction.newline,
                    enabled: !_busy,
                    decoration: const InputDecoration(
                      hintText: 'Type your answer…',
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _busy ? null : _sendAnswer,
                  icon: const Icon(Icons.send_rounded),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildBubble(BuildContext context, _ChatMessage msg) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final alignRight = msg.isUser;

    final bubble = Container(
      margin: EdgeInsets.only(
        left: alignRight ? 56 : 0,
        right: alignRight ? 0 : 56,
        bottom: 12,
      ),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: msg.isFeedback
            ? colorScheme.secondaryContainer
            : alignRight
            ? colorScheme.primaryContainer
            : colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(16),
          topRight: const Radius.circular(16),
          bottomLeft: Radius.circular(alignRight ? 16 : 4),
          bottomRight: Radius.circular(alignRight ? 4 : 16),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (msg.isFeedback)
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.insights,
                    size: 14,
                    color: colorScheme.onSecondaryContainer,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'Feedback',
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: colorScheme.onSecondaryContainer,
                    ),
                  ),
                ],
              ),
            ),
          SelectableText(
            msg.text,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: msg.isFeedback
                  ? colorScheme.onSecondaryContainer
                  : alignRight
                  ? colorScheme.onPrimaryContainer
                  : colorScheme.onSurface,
            ),
          ),
        ],
      ),
    );

    return Align(
      alignment: alignRight ? Alignment.centerRight : Alignment.centerLeft,
      child: bubble,
    );
  }

  Widget _buildEvaluation() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Row(
          children: [
            const Icon(Icons.assessment_outlined),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                'Interview evaluation',
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (_evaluation.isEmpty)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('No evaluation was returned.'),
            ),
          )
        else ...[
          if (_evaluation['overall_score'] != null)
            _ScoreHeader(score: _evaluation['overall_score']),
          const SizedBox(height: 8),
          Card(
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                for (final entry in _evaluation.entries)
                  if (entry.key != 'overall_score')
                    _EvalRow(label: _humanize(entry.key), value: entry.value),
              ],
            ),
          ),
        ],
        const SizedBox(height: 24),
        FilledButton.icon(
          onPressed: _restart,
          icon: const Icon(Icons.refresh),
          label: const Text('Start over'),
        ),
        const SizedBox(height: 16),
      ],
    );
  }
}

/// Big overall score badge shown above the evaluation details.
class _ScoreHeader extends StatelessWidget {
  final dynamic score;
  const _ScoreHeader({required this.score});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Text(
              score.toString(),
              style: theme.textTheme.displaySmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Overall score',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// One row of the evaluation object. Values are rendered gracefully:
/// strings inline, lists as bullet lines, maps as indented JSON.
class _EvalRow extends StatelessWidget {
  static const double _indentWidth = 3.0;

  final String label;
  final dynamic value;
  const _EvalRow({required this.label, required this.value});

  String _formatValue(dynamic v) {
    if (v == null) return '—';
    if (v is List) {
      return v.map((e) => '• ${_formatValue(e)}').join('\n');
    }
    if (v is Map) {
      return const JsonEncoder.withIndent('  ').convert(v);
    }
    return v.toString();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: BoxDecoration(
        border: Border(
          left: BorderSide(
            color: theme.colorScheme.outlineVariant,
            width: _indentWidth,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 4),
          SelectableText(
            _formatValue(value),
            style: theme.textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

String _humanize(String key) {
  final cleaned = key.replaceAll('_', ' ').trim();
  if (cleaned.isEmpty) return key;
  return cleaned[0].toUpperCase() + cleaned.substring(1);
}
