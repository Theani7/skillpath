import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../router.dart';
import '../services/api_client.dart';
import '../state/session.dart';
import '../theme.dart';

/// Premium floating bottom nav + top bar with notifications bell.
class HomeShell extends StatefulWidget {
  final Widget child;
  const HomeShell({super.key, required this.child});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _notifCount = 0;

  @override
  void initState() {
    super.initState();
    _loadNotifCount();
  }

  Future<void> _loadNotifCount() async {
    try {
      final res = await Api.instance.dio.get('/api/notifications');
      final list = (res.data is Map ? (res.data as Map)['notifications'] : null) as List?;
      final pending = (list ?? []).where((e) => e is Map && (e['status']?.toString() == 'pending')).length;
      if (mounted) setState(() => _notifCount = pending);
    } catch (_) {}
  }

  static const _tabs = [
    (Routes.home, Icons.cloud_upload_outlined, Icons.cloud_upload, 'Analyze'),
    (Routes.result, Icons.insights_outlined, Icons.insights, 'Results'),
    (Routes.interview, Icons.record_voice_over_outlined, Icons.record_voice_over, 'Interview'),
    (Routes.coverLetter, Icons.mail_outline, Icons.mail, 'Cover Letter'),
    (Routes.profile, Icons.person_outline, Icons.person, 'Profile'),
  ];

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.path;
    var index = _tabs.indexWhere((t) => t.$1 == location);
    if (index < 0) index = 0;
    final session = context.watch<Session>();
    final name = session.user?.fullName ?? session.user?.username ?? '';
    final initial = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return Scaffold(
      backgroundColor: T.bg,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(56),
        child: Container(
          decoration: BoxDecoration(color: T.surface, border: Border(bottom: BorderSide(color: T.borderLight)), boxShadow: [BoxShadow(color: T.primary.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 2))]),
          child: SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 12, 8),
              child: Row(
                children: [
                  Container(
                    height: 32, width: 32,
                    padding: const EdgeInsets.all(5),
                    decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(9), border: Border.all(color: T.borderLight)),
                    child: ClipRRect(borderRadius: BorderRadius.circular(5), child: Image.asset('assets/icon.png', fit: BoxFit.contain)),
                  ),
                  const SizedBox(width: 10),
                  Text('SkillPath', style: displayStyle(context, 16).copyWith(fontSize: 16, letterSpacing: -0.02 * 16)),
                  const Spacer(),
                  // bell
                  InkWell(
                    onTap: () async {
                      await context.push(Routes.notifications);
                      _loadNotifCount();
                    },
                    borderRadius: BorderRadius.circular(10),
                    child: Container(
                      height: 36, width: 36,
                      decoration: BoxDecoration(color: T.bg, borderRadius: BorderRadius.circular(10), border: Border.all(color: T.borderLight)),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          const Icon(Icons.notifications_none, size: 18, color: T.textMuted),
                          if (_notifCount > 0)
                            Positioned(
                              top: 6, right: 7,
                              child: Container(
                                height: 14, width: 14,
                                decoration: const BoxDecoration(color: T.error, shape: BoxShape.circle),
                                child: Center(child: Text(_notifCount > 9 ? '9+' : '$_notifCount', style: const TextStyle(fontSize: 8, fontWeight: FontWeight.w800, color: Colors.white))),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  InkWell(
                    onTap: () => context.go(Routes.profile),
                    borderRadius: BorderRadius.circular(10),
                    child: Container(
                      height: 36, width: 36,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [T.primary, Color(0xFF1A2D4A)], begin: Alignment.topLeft, end: Alignment.bottomRight),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Center(child: Text(initial, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Colors.white))),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
      body: widget.child,
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
          child: Container(
            height: 68,
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
            decoration: BoxDecoration(
              color: T.surface,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: T.borderLight),
              boxShadow: [
                BoxShadow(offset: const Offset(0, 8), blurRadius: 24, spreadRadius: -4, color: T.primary.withValues(alpha: 0.10)),
                BoxShadow(offset: const Offset(0, 2), blurRadius: 8, color: T.primary.withValues(alpha: 0.05)),
              ],
            ),
            child: Row(
              children: [
                for (int i = 0; i < _tabs.length; i++)
                  Expanded(
                    child: _NavItem(
                      selected: i == index,
                      iconOutline: _tabs[i].$2,
                      iconFilled: _tabs[i].$3,
                      label: _tabs[i].$4,
                      onTap: () => context.go(_tabs[i].$1),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final bool selected;
  final IconData iconOutline;
  final IconData iconFilled;
  final String label;
  final VoidCallback onTap;
  const _NavItem({required this.selected, required this.iconOutline, required this.iconFilled, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeOut,
        margin: const EdgeInsets.symmetric(horizontal: 2),
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 6),
        decoration: BoxDecoration(color: selected ? const Color(0xFFFFEDD5) : Colors.transparent, borderRadius: BorderRadius.circular(14)),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 180),
              transitionBuilder: (c, a) => ScaleTransition(scale: a, child: c),
              child: Icon(selected ? iconFilled : iconOutline, key: ValueKey(selected), size: 22, color: selected ? T.secondaryDark : T.navy500),
            ),
            const SizedBox(height: 3),
            Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 10.5, fontWeight: selected ? FontWeight.w700 : FontWeight.w600, letterSpacing: 0.01 * 10.5, color: selected ? T.primary : T.textLight, height: 1)),
          ],
        ),
      ),
    );
  }
}
