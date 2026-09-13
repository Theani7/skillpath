import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../router.dart';
import '../theme.dart';
import '../widgets/onboarding/analysis_report_illustration.dart';
import '../widgets/onboarding/career_ascent_illustration.dart';
import '../widgets/onboarding/resume_audit_illustration.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _ctrl = PageController();
  int _index = 0;

  static const List<_OnboardItem> _pages = [
    _OnboardItem(
      title: 'Get a Clear Picture of Your Resume',
      desc: 'Upload your resume and let AI analyze it in seconds.',
      illustration: ResumeAuditIllustration(),
    ),
    _OnboardItem(
      title: 'Get Detailed Feedback',
      desc: "Find out what's working, what can be improved, and how to make your resume stronger.",
      illustration: AnalysisReportIllustration(),
    ),
    _OnboardItem(
      title: 'Build a Stronger You',
      desc: 'Create a better resume, unlock new opportunities, and take the next step in your career.',
      illustration: CareerAscentIllustration(),
    ),
  ];

  Future<void> _complete() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('hasSeenOnboarding', true);
    if (!mounted) return;
    context.go(Routes.login);
  }

  Future<void> _skip() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('hasSeenOnboarding', true);
    if (!mounted) return;
    context.go(Routes.login);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isLast = _index == _pages.length - 1;

    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          // Ambient soft background corner gradients
          Positioned(
            top: -120,
            right: -100,
            child: Container(
              width: 360,
              height: 360,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    T.primary.withValues(alpha: 0.05),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: -140,
            left: -140,
            child: Container(
              width: 380,
              height: 380,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    T.secondary.withValues(alpha: 0.06),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),

          SafeArea(
            child: Column(
              children: [
                // Top bar with Skip button
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  child: SizedBox(
                    height: 44,
                    child: Row(
                      children: [
                        const Spacer(),
                        AnimatedOpacity(
                          opacity: isLast ? 0.0 : 1.0,
                          duration: const Duration(milliseconds: 200),
                          child: IgnorePointer(
                            ignoring: isLast,
                            child: TextButton(
                              onPressed: _skip,
                              style: TextButton.styleFrom(
                                foregroundColor: T.textMuted,
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              ),
                              child: const Text(
                                'Skip',
                                style: TextStyle(
                                  fontSize: 14.5,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Main Page View
                Expanded(
                  child: PageView.builder(
                    controller: _ctrl,
                    itemCount: _pages.length,
                    onPageChanged: (i) => setState(() => _index = i),
                    itemBuilder: (context, index) {
                      final item = _pages[index];
                      return LayoutBuilder(
                        builder: (context, constraints) {
                          return SingleChildScrollView(
                            physics: const ClampingScrollPhysics(),
                            child: ConstrainedBox(
                              constraints: BoxConstraints(
                                minHeight: constraints.maxHeight,
                              ),
                              child: IntrinsicHeight(
                                child: Padding(
                                  padding: const EdgeInsets.symmetric(horizontal: 24),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.center,
                                    children: [
                                      const SizedBox(height: 8),

                                      // Headline
                                      Text(
                                        item.title,
                                        textAlign: TextAlign.center,
                                        style: displayStyle(context, 26).copyWith(
                                          fontWeight: FontWeight.w800,
                                          height: 1.25,
                                          letterSpacing: -0.5,
                                        ),
                                      ),
                                      const SizedBox(height: 12),

                                      // Subtitle
                                      Padding(
                                        padding: const EdgeInsets.symmetric(horizontal: 8),
                                        child: Text(
                                          item.desc,
                                          textAlign: TextAlign.center,
                                          style: const TextStyle(
                                            fontSize: 14.5,
                                            height: 1.5,
                                            color: T.textMuted,
                                            fontWeight: FontWeight.w400,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(height: 24),

                                      // Center Illustration
                                      Expanded(
                                        child: Center(
                                          child: FittedBox(
                                            fit: BoxFit.scaleDown,
                                            child: item.illustration,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(height: 12),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      );
                    },
                  ),
                ),

                // Bottom Indicator & Action CTA
                Padding(
                  padding: const EdgeInsets.fromLTRB(24, 8, 24, 28),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 3-dot indicator
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          for (int i = 0; i < _pages.length; i++)
                            AnimatedContainer(
                              duration: const Duration(milliseconds: 250),
                              margin: const EdgeInsets.symmetric(horizontal: 4),
                              height: 7,
                              width: _index == i ? 22 : 7,
                              decoration: BoxDecoration(
                                color: _index == i ? T.secondary : const Color(0xFFD4D8E0),
                                borderRadius: BorderRadius.circular(100),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 22),

                      // CTA Button
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: FilledButton(
                          onPressed: () {
                            if (!isLast) {
                              _ctrl.nextPage(
                                duration: const Duration(milliseconds: 320),
                                curve: Curves.easeInOut,
                              );
                            } else {
                              _complete();
                            }
                          },
                          style: FilledButton.styleFrom(
                            backgroundColor: T.secondary,
                            foregroundColor: Colors.white,
                            elevation: 2,
                            shadowColor: T.secondary.withValues(alpha: 0.35),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          child: isLast
                              ? const Text(
                                  'Get Started',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w700,
                                    color: Colors.white,
                                  ),
                                )
                              : const Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      'Next',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w700,
                                        color: Colors.white,
                                      ),
                                    ),
                                    SizedBox(width: 8),
                                    Icon(
                                      Icons.arrow_forward,
                                      size: 18,
                                      color: Colors.white,
                                    ),
                                  ],
                                ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _OnboardItem {
  final String title;
  final String desc;
  final Widget illustration;

  const _OnboardItem({
    required this.title,
    required this.desc,
    required this.illustration,
  });
}
