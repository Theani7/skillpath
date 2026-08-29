import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../state/session.dart';
import '../theme.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _pwFormKey = GlobalKey<FormState>();
  final _currentPwCtrl = TextEditingController();
  final _newPwCtrl = TextEditingController();
  final _confirmPwCtrl = TextEditingController();

  bool _changingPw = false;
  bool _showPw = false;
  bool _exporting = false;
  bool _deletingAccount = false;
  bool _clearingAll = false;

  List<Map<String, dynamic>> _history = [];
  bool _historyLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  @override
  void dispose() {
    _currentPwCtrl.dispose();
    _newPwCtrl.dispose();
    _confirmPwCtrl.dispose();
    super.dispose();
  }

  void _snack(String message, {bool error = false, SnackBarAction? action}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message), behavior: SnackBarBehavior.floating, backgroundColor: error ? T.error : T.primary, action: action));
  }

  String _messageOf(Object errorOrResponse) {
    if (errorOrResponse is Response) {
      final data = errorOrResponse.data;
      if (data is Map) {
        final detail = data['detail'];
        if (detail is String && detail.isNotEmpty) return detail;
      }
    }
    return Api.errorMessage(errorOrResponse);
  }

  String _fmtDate(dynamic ts) {
    final s = ts?.toString();
    final d = s == null ? null : DateTime.tryParse(s);
    if (d == null) return s ?? '';
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${months[d.month - 1]} ${d.day}, ${d.year}';
  }

  String _fmtScore(dynamic raw) {
    final n = raw is num ? raw.toDouble() : double.tryParse('$raw');
    if (n == null) return '$raw';
    return n % 1 == 0 ? n.toStringAsFixed(0) : n.toStringAsFixed(1);
  }

  Future<void> _loadHistory() async {
    setState(() => _historyLoading = true);
    try {
      final res = await Api.instance.dio.get('/api/user/history');
      if (res.statusCode == 200) {
        final items = (res.data as Map)['history'];
        setState(() {
          _history = (items as List? ?? []).whereType<Map>().map((m) => m.cast<String, dynamic>()).toList();
          _historyLoading = false;
        });
      } else {
        setState(() => _historyLoading = false);
        _snack(_messageOf(res), error: true);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _historyLoading = false);
      _snack(Api.errorMessage(e), error: true);
    }
  }

  Future<void> _deleteAnalysis(Map<String, dynamic> item) async {
    final id = item['id'];
    try {
      final res = await Api.instance.dio.delete('/api/user/analysis/$id');
      if (res.statusCode != null && res.statusCode! < 300) {
        setState(() => _history.removeWhere((e) => e['id'] == id));
        _snack('Analysis deleted');
      } else {
        _snack(_messageOf(res), error: true);
      }
    } catch (e) {
      _snack(Api.errorMessage(e), error: true);
    }
  }

  Future<void> _clearAll() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Clear all analyses?'),
        content: const Text('This permanently removes every analysis from your history.'),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusXl)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(style: FilledButton.styleFrom(backgroundColor: T.error), onPressed: () => Navigator.pop(ctx, true), child: const Text('Clear All')),
        ],
      ),
    );
    if (confirmed != true) return;
    setState(() => _clearingAll = true);
    try {
      final res = await Api.instance.dio.delete('/api/user/history');
      if (res.statusCode != null && res.statusCode! < 300) {
        setState(() => _history.clear());
        _snack('History cleared');
      } else {
        _snack(_messageOf(res), error: true);
      }
    } catch (e) {
      _snack(Api.errorMessage(e), error: true);
    } finally {
      if (mounted) setState(() => _clearingAll = false);
    }
  }

  Future<void> _changePassword() async {
    if (!_pwFormKey.currentState!.validate()) return;
    FocusScope.of(context).unfocus();
    setState(() => _changingPw = true);
    final err = await AuthService.changePassword(_currentPwCtrl.text, _newPwCtrl.text);
    if (!mounted) return;
    setState(() => _changingPw = false);
    if (err != null) {
      _snack(err, error: true);
    } else {
      _currentPwCtrl.clear();
      _newPwCtrl.clear();
      _confirmPwCtrl.clear();
      _snack('Password updated');
    }
  }

  Future<void> _exportData() async {
    setState(() => _exporting = true);
    try {
      final res = await Api.instance.dio.get('/api/user/export');
      if (res.statusCode == 200) {
        final data = res.data;
        final jsonText = data is String ? data : jsonEncode(data ?? {});
        final bytes = utf8.encode(jsonText).length;
        _snack('Your data export is ready ($bytes bytes)', action: SnackBarAction(label: 'Copy JSON', textColor: Colors.white, onPressed: () async {
          await Clipboard.setData(ClipboardData(text: jsonText));
          _snack('Copied to clipboard');
        }));
      } else {
        _snack(_messageOf(res), error: true);
      }
    } catch (e) {
      _snack(Api.errorMessage(e), error: true);
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  Future<void> _deleteAccountFlow(Session session) async {
    final pwdCtrl = TextEditingController();
    bool show = false;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(builder: (ctx, setS) => AlertDialog(
            title: const Text('Delete your account?'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('This cannot be undone. Enter your password to confirm.', style: TextStyle(fontSize: 13, color: T.textMuted)),
                const SizedBox(height: 12),
                TextField(
                  controller: pwdCtrl,
                  obscureText: !show,
                  decoration: InputDecoration(
                    labelText: 'Confirm your password',
                    prefixIcon: const Icon(Icons.lock_outline, size: 18, color: T.textLight),
                    suffixIcon: IconButton(icon: Icon(show ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 18), onPressed: () => setS(() => show = !show)),
                  ),
                ),
              ],
            ),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusXl)),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
              FilledButton(style: FilledButton.styleFrom(backgroundColor: T.error), onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete Account')),
            ],
          )),
    );
    pwdCtrl.dispose();
    if (confirmed != true || !mounted) return;
    setState(() => _deletingAccount = true);
    try {
      final res = await Api.instance.dio.delete('/api/user/account', data: {'password': pwdCtrl.text});
      if (res.statusCode != null && res.statusCode! < 300) {
        await session.logout();
      } else if (mounted) {
        setState(() => _deletingAccount = false);
        _snack(_messageOf(res), error: true);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _deletingAccount = false);
        _snack(Api.errorMessage(e), error: true);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final session = context.watch<Session>();
    final user = session.user;

    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          Positioned(top: -120, right: -100, child: Container(width: 360, height: 360, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.primary.withValues(alpha: 0.06), Colors.transparent])))),
          Positioned(bottom: -140, left: -140, child: Container(width: 380, height: 380, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.secondary.withValues(alpha: 0.05), Colors.transparent])))),
          SafeArea(
            child: RefreshIndicator(
              onRefresh: _loadHistory,
              color: T.secondary,
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
                children: [
                  // header
                  Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                      decoration: BoxDecoration(color: T.navy100.withValues(alpha: 0.6), borderRadius: BorderRadius.circular(100), border: Border.all(color: T.navy100)),
                      child: const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.person_outline, size: 11, color: T.primary), SizedBox(width: 6), Text('PROFILE • ACCOUNT', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.08 * 11, color: T.primary))]),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text('Your Profile', textAlign: TextAlign.center, style: displayStyle(context, 26)),
                  const SizedBox(height: 6),
                  const Text('Manage your history, security and data', textAlign: TextAlign.center, style: TextStyle(fontSize: 13, color: T.textMuted, fontWeight: FontWeight.w500)),
                  const SizedBox(height: 18),
                  _accountCard(user, session),
                  const SizedBox(height: 14),
                  _historyCard(),
                  const SizedBox(height: 14),
                  _securityCard(),
                  const SizedBox(height: 14),
                  _dataCard(session),
                  const SizedBox(height: 8),
                  const Text('SkillPath • AI-powered career growth', textAlign: TextAlign.center, style: TextStyle(fontSize: 11, color: T.textLight, letterSpacing: 0.04 * 11)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _accountCard(dynamic user, Session session) {
    final name = (user as dynamic)?.fullName as String? ?? '';
    final username = (user as dynamic)?.username as String? ?? '';
    final role = (user as dynamic)?.role as String? ?? '';
    final initial = name.isNotEmpty ? name[0].toUpperCase() : (username.isNotEmpty ? username[0].toUpperCase() : '?');
    final count = _history.length;
    final avg = count == 0 ? 0 : _history.map((e) => double.tryParse('${e['resume_score']}') ?? 0).reduce((a, b) => a + b) / count;

    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
      decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                height: 56, width: 56,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [T.primary, Color(0xFF1A2D4A)], begin: Alignment.topLeft, end: Alignment.bottomRight),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [BoxShadow(color: T.primary.withValues(alpha: 0.2), blurRadius: 12, offset: const Offset(0, 4))],
                ),
                child: Center(child: Text(initial, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: Colors.white))),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(name.isNotEmpty ? name : username, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: T.text)),
                  const SizedBox(height: 2),
                  Text('@$username', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 6),
                  Row(children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: role == 'admin' ? const Color(0xFFFEF3C7) : T.navy100, borderRadius: BorderRadius.circular(100), border: Border.all(color: role == 'admin' ? const Color(0xFFFCD34D) : T.navy100)),
                      child: Row(mainAxisSize: MainAxisSize.min, children: [Icon(role == 'admin' ? Icons.shield_outlined : Icons.person_outline, size: 11, color: role == 'admin' ? const Color(0xFF92400E) : T.navy900), const SizedBox(width: 4), Text(role.isEmpty ? 'user' : role, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: role == 'admin' ? const Color(0xFF92400E) : T.navy900))]),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: T.successLight, borderRadius: BorderRadius.circular(100), border: Border.all(color: const Color(0xFFBBF7D0))),
                      child: const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.verified, size: 11, color: T.success), SizedBox(width: 4), Text('Verified', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF166534)))]),
                    ),
                  ]),
                ]),
              ),
              IconButton(
                  tooltip: 'Log out',
                  onPressed: () async {
                    final ok = await showDialog<bool>(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Log out?'),
                        content: const Text('Are you sure you want to log out?'),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusXl)),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                          FilledButton(onPressed: () => Navigator.pop(ctx, true), style: FilledButton.styleFrom(backgroundColor: T.primary), child: const Text('Log out', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700))),
                        ],
                      ),
                    );
                    if (ok == true) session.logout();
                  },
                  style: IconButton.styleFrom(backgroundColor: T.bg, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: const BorderSide(color: T.borderLight))),
                  icon: const Icon(Icons.logout, size: 16, color: T.textMuted)),
            ],
          ),
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(color: T.bg, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: T.borderLight)),
            child: Row(
              children: [
                _Stat(label: 'Analyses', value: '$count', icon: Icons.description_outlined),
                Container(width: 1, height: 28, color: T.border, margin: const EdgeInsets.symmetric(horizontal: 12)),
                _Stat(label: 'Avg score', value: count == 0 ? '—' : avg.toStringAsFixed(1), icon: Icons.bar_chart_rounded),
                Container(width: 1, height: 28, color: T.border, margin: const EdgeInsets.symmetric(horizontal: 12)),
                _Stat(label: 'Role', value: role.isEmpty ? 'user' : role, icon: Icons.badge_outlined),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _historyCard() {
    return _Section(
      icon: Icons.history_rounded, iconBg: const Color(0xFFF0F4F8), iconColor: T.primary,
      title: 'Analysis History', subtitle: '${_history.length} saved',
      action: _history.isEmpty ? null : TextButton(onPressed: _clearingAll ? null : _clearAll, style: TextButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6), minimumSize: Size.zero, tapTargetSize: MaterialTapTargetSize.shrinkWrap), child: _clearingAll ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: T.primary)) : const Text('Clear All', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700))),
      child: _historyLoading
          ? const Padding(padding: EdgeInsets.all(28), child: Center(child: SizedBox(height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2.5, color: T.secondary))))
          : _history.isEmpty
              ? Padding(
                  padding: const EdgeInsets.fromLTRB(16, 20, 16, 20),
                  child: Column(children: [
                    Container(height: 44, width: 44, decoration: BoxDecoration(color: T.bg, shape: BoxShape.circle, border: Border.all(color: T.borderLight)), child: const Icon(Icons.history, size: 20, color: T.textLight)),
                    const SizedBox(height: 10),
                    const Text('No analyses yet.', style: TextStyle(fontWeight: FontWeight.w700, color: T.text)),
                    const SizedBox(height: 4),
                    const Text('Upload a resume from Analyze to get started.', textAlign: TextAlign.center, style: TextStyle(fontSize: 12.5, color: T.textMuted)),
                  ]),
                )
              : Column(children: [
                  for (var i = 0; i < _history.length; i++) ...[
                    if (i > 0) const Divider(height: 1, indent: 16, endIndent: 16, color: T.borderLight),
                    _historyTile(_history[i]),
                  ],
                ]),
    );
  }

  Widget _historyTile(Map<String, dynamic> item) {
    final score = _fmtScore(item['resume_score']);
    final n = double.tryParse(score) ?? 0;
    final color = n >= 70 ? T.success : n >= 50 ? const Color(0xFFF59E0B) : T.error;
    return Dismissible(
      key: ValueKey(item['id']),
      direction: DismissDirection.endToStart,
      background: Container(
        decoration: BoxDecoration(color: T.errorLight, borderRadius: BorderRadius.circular(T.radiusLg)),
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 16),
        child: const Icon(Icons.delete_outline, color: T.error),
      ),
      confirmDismiss: (_) async => await showDialog<bool>(context: context, builder: (ctx) => AlertDialog(title: const Text('Delete this analysis?'), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusXl)), actions: [TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')), FilledButton(style: FilledButton.styleFrom(backgroundColor: T.error), onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete'))])) == true,
      onDismissed: (_) => _deleteAnalysis(item),
      child: ListTile(
        contentPadding: const EdgeInsets.fromLTRB(12, 6, 4, 6),
        leading: Container(height: 36, width: 36, decoration: BoxDecoration(color: T.primary.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.picture_as_pdf_outlined, size: 16, color: T.primary)),
        title: Text((item['pdf_name'] ?? 'Resume').toString(), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: T.text)),
        subtitle: Text('${_fmtDate(item['Timestamp'])}${item['target_role'] != null ? ' • ${item['target_role']}' : ''}', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w600)),
        trailing: Row(mainAxisSize: MainAxisSize.min, children: [
          Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5), decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(100), border: Border.all(color: color.withValues(alpha: 0.18))), child: Text(score, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: color))),
          IconButton(tooltip: 'Delete', icon: const Icon(Icons.delete_outline, size: 16, color: T.textLight), onPressed: () async {
            final ok = await showDialog<bool>(context: context, builder: (ctx) => AlertDialog(title: const Text('Delete this analysis?'), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusXl)), actions: [TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')), FilledButton(style: FilledButton.styleFrom(backgroundColor: T.error), onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete'))]));
            if (ok == true) _deleteAnalysis(item);
          }),
        ]),
      ),
    );
  }

  Widget _securityCard() {
    return _Section(
      icon: Icons.lock_outline, iconBg: const Color(0xFFFFEDD5), iconColor: T.secondaryDark,
      title: 'Security', subtitle: 'Change your password',
      child: Form(
        key: _pwFormKey,
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          TextFormField(
            controller: _currentPwCtrl,
            obscureText: !_showPw,
            decoration: InputDecoration(labelText: 'Current password', prefixIcon: const Icon(Icons.lock_outline, size: 18, color: T.textLight), suffixIcon: IconButton(icon: Icon(_showPw ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 18, color: T.textLight), onPressed: () => setState(() => _showPw = !_showPw))),
            validator: (v) => (v == null || v.isEmpty) ? 'Enter your current password' : null,
          ),
          const SizedBox(height: 12),
          TextFormField(
            controller: _newPwCtrl,
            obscureText: !_showPw,
            decoration: const InputDecoration(labelText: 'New password', helperText: 'At least 8 characters', prefixIcon: Icon(Icons.password_outlined, size: 18, color: T.textLight)),
            validator: (v) => (v == null || v.length < 8) ? 'New password must be at least 8 characters' : null,
          ),
          const SizedBox(height: 12),
          TextFormField(
            controller: _confirmPwCtrl,
            obscureText: !_showPw,
            decoration: const InputDecoration(labelText: 'Confirm new password', prefixIcon: Icon(Icons.repeat, size: 18, color: T.textLight)),
            validator: (v) => v != _newPwCtrl.text ? 'Passwords do not match' : null,
          ),
          const SizedBox(height: 14),
          FilledButton.icon(
            onPressed: _changingPw ? null : _changePassword,
            icon: _changingPw ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.check_circle_outline, size: 18, color: Colors.white),
            label: const Text('Change Password', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
            style: FilledButton.styleFrom(backgroundColor: T.primary, minimumSize: const Size.fromHeight(46), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg))),
          ),
        ]),
      ),
    );
  }

  Widget _dataCard(Session session) {
    return _Section(
      icon: Icons.storage_outlined, iconBg: const Color(0xFFEFF6FF), iconColor: Color(0xFF2563EB),
      title: 'Data & Support', subtitle: 'Export or delete your account',
      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        OutlinedButton.icon(onPressed: _exporting ? null : _exportData, icon: _exporting ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: T.primary)) : const Icon(Icons.download_outlined, size: 18), label: const Text('Export My Data'), style: OutlinedButton.styleFrom(minimumSize: const Size.fromHeight(46), side: const BorderSide(color: T.border), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)))),
        const SizedBox(height: 14),
        Container(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 12),
          decoration: BoxDecoration(color: const Color(0xFFFEF2F2), borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: const Color(0xFFFECACA))),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Row(children: [Icon(Icons.warning_amber_rounded, size: 14, color: T.error), SizedBox(width: 6), Text('Danger Zone', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 0.06 * 12, color: T.error))]),
            const SizedBox(height: 8),
            const Text('Permanently delete your account and all data. This cannot be undone.', style: TextStyle(fontSize: 12.5, color: Color(0xFF991B1B), height: 1.4)),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                style: FilledButton.styleFrom(backgroundColor: T.error, foregroundColor: Colors.white, minimumSize: const Size.fromHeight(44), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg))),
                onPressed: _deletingAccount ? null : () => _deleteAccountFlow(session),
                icon: _deletingAccount ? SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.person_remove_outlined, size: 16, color: Colors.white),
                label: const Text('Delete Account', style: TextStyle(fontWeight: FontWeight.w700, color: Colors.white)),
              ),
            ),
          ]),
        ),
      ]),
    );
  }
}

class _Section extends StatelessWidget {
  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String title;
  final String subtitle;
  final Widget? action;
  final Widget child;
  const _Section({required this.icon, required this.iconBg, required this.iconColor, required this.title, required this.subtitle, this.action, required this.child});
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 0),
          child: Row(children: [
            Container(height: 30, width: 30, decoration: BoxDecoration(color: iconBg, borderRadius: BorderRadius.circular(8)), child: Icon(icon, size: 16, color: iconColor)),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w800, color: T.text)), Text(subtitle, style: const TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w500))])),
            if (action != null) action!,
          ]),
        ),
        const SizedBox(height: 12),
        Padding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 16), child: child),
      ]),
    );
  }
}

class _Stat extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  const _Stat({required this.label, required this.value, required this.icon});
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Icon(icon, size: 14, color: T.textLight),
          const SizedBox(height: 2),
          Text(value, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: T.text)),
          Text(label, style: const TextStyle(fontSize: 10.5, color: T.textLight, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
