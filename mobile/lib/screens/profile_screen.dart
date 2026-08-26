import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../state/session.dart';

/// Profile: account header, analysis history, security, data & support.
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

  // ---------------------------------------------------------------- helpers

  void _snack(String message, {bool error = false, SnackBarAction? action}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          behavior: SnackBarBehavior.floating,
          backgroundColor: error ? Theme.of(context).colorScheme.error : null,
          action: action,
        ),
      );
  }

  /// Extract a human-readable message from an error or a non-2xx response
  /// (dio is configured with validateStatus < 500, so 4xx does not throw).
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
    final months = const [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return '${months[d.month - 1]} ${d.day}, ${d.year}';
  }

  String _fmtScore(dynamic raw) {
    final n = raw is num ? raw.toDouble() : double.tryParse('$raw');
    if (n == null) return '$raw';
    return n % 1 == 0 ? n.toStringAsFixed(0) : n.toStringAsFixed(1);
  }

  // ---------------------------------------------------------------- history

  Future<void> _loadHistory() async {
    setState(() => _historyLoading = true);
    try {
      final res = await Api.instance.dio.get('/api/user/history');
      if (res.statusCode == 200) {
        final items = (res.data as Map)['history'];
        setState(() {
          _history = (items as List? ?? [])
              .whereType<Map>()
              .map((m) => m.cast<String, dynamic>())
              .toList();
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
        content: const Text(
          'This permanently removes every analysis from your history.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(ctx).colorScheme.error,
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Clear All'),
          ),
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

  // ---------------------------------------------------------- change password

  Future<void> _changePassword() async {
    if (!_pwFormKey.currentState!.validate()) return;
    FocusScope.of(context).unfocus();
    setState(() => _changingPw = true);
    final err = await AuthService.changePassword(
      _currentPwCtrl.text,
      _newPwCtrl.text,
    );
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

  // ------------------------------------------------------------------ export

  Future<void> _exportData() async {
    setState(() => _exporting = true);
    try {
      final res = await Api.instance.dio.get('/api/user/export');
      if (res.statusCode == 200) {
        final data = res.data;
        final jsonText = data is String ? data : jsonEncode(data ?? {});
        final bytes = utf8.encode(jsonText).length;
        _snack(
          'Your data export is ready ($bytes bytes)',
          action: SnackBarAction(
            label: 'Copy JSON',
            onPressed: () async {
              await Clipboard.setData(ClipboardData(text: jsonText));
              _snack('Copied to clipboard');
            },
          ),
        );
      } else {
        _snack(_messageOf(res), error: true);
      }
    } catch (e) {
      _snack(Api.errorMessage(e), error: true);
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  // ----------------------------------------------------------- delete account

  Future<void> _deleteAccountFlow(Session session) async {
    final pwdCtrl = TextEditingController();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete your account?'),
        content: TextFormField(
          controller: pwdCtrl,
          obscureText: true,
          autofillHints: const [AutofillHints.password],
          decoration: const InputDecoration(
            labelText: 'Confirm your password',
            prefixIcon: Icon(Icons.lock_outline),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(ctx).colorScheme.error,
            ),
            onPressed: () =>
                pwdCtrl.text.isEmpty ? null : Navigator.pop(ctx, true),
            child: const Text('Delete Account'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    setState(() => _deletingAccount = true);
    try {
      final res = await Api.instance.dio.delete(
        '/api/user/account',
        data: {'password': pwdCtrl.text},
      );
      if (res.statusCode != null && res.statusCode! < 300) {
        await session.logout(); // router redirects to /login
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

  // -------------------------------------------------------------------- build

  @override
  Widget build(BuildContext context) {
    final session = context.watch<Session>();
    final user = session.user;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: RefreshIndicator(
        onRefresh: _loadHistory,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
          children: [
            _accountCard(theme, user, session),
            const SizedBox(height: 16),
            _historyCard(theme),
            const SizedBox(height: 16),
            _securityCard(theme),
            const SizedBox(height: 16),
            _dataCard(theme, session),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(ThemeData theme, String text, {Widget? action}) =>
      Padding(
        padding: const EdgeInsets.only(left: 4, bottom: 8, top: 4),
        child: Row(
          children: [
            Expanded(child: Text(text, style: theme.textTheme.titleMedium)),
            ?action,
          ],
        ),
      );

  Widget _accountCard(ThemeData theme, dynamic user, Session session) {
    final name = user?.fullName as String? ?? '';
    final username = user?.username as String? ?? '';
    final role = user?.role as String? ?? '';
    final initial = name.isNotEmpty
        ? name[0].toUpperCase()
        : (username.isNotEmpty ? username[0].toUpperCase() : '?');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle(theme, 'Account'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  child: Text(
                    initial,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: theme.textTheme.titleLarge,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '@$username',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Chip(
                        label: Text(role),
                        labelStyle: theme.textTheme.labelSmall,
                        visualDensity: VisualDensity.compact,
                        padding: EdgeInsets.zero,
                      ),
                    ],
                  ),
                ),
                IconButton(
                  tooltip: 'Log out',
                  icon: const Icon(Icons.logout),
                  onPressed: () => session.logout(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _historyCard(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle(
          theme,
          'Analysis History',
          action: _history.isEmpty
              ? null
              : TextButton(
                  onPressed: _clearingAll ? null : _clearAll,
                  child: _clearingAll
                      ? const SizedBox(
                          width: 14,
                          height: 14,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Clear All'),
                ),
        ),
        Card(
          clipBehavior: Clip.antiAlias,
          child: _historyLoading
              ? const Padding(
                  padding: EdgeInsets.all(32),
                  child: Center(child: CircularProgressIndicator()),
                )
              : _history.isEmpty
              ? Padding(
                  padding: const EdgeInsets.all(24),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(
                          Icons.history,
                          size: 36,
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'No analyses yet.\nUpload a resume from Home.',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              : Column(
                  children: [
                    for (var i = 0; i < _history.length; i++) ...[
                      if (i > 0) const Divider(height: 1, indent: 56),
                      _historyTile(_history[i]),
                    ],
                  ],
                ),
        ),
      ],
    );
  }

  Widget _historyTile(Map<String, dynamic> item) {
    return Dismissible(
      key: ValueKey(item['id']),
      direction: DismissDirection.endToStart,
      background: Container(
        color: Theme.of(context).colorScheme.errorContainer,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: Icon(
          Icons.delete_outline,
          color: Theme.of(context).colorScheme.onErrorContainer,
        ),
      ),
      confirmDismiss: (_) async =>
          await showDialog<bool>(
            context: context,
            builder: (ctx) => AlertDialog(
              title: const Text('Delete this analysis?'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: Theme.of(ctx).colorScheme.error,
                  ),
                  onPressed: () => Navigator.pop(ctx, true),
                  child: const Text('Delete'),
                ),
              ],
            ),
          ) ==
          true,
      onDismissed: (_) => _deleteAnalysis(item),
      child: ListTile(
        leading: const Icon(Icons.picture_as_pdf_outlined),
        title: Text(
          (item['pdf_name'] ?? 'Resume').toString(),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          '${_fmtDate(item['Timestamp'])}'
          '${item['target_role'] != null ? '  ·  ${item['target_role']}' : ''}',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: Theme.of(
                  context,
                ).colorScheme.primaryContainer.withValues(alpha: 0.7),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                _fmtScore(item['resume_score']),
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
              ),
            ),
            IconButton(
              tooltip: 'Delete',
              icon: const Icon(Icons.delete_outline),
              onPressed: () async {
                final ok = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Delete this analysis?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        child: const Text('Cancel'),
                      ),
                      FilledButton(
                        style: FilledButton.styleFrom(
                          backgroundColor: Theme.of(ctx).colorScheme.error,
                        ),
                        onPressed: () => Navigator.pop(ctx, true),
                        child: const Text('Delete'),
                      ),
                    ],
                  ),
                );
                if (ok == true) _deleteAnalysis(item);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _securityCard(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle(theme, 'Security'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _pwFormKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextFormField(
                    controller: _currentPwCtrl,
                    obscureText: true,
                    autofillHints: const [AutofillHints.password],
                    decoration: const InputDecoration(
                      labelText: 'Current password',
                      prefixIcon: Icon(Icons.lock_outline),
                    ),
                    validator: (v) => (v == null || v.isEmpty)
                        ? 'Enter your current password'
                        : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _newPwCtrl,
                    obscureText: true,
                    autofillHints: const [AutofillHints.newPassword],
                    decoration: const InputDecoration(
                      labelText: 'New password',
                      helperText: 'At least 8 characters',
                      prefixIcon: Icon(Icons.password_outlined),
                    ),
                    validator: (v) => (v == null || v.length < 8)
                        ? 'New password must be at least 8 characters'
                        : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _confirmPwCtrl,
                    obscureText: true,
                    autofillHints: const [AutofillHints.newPassword],
                    decoration: const InputDecoration(
                      labelText: 'Confirm new password',
                      prefixIcon: Icon(Icons.repeat),
                    ),
                    validator: (v) =>
                        v != _newPwCtrl.text ? 'Passwords do not match' : null,
                  ),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: _changingPw ? null : _changePassword,
                    icon: _changingPw
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.check_circle_outline),
                    label: const Text('Change Password'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _dataCard(ThemeData theme, Session session) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle(theme, 'Data & Support'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                OutlinedButton.icon(
                  onPressed: _exporting ? null : _exportData,
                  icon: _exporting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.download_outlined),
                  label: const Text('Export My Data'),
                ),
                const Divider(height: 32),
                Text(
                  'Danger Zone',
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: theme.colorScheme.error,
                  ),
                ),
                const SizedBox(height: 8),
                FilledButton.icon(
                  style: FilledButton.styleFrom(
                    backgroundColor: theme.colorScheme.error,
                    foregroundColor: theme.colorScheme.onError,
                  ),
                  onPressed: _deletingAccount
                      ? null
                      : () => _deleteAccountFlow(session),
                  icon: _deletingAccount
                      ? SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: theme.colorScheme.onError,
                          ),
                        )
                      : const Icon(Icons.person_remove_outlined),
                  label: const Text('Delete Account'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
