import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:shared_preferences/shared_preferences.dart';

import 'config.dart';
import 'router.dart';
import 'services/api_client.dart';
import 'state/session.dart';
import 'theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Api.init(kApiBaseUrl);
  final prefs = await SharedPreferences.getInstance();
  final hasSeenOnboarding = prefs.getBool('hasSeenOnboarding') ?? false;
  final session = Session();
  // Non-fatal: the router shows the login screen when restore() fails.
  unawaitedRestore(session);
  runApp(SkillPathApp(session: session, hasSeenOnboarding: hasSeenOnboarding));
}

void unawaitedRestore(Session session) {
  session.restore();
}

class SkillPathApp extends StatelessWidget {
  final Session session;
  final bool hasSeenOnboarding;
  const SkillPathApp({super.key, required this.session, required this.hasSeenOnboarding});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: session,
      child: MaterialApp.router(
        title: kAppName,
        debugShowCheckedModeBanner: false,
        theme: buildTheme(),
        routerConfig: buildRouter(session, hasSeenOnboarding: hasSeenOnboarding),
      ),
    );
  }
}
