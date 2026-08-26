import 'package:go_router/go_router.dart';

import 'screens/analyzer_screen.dart';
import 'screens/auth/forgot_password_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/otp_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/cover_letter_screen.dart';
import 'screens/home_shell.dart';
import 'screens/interview_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/result_screen.dart';
import 'state/session.dart';

/// Route names shared by every screen.
abstract final class Routes {
  static const login = '/login';
  static const register = '/register';
  static const verify = '/verify';
  static const forgot = '/forgot';
  static const home = '/';
  static const result = '/result';
  static const interview = '/interview';
  static const coverLetter = '/cover-letter';
  static const profile = '/profile';
}

final _authLocations = {
  Routes.login,
  Routes.register,
  Routes.verify,
  Routes.forgot,
};

GoRouter buildRouter(Session session) {
  return GoRouter(
    initialLocation: Routes.home,
    refreshListenable: session,
    redirect: (context, state) {
      if (session.loading) return null;
      final authed = session.isAuthenticated;
      final onAuthScreen = _authLocations.contains(state.matchedLocation);
      if (!authed && !onAuthScreen) return Routes.login;
      if (authed && onAuthScreen) return Routes.home;
      return null;
    },
    routes: [
      GoRoute(
        path: Routes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: Routes.register,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: Routes.verify,
        builder: (context, state) => OtpScreen(
          email: state.uri.queryParameters['email'] ?? '',
          purpose: state.uri.queryParameters['purpose'] ?? 'register',
        ),
      ),
      GoRoute(
        path: Routes.forgot,
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => HomeShell(child: child),
        routes: [
          GoRoute(
            path: Routes.home,
            builder: (context, state) => const AnalyzerScreen(),
          ),
          GoRoute(
            path: Routes.result,
            builder: (context, state) => const ResultScreen(),
          ),
          GoRoute(
            path: Routes.interview,
            builder: (context, state) => const InterviewScreen(),
          ),
          GoRoute(
            path: Routes.coverLetter,
            builder: (context, state) => const CoverLetterScreen(),
          ),
          GoRoute(
            path: Routes.profile,
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),
    ],
  );
}
