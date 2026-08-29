import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../router.dart';
import '../theme.dart';

/// Premium floating bottom nav — navy/orange Launchpad system.
class HomeShell extends StatelessWidget {
  final Widget child;
  const HomeShell({super.key, required this.child});

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

    return Scaffold(
      body: child,
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
        decoration: BoxDecoration(
          color: selected ? const Color(0xFFFFEDD5) : Colors.transparent,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 180),
              transitionBuilder: (c, a) => ScaleTransition(scale: a, child: c),
              child: Icon(
                selected ? iconFilled : iconOutline,
                key: ValueKey(selected),
                size: 22,
                color: selected ? T.secondaryDark : T.navy500,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 10.5,
                fontWeight: selected ? FontWeight.w700 : FontWeight.w600,
                letterSpacing: 0.01 * 10.5,
                color: selected ? T.primary : T.textLight,
                height: 1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
