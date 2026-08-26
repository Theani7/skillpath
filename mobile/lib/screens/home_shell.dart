import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../router.dart';

/// Bottom-nav app shell shared by all authenticated tabs.
class HomeShell extends StatelessWidget {
  final Widget child;
  const HomeShell({super.key, required this.child});

  static const _tabs = [
    (Routes.home, Icons.upload_file_outlined, 'Analyze'),
    (Routes.result, Icons.insights_outlined, 'Results'),
    (Routes.interview, Icons.record_voice_over_outlined, 'Interview'),
    (Routes.coverLetter, Icons.mail_outline, 'Cover Letter'),
    (Routes.profile, Icons.person_outline, 'Profile'),
  ];

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.path;
    var index = _tabs.indexWhere((t) => t.$1 == location);
    if (index < 0) index = 0;
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (i) => context.go(_tabs[i].$1),
        destinations: [
          for (final t in _tabs)
            NavigationDestination(icon: Icon(t.$2), label: t.$3),
        ],
      ),
    );
  }
}
