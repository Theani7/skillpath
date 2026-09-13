import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../config.dart';
import '../../router.dart';
import '../../services/api_client.dart';
import '../../state/session.dart';
import '../../theme.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();

  int _step = 1; // 1 = Email, 2 = Password
  bool _checkingEmail = false;
  bool _submitting = false;
  bool _showPass = false;
  bool _accountNotFound = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _checkEmailAndProceed() async {
    if (!_formKey.currentState!.validate()) return;
    final email = _email.text.trim();

    setState(() {
      _checkingEmail = true;
      _error = null;
      _accountNotFound = false;
    });

    try {
      final res = await Api.instance.dio.get(
        '/api/auth/check-email/${Uri.encodeComponent(email)}',
      );
      if (!mounted) return;

      if (res.statusCode == 200 && res.data is Map) {
        final exists = res.data['exists'] == true;
        if (exists) {
          setState(() {
            _step = 2;
            _checkingEmail = false;
          });
        } else {
          setState(() {
            _accountNotFound = true;
            _checkingEmail = false;
          });
        }
        return;
      }
    } catch (_) {
      // In offline / fallback mode, advance to password step gracefully
      if (!mounted) return;
      setState(() {
        _step = 2;
        _checkingEmail = false;
      });
      return;
    }

    if (mounted) {
      setState(() => _checkingEmail = false);
    }
  }

  Future<void> _submitPassword() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _error = null;
    });

    final error = await context.read<Session>().login(
      _email.text.trim(),
      _password.text,
    );
    if (!mounted) return;

    // On success the router's auth guard redirects automatically.
    setState(() {
      _submitting = false;
      _error = error;
    });
  }

  Future<void> _continueWithGoogle() async {
    final googleUrl = Uri.parse('$kApiBaseUrl/api/auth/google');
    try {
      final canLaunch = await canLaunchUrl(googleUrl);
      if (canLaunch) {
        await launchUrl(googleUrl, mode: LaunchMode.externalApplication);
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Google sign-in is not configured yet.')),
        );
      }
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to launch Google authentication.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 8),

                  // ── Brand header ──
                  Column(
                    children: [
                      Hero(
                        tag: 'skillpath-logo',
                        child: Container(
                          height: 64,
                          width: 64,
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: T.surface,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: T.borderLight),
                            boxShadow: T.cardShadow,
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(10),
                            child: Image.asset('assets/icon.png', fit: BoxFit.contain),
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(100),
                          border: Border.all(color: const Color(0xFFDBEAFE)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              _step == 1 ? Icons.lock_outline : Icons.shield_outlined,
                              size: 14,
                              color: T.primary,
                            ),
                            const SizedBox(width: 5),
                            Text(
                              _step == 1 ? 'SECURE SIGN IN • STEP 1' : 'ENTER PASSWORD • STEP 2',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.08 * 11,
                                color: T.primary,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        _step == 1 ? 'Welcome back' : 'Enter your password',
                        textAlign: TextAlign.center,
                        style: displayStyle(context, 30),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _step == 1
                            ? 'Enter your email to access your account\nand unlock AI-powered insights.'
                            : 'Verify your credentials to continue your journey.',
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 14.5, height: 1.55, color: T.textMuted),
                      ),
                    ],
                  ),
                  const SizedBox(height: 22),

                  // ── Form card ──
                  Container(
                    padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
                    decoration: BoxDecoration(
                      color: T.surface,
                      borderRadius: BorderRadius.circular(T.radiusXl),
                      border: Border.all(color: T.borderLight),
                      boxShadow: T.cardShadow,
                    ),
                    child: Form(
                      key: _formKey,
                      child: AnimatedSwitcher(
                        duration: const Duration(milliseconds: 280),
                        transitionBuilder: (child, animation) {
                          return FadeTransition(
                            opacity: animation,
                            child: SlideTransition(
                              position: Tween<Offset>(
                                begin: child.key == const ValueKey(2)
                                    ? const Offset(0.08, 0)
                                    : const Offset(-0.08, 0),
                                end: Offset.zero,
                              ).animate(CurvedAnimation(parent: animation, curve: Curves.easeOutCubic)),
                              child: child,
                            ),
                          );
                        },
                        child: _step == 1 ? _buildStep1() : _buildStep2(),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Footer
                  Wrap(
                    alignment: WrapAlignment.center,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      const Text("Don't have an account?",
                          style: TextStyle(fontSize: 13.5, color: T.textMuted)),
                      const SizedBox(width: 4),
                      TextButton(
                        onPressed: () => context.go(Routes.register),
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: const Text('Create account',
                            style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: T.secondaryDark)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'By signing in you agree to our Terms and Privacy Policy.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 11, color: T.textLight, height: 1.4),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ── Step 1: Email & Google ──
  Widget _buildStep1() {
    return Column(
      key: const ValueKey<int>(1),
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_accountNotFound) ...[
          Container(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
            decoration: BoxDecoration(
              color: const Color(0xFFFEF2F2),
              borderRadius: BorderRadius.circular(T.radiusLg),
              border: Border.all(color: const Color(0xFFFECACA)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline_rounded, size: 18, color: T.error),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'No account found with this email.',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: T.error),
                  ),
                ),
                TextButton(
                  onPressed: () => context.go(Routes.register),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: const Text(
                    'Sign up',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: T.secondaryDark),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
        ],

        const Text(
          'Email address',
          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155)),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: _email,
          keyboardType: TextInputType.emailAddress,
          autofillHints: const [AutofillHints.email],
          textInputAction: TextInputAction.next,
          onFieldSubmitted: (_) => _checkEmailAndProceed(),
          decoration: const InputDecoration(
            hintText: 'you@example.com',
            prefixIcon: Icon(Icons.alternate_email_rounded, size: 18, color: T.textLight),
          ),
          validator: (v) {
            final val = v?.trim() ?? '';
            if (val.isEmpty) return 'Email is required';
            final emailRegex = RegExp(r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$');
            if (!emailRegex.hasMatch(val)) return 'Enter a valid email address';
            return null;
          },
        ),
        const SizedBox(height: 18),

        // Continue Button
        FilledButton(
          onPressed: _checkingEmail ? null : _checkEmailAndProceed,
          style: FilledButton.styleFrom(
            minimumSize: const Size.fromHeight(48),
            backgroundColor: T.primary,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
          ),
          child: _checkingEmail
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Continue', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Colors.white)),
                    SizedBox(width: 8),
                    Icon(Icons.arrow_forward_rounded, size: 16, color: Colors.white),
                  ],
                ),
        ),
        const SizedBox(height: 14),

        // Divider
        Row(
          children: [
            const Expanded(child: Divider(color: T.border, thickness: 1)),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10),
              child: const Text('or', style: TextStyle(fontSize: 12, color: T.textLight, fontWeight: FontWeight.w600)),
            ),
            const Expanded(child: Divider(color: T.border, thickness: 1)),
          ],
        ),
        const SizedBox(height: 14),

        // Continue with Google
        OutlinedButton.icon(
          onPressed: _continueWithGoogle,
          icon: const _GoogleIcon(),
          label: const Text('Continue with Google', style: TextStyle(fontWeight: FontWeight.w700, color: T.primary)),
          style: OutlinedButton.styleFrom(
            minimumSize: const Size.fromHeight(48),
            backgroundColor: T.surface,
            side: const BorderSide(color: T.border),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
          ),
        ),
      ],
    );
  }

  // ── Step 2: Password Entry ──
  Widget _buildStep2() {
    return Column(
      key: const ValueKey<int>(2),
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_error != null) ...[
          Container(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
            decoration: BoxDecoration(
              color: T.errorLight,
              borderRadius: BorderRadius.circular(T.radiusLg),
              border: Border.all(color: const Color(0xFFFECACA)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  height: 22,
                  width: 22,
                  decoration: const BoxDecoration(color: T.error, shape: BoxShape.circle),
                  child: const Icon(Icons.priority_high, size: 14, color: Colors.white),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    _error!,
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: T.error, height: 1.35),
                  ),
                ),
                InkWell(
                  onTap: () => setState(() => _error = null),
                  child: const Icon(Icons.close, size: 16, color: T.error),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
        ],

        // Verified Email Pill
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFFF1F5F9),
            borderRadius: BorderRadius.circular(T.radiusLg),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Row(
            children: [
              Container(
                height: 32,
                width: 32,
                decoration: const BoxDecoration(
                  color: T.primary,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.person, size: 18, color: Colors.white),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'ACCOUNT',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        color: T.textLight,
                        letterSpacing: 0.6,
                      ),
                    ),
                    Text(
                      _email.text.trim(),
                      style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: T.primary),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              TextButton(
                onPressed: () {
                  setState(() {
                    _step = 1;
                    _error = null;
                  });
                },
                style: TextButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: const Text('Change', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: T.secondaryDark)),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Password label
        Row(
          children: [
            const Text('Password',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
            const Spacer(),
            InkWell(
              onTap: () => context.go(Routes.forgot),
              borderRadius: BorderRadius.circular(6),
              child: const Padding(
                padding: EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                child: Text('Forgot password?',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: T.secondaryDark)),
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: _password,
          obscureText: !_showPass,
          decoration: InputDecoration(
            hintText: '••••••••',
            prefixIcon: const Icon(Icons.lock_outline, size: 18, color: T.textLight),
            suffixIcon: IconButton(
              icon: Icon(_showPass ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                  size: 18, color: T.textLight),
              onPressed: () => setState(() => _showPass = !_showPass),
              tooltip: _showPass ? 'Hide' : 'Show',
            ),
          ),
          autofillHints: const [AutofillHints.password],
          onFieldSubmitted: (_) => _submitPassword(),
          validator: (v) => (v == null || v.isEmpty) ? 'Password is required' : null,
        ),
        const SizedBox(height: 18),

        // Sign in Submit
        FilledButton(
          onPressed: _submitting ? null : _submitPassword,
          style: FilledButton.styleFrom(
            minimumSize: const Size.fromHeight(48),
            backgroundColor: T.secondary,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
          ),
          child: _submitting
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.login, size: 18, color: Colors.white),
                    SizedBox(width: 8),
                    Text('Sign in',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Colors.white)),
                    SizedBox(width: 8),
                    Icon(Icons.arrow_forward, size: 16, color: Colors.white),
                  ],
                ),
        ),
      ],
    );
  }
}

class _GoogleIcon extends StatelessWidget {
  const _GoogleIcon();
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 18,
      width: 18,
      child: CustomPaint(painter: _GooglePainter()),
    );
  }
}

class _GooglePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final r = size.width / 2;
    final center = Offset(r, r);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;
    paint.color = const Color(0xFF4285F4);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), -0.6, 1.9, false, paint);
    paint.color = const Color(0xFF34A853);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), 1.3, 1.4, false, paint);
    paint.color = const Color(0xFFFBBC05);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), 2.7, 1.2, false, paint);
    paint.color = const Color(0xFFEA4335);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), 3.9, 1.1, false, paint);
    paint.style = PaintingStyle.fill;
    paint.color = const Color(0xFF4285F4);
    canvas.drawRect(Rect.fromLTWH(center.dx - 1, center.dy - 1, r - 1, 2), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
