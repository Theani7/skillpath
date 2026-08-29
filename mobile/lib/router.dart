import 'package:go_router/go_router.dart';

import 'screens/analyzer_screen.dart';
import 'screens/auth/forgot_password_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/otp_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/cover_letter_screen.dart';
import 'screens/edit_profile_screen.dart';
import 'screens/home_shell.dart';
import 'screens/interview_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/result_screen.dart';
import 'screens/splash_screen.dart';
import 'state/session.dart';

/// Route names shared by every screen.
abstract final class Routes {
  static const splash = '/splash';
  static const onboarding = '/onboarding';
  static const login = '/login';
  static const register = '/register';
  static const verify = '/verify';
  static const forgot = '/forgot';
  static const home = '/';
  static const result = '/result';
  static const interview = '/interview';
  static const coverLetter = '/cover-letter';
  static const profile = '/profile';
  static const editProfile = '/profile/edit';
  static const notifications = '/notifications';
}

final _authLocations = {
  Routes.login,
  Routes.register,
  Routes.verify,
  Routes.forgot,
};

GoRouter buildRouter(Session session, {bool hasSeenOnboarding = true}) {
  return GoRouter(
    initialLocation: Routes.splash,
    refreshListenable: session,
    redirect: (context, state) {
      final loc = state.matchedLocation;
      final isSplash = loc == Routes.splash;
      final isOnboarding = loc == Routes.onboarding;

      if (session.loading) return isSplash ? null : Routes.splash;

      // first-run onboarding for unauthed users
      if (!hasSeenOnboarding && !session.isAuthenticated && !isOnboarding && !isSplash && !_authLocations.contains(loc)) {
        return Routes.onboarding;
      }
      if (!hasSeenOnboarding && isSplash && !session.isAuthenticated) return Routes.onboarding;

      final authed = session.isAuthenticated;
      final onAuthScreen = _authLocations.contains(loc);
      final onSplashOrOnboarding = isSplash || isOnboarding;

      if (!authed && !onAuthScreen && !onSplashOrOnboarding) return Routes.login;
      if (authed && (onAuthScreen || onSplashOrOnboarding)) return Routes.home;
      if (isSplash) return authed ? Routes.home : (hasSeenOnboarding ? Routes.login : Routes.onboarding);
      return null;
    },
    routes: [
      GoRoute(path: Routes.splash, builder: (context, state) => const SplashScreen()),
      GoRoute(path: Routes.onboarding, builder: (context, state) => const OnboardingScreen()),
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
      GoRoute(path: Routes.editProfile, builder: (context, state) => const EditProfileScreen()),
      GoRoute(path: Routes.notifications, builder: (context, state) => const NotificationsScreen()),
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
