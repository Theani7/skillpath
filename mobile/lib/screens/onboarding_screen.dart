import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../router.dart';
import '../theme.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _ctrl = PageController();
  int _index = 0;

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
    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          Positioned(top: -120, right: -100, child: Container(width: 360, height: 360, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.primary.withValues(alpha: 0.06), Colors.transparent])))),
          Positioned(bottom: -140, left: -140, child: Container(width: 380, height: 380, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.secondary.withValues(alpha: 0.05), Colors.transparent])))),
          SafeArea(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                  child: Row(
                    children: [
                      const Spacer(),
                      TextButton(onPressed: _skip, child: const Text('Skip', style: TextStyle(color: T.textMuted, fontWeight: FontWeight.w700))),
                    ],
                  ),
                ),
                Expanded(
                  child: PageView(
                    controller: _ctrl,
                    onPageChanged: (i) => setState(() => _index = i),
                    children: const [
                      _OnboardPage(
                        icon: Icons.cloud_upload_outlined,
                        title: 'Upload your resume',
                        desc: 'Drop a PDF or DOCX — we extract every skill with magic-byte validation and 5 MB limit.',
                        color: T.primary,
                        bg: T.navy100,
                      ),
                      _OnboardPage(
                        icon: Icons.insights_outlined,
                        title: 'Discover skill gaps',
                        desc: 'AI compares you to 22 target roles and shows 82% match style insights in seconds.',
                        color: T.secondaryDark,
                        bg: Color(0xFFFFEDD5),
                      ),
                      _OnboardPage(
                        icon: Icons.map_outlined,
                        title: 'Get your roadmap',
                        desc: 'Personalized learning path with courses, projects and interview practice to land the role.',
                        color: T.success,
                        bg: T.successLight,
                        isLast: true,
                      ),
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          for (int i = 0; i < 3; i++)
                            AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              margin: const EdgeInsets.symmetric(horizontal: 4),
                              height: 6,
                              width: _index == i ? 22 : 6,
                              decoration: BoxDecoration(color: _index == i ? T.primary : T.border, borderRadius: BorderRadius.circular(100)),
                            ),
                        ],
                      ),
                      const SizedBox(height: 18),
                      SizedBox(
                        width: double.infinity,
                        child: FilledButton(
                          onPressed: () {
                            if (_index < 2) {
                              _ctrl.nextPage(duration: const Duration(milliseconds: 280), curve: Curves.easeOut);
                            } else {
                              _complete();
                            }
                          },
                          style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48), backgroundColor: _index == 2 ? T.secondary : T.primary, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg))),
                          child: Text(_index == 2 ? 'Get Started' : 'Next', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
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

class _OnboardPage extends StatelessWidget {
  final IconData icon;
  final String title;
  final String desc;
  final Color color;
  final Color bg;
  final bool isLast;
  const _OnboardPage({required this.icon, required this.title, required this.desc, required this.color, required this.bg, this.isLast = false});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 8),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Hero(
            tag: isLast ? 'skillpath-logo' : 'onboard-$title',
            child: Container(
              height: isLast ? 78 : 96, width: isLast ? 78 : 96,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: isLast ? T.surface : bg, borderRadius: BorderRadius.circular(20), border: Border.all(color: isLast ? T.borderLight : Colors.transparent), boxShadow: isLast ? T.cardShadow : []),
              child: isLast
                  ? ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.asset('assets/icon.png', fit: BoxFit.contain))
                  : Icon(icon, size: 42, color: color),
            ),
          ),
          const SizedBox(height: 22),
          Text(title, textAlign: TextAlign.center, style: displayStyle(context, 24)),
          const SizedBox(height: 10),
          Text(desc, textAlign: TextAlign.center, style: const TextStyle(fontSize: 14, height: 1.6, color: T.textMuted)),
          if (!isLast) ...[
            const SizedBox(height: 18),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(100), border: Border.all(color: T.borderLight)),
              child: Text(
                switch (title) {
                  'Upload your resume' => 'PDF • DOCX • 5 MB',
                  'Discover skill gaps' => '22 roles • 15 skills each',
                  _ => 'Courses • Projects • Interviews',
                },
                style: const TextStyle(fontSize: 11, color: T.textLight, fontWeight: FontWeight.w700),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
