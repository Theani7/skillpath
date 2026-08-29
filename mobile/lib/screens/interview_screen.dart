import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../services/api_client.dart';
import '../theme.dart';

class _ChatMessage {
  final String text;
  final bool isUser;
  final bool isFeedback;
  const _ChatMessage(this.text, {required this.isUser, this.isFeedback = false});
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
      final roles = (res.data['roles'] as List? ?? []).map((e) => e.toString()).toList();
      if (!mounted) return;
      setState(() {
        _roles = roles;
        _selectedRole = roles.isNotEmpty ? roles.first : null;
        _phase = _Phase.pick;
      });
      if (roles.isEmpty) return;
      try {
        final la = await Api.instance.dio.get('/api/user/latest-analysis');
        if (la.statusCode == 200 && la.data is Map) {
          final target = la.data['target_role']?.toString();
          if (target != null && roles.contains(target) && mounted) setState(() => _selectedRole = target);
        }
      } catch (_) {}
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
      final res = await Api.instance.dio.post('/api/mock-interview/start', data: {'role': role});
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
      final res = await Api.instance.dio.post('/api/mock-interview/answer', data: {
        'session_id': _sessionId,
        'question': question,
        'answer': answer,
        'role': _selectedRole,
        'chat_history': _history,
      });
      if (res.statusCode == 404 || (res.data is Map && (res.data['detail'] ?? '').toString().contains('Session not found'))) {
        _sessionExpired();
        return;
      }
      if (res.statusCode != 200 || res.data is! Map) {
        if (!mounted) return;
        setState(() {
          _busy = false;
          _messages.add(_ChatMessage(_messageFrom(res) ?? 'Failed to send answer.', isUser: false, isFeedback: true));
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
        if (feedback.isNotEmpty) _messages.add(_ChatMessage(feedback, isUser: false, isFeedback: true));
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
        _messages.add(_ChatMessage(Api.errorMessage(e), isUser: false, isFeedback: true));
      });
      _scrollToBottom();
    }
  }

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
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('This interview session has expired. Please start a new one.')));
  }

  Future<void> _finish() async {
    if (_sessionId == null || _busy) return;
    setState(() {
      _busy = true;
      _phase = _Phase.evaluating;
    });
    try {
      final res = await Api.instance.dio.post('/api/mock-interview/finish/$_sessionId');
      if (res.statusCode == 404 || (res.data is Map && (res.data['detail'] ?? '').toString().contains('Session not found'))) {
        _sessionExpired();
        return;
      }
      if (res.statusCode != 200) {
        _setError(_messageFrom(res) ?? 'Could not load the evaluation.');
        return;
      }
      if (!mounted) return;
      setState(() {
        _evaluation = res.data is Map ? Map<String, dynamic>.from(res.data as Map) : {'result': res.data?.toString() ?? ''};
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
      _scrollCtrl.animateTo(_scrollCtrl.position.maxScrollExtent, duration: const Duration(milliseconds: 250), curve: Curves.easeOut);
    });
  }

  String? _messageFrom(Response res) {
    final data = res.data;
    if (data is Map) {
      final detail = data['detail'] ?? data['message'];
      if (detail != null && detail.toString().isNotEmpty) return detail.toString();
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          Positioned(top: -120, right: -100, child: Container(width: 360, height: 360, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.primary.withValues(alpha: 0.06), Colors.transparent])))),
          Positioned(bottom: -140, left: -140, child: Container(width: 380, height: 380, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.secondary.withValues(alpha: 0.05), Colors.transparent])))),
          SafeArea(
            child: switch (_phase) {
              _Phase.loadingRoles => const Center(child: SizedBox(height: 28, width: 28, child: CircularProgressIndicator(strokeWidth: 2.5, color: T.secondary))),
              _Phase.pick => _buildPicker(),
              _Phase.chatting => _buildChat(),
              _Phase.evaluating => const Center(child: Column(mainAxisSize: MainAxisSize.min, children: [SizedBox(height: 32, width: 32, child: CircularProgressIndicator(strokeWidth: 3, color: T.secondary)), SizedBox(height: 12), Text('Evaluating your interview…', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: T.textMuted))])),
              _Phase.done => _buildEvaluation(),
            },
          ),
        ],
      ),
    );
  }

  Widget _buildPicker() {
    if (_roles.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 400),
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
            decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Container(height: 48, width: 48, decoration: const BoxDecoration(color: T.errorLight, shape: BoxShape.circle), child: const Icon(Icons.forum_outlined, color: T.error)),
              const SizedBox(height: 12),
              const Text('No interview roles available.', style: TextStyle(fontWeight: FontWeight.w700, color: T.text)),
              const SizedBox(height: 16),
              FilledButton.tonalIcon(onPressed: _loadRoles, icon: const Icon(Icons.refresh, size: 18), label: const Text('Retry')),
            ]),
          ),
        ),
      );
    }
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520),
          child: Column(
            children: [
              Container(
                height: 64, width: 64,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(18), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                child: ClipRRect(borderRadius: BorderRadius.circular(10), child: Image.asset('assets/icon.png', fit: BoxFit.contain)),
              ),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                decoration: BoxDecoration(color: T.navy100.withValues(alpha: 0.6), borderRadius: BorderRadius.circular(100), border: Border.all(color: T.navy100)),
                child: const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.record_voice_over, size: 11, color: T.primary), SizedBox(width: 6), Text('AI MOCK INTERVIEW • PRACTICE', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.08 * 11, color: T.primary))]),
              ),
              const SizedBox(height: 12),
              Text('Practice with an AI interviewer', textAlign: TextAlign.center, style: displayStyle(context, 26)),
              const SizedBox(height: 8),
              const Text('Answer role-specific questions and get instant, actionable feedback.', textAlign: TextAlign.center, style: TextStyle(fontSize: 14, height: 1.55, color: T.textMuted)),
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
                decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text('Interview role', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      initialValue: _selectedRole,
                      decoration: const InputDecoration(prefixIcon: Icon(Icons.work_outline, size: 18, color: T.textLight)),
                      items: _roles.map((r) => DropdownMenuItem(value: r, child: Text(r, overflow: TextOverflow.ellipsis))).toList(),
                      onChanged: (v) => setState(() => _selectedRole = v),
                      borderRadius: BorderRadius.circular(T.radiusLg),
                      isExpanded: true,
                    ),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      onPressed: _busy ? null : _startSession,
                      icon: _busy ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.play_arrow_rounded, color: Colors.white),
                      label: const Text('Start interview', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                      style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48), backgroundColor: T.primary, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg))),
                    ),
                    const SizedBox(height: 10),
                    const Row(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.bolt, size: 11, color: T.textLight), SizedBox(width: 4), Text('3–5 questions • instant feedback • private', style: TextStyle(fontSize: 11, color: T.textLight, fontWeight: FontWeight.w600))]),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChat() {
    return Column(
      children: [
        // header bar
        Container(
          margin: const EdgeInsets.fromLTRB(16, 6, 16, 8),
          padding: const EdgeInsets.fromLTRB(12, 8, 8, 8),
          decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
          child: Row(
            children: [
              Container(height: 32, width: 32, decoration: BoxDecoration(color: const Color(0xFFFFEDD5), borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.record_voice_over, size: 16, color: T.secondaryDark)),
              const SizedBox(width: 10),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(_selectedRole ?? 'Interview', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: T.text)),
                  Row(children: [Container(height: 6, width: 6, decoration: const BoxDecoration(color: T.success, shape: BoxShape.circle)), const SizedBox(width: 4), Text('${_history.length + 1} • Live session', style: const TextStyle(fontSize: 11, color: T.textMuted, fontWeight: FontWeight.w600))]),
                ]),
              ),
              TextButton.icon(onPressed: _busy ? null : _finish, icon: const Icon(Icons.flag_outlined, size: 16), label: const Text('Finish'), style: TextButton.styleFrom(foregroundColor: T.primary, padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6), backgroundColor: T.navy100.withValues(alpha: 0.6), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)))),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            controller: _scrollCtrl,
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 12),
            itemCount: _messages.length + (_busy && _messages.isNotEmpty && _messages.last.isUser ? 1 : 0),
            itemBuilder: (context, i) {
              if (i == _messages.length) {
                return Align(
                  alignment: Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 12, right: 56),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(color: T.surface, borderRadius: const BorderRadius.only(topLeft: Radius.circular(16), topRight: Radius.circular(16), bottomRight: Radius.circular(16), bottomLeft: Radius.circular(4)), border: Border.all(color: T.borderLight)),
                    child: const Row(mainAxisSize: MainAxisSize.min, children: [SizedBox(height: 12, width: 12, child: CircularProgressIndicator(strokeWidth: 2, color: T.secondary)), SizedBox(width: 8), Text('Thinking…', style: TextStyle(fontSize: 12.5, color: T.textMuted, fontWeight: FontWeight.w600))]),
                  ),
                );
              }
              return _buildBubble(context, _messages[i]);
            },
          ),
        ),
        Container(
          padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
          decoration: BoxDecoration(color: T.surface, border: Border(top: BorderSide(color: T.borderLight))),
          child: SafeArea(
            top: false,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(color: T.bg, borderRadius: BorderRadius.circular(14), border: Border.all(color: T.border)),
                    child: TextField(
                      controller: _answerCtrl,
                      minLines: 1,
                      maxLines: 5,
                      textInputAction: TextInputAction.newline,
                      enabled: !_busy,
                      decoration: const InputDecoration(hintText: 'Type your answer…', border: InputBorder.none, contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 12), isDense: true),
                      onSubmitted: (_) => _sendAnswer(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                SizedBox(
                  height: 44, width: 44,
                  child: FilledButton(
                    onPressed: _busy ? null : _sendAnswer,
                    style: FilledButton.styleFrom(backgroundColor: T.secondary, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)), padding: EdgeInsets.zero, minimumSize: const Size(44, 44)),
                    child: const Icon(Icons.send_rounded, size: 18, color: Colors.white),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildBubble(BuildContext context, _ChatMessage msg) {
    final alignRight = msg.isUser;
    if (msg.isFeedback) {
      return Align(
        alignment: Alignment.centerLeft,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12, right: 32),
          padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
          decoration: BoxDecoration(color: const Color(0xFFFFEDD5), borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFFFFD7B8))),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.lightbulb_outline, size: 13, color: T.secondaryDark), SizedBox(width: 4), Text('Feedback', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.06 * 11, color: T.secondaryDark))]),
              const SizedBox(height: 4),
              SelectableText(msg.text, style: const TextStyle(fontSize: 13, height: 1.5, color: Color(0xFF7C2D12))),
            ],
          ),
        ),
      );
    }
    return Align(
      alignment: alignRight ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.only(left: alignRight ? 40 : 0, right: alignRight ? 0 : 40, bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: alignRight ? T.primary : T.surface,
          borderRadius: BorderRadius.only(topLeft: const Radius.circular(16), topRight: const Radius.circular(16), bottomLeft: Radius.circular(alignRight ? 16 : 4), bottomRight: Radius.circular(alignRight ? 4 : 16)),
          border: alignRight ? null : Border.all(color: T.borderLight),
          boxShadow: alignRight ? [] : T.cardShadow,
        ),
        child: SelectableText(msg.text, style: TextStyle(fontSize: 13.5, height: 1.5, color: alignRight ? Colors.white : T.text)),
      ),
    );
  }

  Widget _buildEvaluation() {
    final hasScore = _evaluation['overall_score'] != null;
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      children: [
        Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
            decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(100), border: Border.all(color: const Color(0xFFBBF7D0))),
            child: const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.verified, size: 11, color: T.success), SizedBox(width: 6), Text('EVALUATION READY', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.08 * 11, color: Color(0xFF166534)))]),
          ),
        ),
        const SizedBox(height: 12),
        Text('Your Interview Report', textAlign: TextAlign.center, style: displayStyle(context, 24)),
        const SizedBox(height: 6),
        Text(_selectedRole ?? 'General', textAlign: TextAlign.center, style: const TextStyle(fontSize: 13, color: T.textMuted, fontWeight: FontWeight.w600)),
        const SizedBox(height: 16),
        if (_evaluation.isEmpty)
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight)),
            child: const Text('No evaluation was returned.', style: TextStyle(color: T.textMuted)),
          )
        else ...[
          if (hasScore)
            Container(
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [T.primary, Color(0xFF1A2D4A)], begin: Alignment.topLeft, end: Alignment.bottomRight),
                borderRadius: BorderRadius.circular(T.radiusXl),
                boxShadow: T.cardShadow,
              ),
              child: Row(
                children: [
                  Container(
                    height: 72, width: 72,
                    decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.12), shape: BoxShape.circle, border: Border.all(color: Colors.white.withValues(alpha: 0.2))),
                    child: Center(child: Text(_evaluation['overall_score'].toString(), style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w800, color: Colors.white))),
                  ),
                  const SizedBox(width: 16),
                  const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Overall Score', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white70)), SizedBox(height: 4), Text('Based on your answers and feedback', style: TextStyle(fontSize: 12.5, color: Colors.white60, height: 1.3))])),
                ],
              ),
            ),
          if (hasScore) const SizedBox(height: 12),
          Container(
            clipBehavior: Clip.antiAlias,
            decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
            child: Column(
              children: [
                for (final entry in _evaluation.entries)
                  if (entry.key != 'overall_score') _EvalRow(label: _humanize(entry.key), value: entry.value),
              ],
            ),
          ),
        ],
        const SizedBox(height: 20),
        FilledButton.icon(onPressed: _restart, icon: const Icon(Icons.refresh, size: 18, color: Colors.white), label: const Text('Start new interview', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)), style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48), backgroundColor: T.primary)),
        const SizedBox(height: 10),
        OutlinedButton.icon(onPressed: () => setState(() => _phase = _Phase.pick), icon: const Icon(Icons.tune, size: 16), label: const Text('Change role')),
      ],
    );
  }
}

class _EvalRow extends StatelessWidget {
  final String label;
  final dynamic value;
  const _EvalRow({required this.label, required this.value});
  String _formatValue(dynamic v) {
    if (v == null) return '—';
    if (v is List) return v.map((e) => '• ${_formatValue(e)}').join('\n');
    if (v is Map) return const JsonEncoder.withIndent('  ').convert(v);
    return v.toString();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: BoxDecoration(border: Border(top: BorderSide(color: T.borderLight))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(height: 6, width: 6, decoration: const BoxDecoration(color: T.secondary, shape: BoxShape.circle)),
            const SizedBox(width: 6),
            Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 0.04 * 12, color: T.primary)),
          ]),
          const SizedBox(height: 6),
          SelectableText(_formatValue(value), style: const TextStyle(fontSize: 13, height: 1.5, color: T.text)),
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
