import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../router.dart';
import '../../state/session.dart';
import '../../theme.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _password = TextEditingController();
  bool _submitting = false;
  bool _showPass = false;
  String? _error;

  @override
  void dispose() {
    _username.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _error = null;
    });
    final error = await context.read<Session>().login(
      _username.text.trim(),
      _password.text,
    );
    if (!mounted) return;
    // On success the router's auth guard redirects automatically.
    setState(() {
      _submitting = false;
      _error = error;
    });
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
                          height: 64, width: 64,
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
                            const Icon(Icons.waving_hand, size: 14, color: T.primary),
                            const SizedBox(width: 4),
                            Text('WELCOME BACK • SECURE',
                                style: TextStyle(
                                  fontSize: 11, fontWeight: FontWeight.w700,
                                  letterSpacing: 0.08 * 11, color: T.primary,
                                )),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text('Welcome back',
                          textAlign: TextAlign.center,
                          style: displayStyle(context, 30)),
                      const SizedBox(height: 8),
                      const Text(
                        'Sign in to continue your career journey\nand unlock AI-powered insights.',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 14.5, height: 1.55, color: T.textMuted),
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
                      child: Column(
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
                                    height: 22, width: 22,
                                    decoration: const BoxDecoration(color: T.error, shape: BoxShape.circle),
                                    child: const Icon(Icons.priority_high, size: 14, color: Colors.white),
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Text(_error!,
                                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: T.error, height: 1.35)),
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

                          // Username / email
                          const Text('Username or email',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
                          const SizedBox(height: 6),
                          TextFormField(
                            controller: _username,
                            decoration: const InputDecoration(
                              hintText: 'you@example.com or handle',
                              prefixIcon: Icon(Icons.person_outline, size: 18, color: T.textLight),
                            ),
                            autofillHints: const [AutofillHints.username],
                            textInputAction: TextInputAction.next,
                            validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null,
                          ),
                          const SizedBox(height: 14),

                          // Password
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
                              hintText: 'Enter your password',
                              prefixIcon: const Icon(Icons.lock_outline, size: 18, color: T.textLight),
                              suffixIcon: IconButton(
                                icon: Icon(_showPass ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                    size: 18, color: T.textLight),
                                onPressed: () => setState(() => _showPass = !_showPass),
                                tooltip: _showPass ? 'Hide' : 'Show',
                              ),
                            ),
                            autofillHints: const [AutofillHints.password],
                            onFieldSubmitted: (_) => _submit(),
                            validator: (v) => (v == null || v.isEmpty) ? 'Required' : null,
                          ),
                          const SizedBox(height: 18),

                          // Submit
                          FilledButton(
                            onPressed: _submitting ? null : _submit,
                            style: FilledButton.styleFrom(
                              minimumSize: const Size.fromHeight(48),
                              backgroundColor: T.primary,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
                            ),
                            child: _submitting
                                ? const SizedBox(
                                    height: 18, width: 18,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
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
                          const SizedBox(height: 14),

                          // Divider
                          Row(
                            children: [
                              const Expanded(child: Divider(color: T.border, thickness: 1)),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10),
                                child: const Text('or',
                                    style: TextStyle(fontSize: 12, color: T.textLight, fontWeight: FontWeight.w600)),
                              ),
                              const Expanded(child: Divider(color: T.border, thickness: 1)),
                            ],
                          ),
                          const SizedBox(height: 14),

                          // Google
                          OutlinedButton.icon(
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Google sign-in coming soon')),
                              );
                            },
                            icon: const _GoogleIcon(),
                            label: const Text('Continue with Google',
                                style: TextStyle(fontWeight: FontWeight.w700, color: T.primary)),
                            style: OutlinedButton.styleFrom(
                              minimumSize: const Size.fromHeight(48),
                              backgroundColor: T.surface,
                              side: const BorderSide(color: T.border),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),

                  // Footer
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text("Don't have an account?",
                          style: TextStyle(fontSize: 13.5, color: T.textMuted)),
                      TextButton(
                        onPressed: () => context.go(Routes.register),
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
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
}

class _GoogleIcon extends StatelessWidget {
  const _GoogleIcon();
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 18, width: 18,
      child: CustomPaint(painter: _GooglePainter()),
    );
  }
}

class _GooglePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final r = size.width / 2;
    final center = Offset(r, r);
    final paint = Paint()..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round;
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
