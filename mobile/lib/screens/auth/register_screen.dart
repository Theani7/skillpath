import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../router.dart';
import '../../services/api_client.dart';
import '../../services/auth_service.dart';
import '../../theme.dart';
import 'otp_screen.dart';

final _usernamePattern = RegExp(r'^[A-Za-z0-9_.-]{3,50}$');
final _emailPattern = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

enum _UsernameState { idle, checking, available, taken }

int _passwordStrength(String v) {
  if (v.isEmpty) return 0;
  var score = 0;
  if (v.length >= 8) score++;
  if (v.length >= 12) score++;
  if (RegExp(r'[A-Z]').hasMatch(v)) score++;
  if (RegExp(r'[a-z]').hasMatch(v)) score++;
  if (RegExp(r'[0-9]').hasMatch(v)) score++;
  if (RegExp(r'[^A-Za-z0-9]').hasMatch(v)) score++;
  // normalize to 0-5
  if (score >= 6) return 5;
  if (score >= 5) return 4;
  if (score >= 4) return 3;
  if (score >= 3) return 2;
  if (score >= 1) return 1;
  return 0;
}

String _strengthLabel(int s) => switch (s) {
      0 => 'Too weak',
      1 => 'Weak',
      2 => 'Fair',
      3 => 'Good',
      4 => 'Strong',
      _ => 'Very strong',
    };

Color _strengthColor(int s) => switch (s) {
      0 => T.border,
      1 => T.error,
      2 => const Color(0xFFF97316),
      3 => const Color(0xFFEAB308),
      4 => const Color(0xFF22C55E),
      _ => const Color(0xFF059669),
    };

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstName = TextEditingController();
  final _lastName = TextEditingController();
  final _username = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  Timer? _debounce;
  bool _submitting = false;
  bool _showPass = false;
  bool _agreed = true;
  _UsernameState _usernameState = _UsernameState.idle;
  String? _error;

  @override
  void dispose() {
    _debounce?.cancel();
    _firstName.dispose();
    _lastName.dispose();
    _username.dispose();
    _email.dispose();
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  void _onUsernameChanged(String value) {
    _debounce?.cancel();
    final valid = _usernamePattern.hasMatch(value);
    if (!valid) {
      setState(() => _usernameState = _UsernameState.idle);
      return;
    }
    setState(() => _usernameState = _UsernameState.checking);
    _debounce = Timer(const Duration(milliseconds: 500), () async {
      try {
        final available = await AuthService.checkUsername(value);
        if (!mounted) return;
        setState(
          () => _usernameState = available
              ? _UsernameState.available
              : _UsernameState.taken,
        );
      } catch (_) {
        if (!mounted) return;
        setState(() => _usernameState = _UsernameState.idle);
      }
    });
  }

  Widget? get _usernameSuffix {
    switch (_usernameState) {
      case _UsernameState.checking:
        return const SizedBox(
          height: 18, width: 18,
          child: CircularProgressIndicator(strokeWidth: 2, color: T.secondary),
        );
      case _UsernameState.available:
        return const Icon(Icons.check_circle, color: T.success, size: 20);
      case _UsernameState.taken:
        return const Icon(Icons.cancel, color: T.error, size: 20);
      case _UsernameState.idle:
        return null;
    }
  }

  String get _fullName {
    final f = _firstName.text.trim();
    final l = _lastName.text.trim();
    if (f.isEmpty) return l;
    if (l.isEmpty) return f;
    return '$f $l';
  }

  bool get _passwordsMatch =>
      _password.text.isNotEmpty && _password.text == _confirm.text;
  bool get _passwordsMismatch =>
      _confirm.text.isNotEmpty && _confirm.text != _password.text;

  Future<Response> _registerRaw() => Api.instance.dio.post(
        '/api/auth/register',
        data: {
          'username': _username.text.trim(),
          'email': _email.text.trim(),
          'password': _password.text,
          'full_name': _fullName,
        },
      );

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_usernameState == _UsernameState.taken) {
      setState(() => _error = 'Username is already taken');
      return;
    }
    if (!_agreed) {
      setState(() => _error = 'Please agree to the Terms to continue');
      return;
    }
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      final res = await _registerRaw();
      if (!mounted) return;
      final map = (res.data as Map?)?.cast<String, dynamic>() ?? {};
      if (res.statusCode == 200) {
        if (map['debug_otp'] != null) {
          OtpScreen.devHint = map['debug_otp'].toString();
        }
        final encoded = Uri.encodeQueryComponent(_email.text.trim());
        context.go('${Routes.verify}?email=$encoded&purpose=register');
        return;
      }
      setState(() {
        _submitting = false;
        _error = map['message']?.toString() ?? 'Registration failed';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _error = Api.errorMessage(e);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final strength = _passwordStrength(_password.text);
    final canSubmit = !_submitting;

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
                  // ── Top bar ──
                  Align(
                    alignment: Alignment.centerLeft,
                    child: InkWell(
                      onTap: () => context.go(Routes.login),
                      borderRadius: BorderRadius.circular(10),
                      child: Container(
                        height: 36, width: 36,
                        decoration: BoxDecoration(
                          color: T.surface,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: T.borderLight),
                        ),
                        child: const Icon(Icons.arrow_back, size: 18, color: T.textMuted),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // ── Brand header ──
                  Column(
                    children: [
                      Container(
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
                      const SizedBox(height: 14),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFFEDD5),
                          borderRadius: BorderRadius.circular(100),
                          border: Border.all(color: const Color(0xFFFFD7B8)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.bolt, size: 14, color: T.secondaryDark),
                            const SizedBox(width: 4),
                            Text('CREATE YOUR ACCOUNT • FREE',
                                style: TextStyle(
                                  fontSize: 11, fontWeight: FontWeight.w700,
                                  letterSpacing: 0.08 * 11, color: T.secondaryDark,
                                )),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text('Create your account',
                          textAlign: TextAlign.center,
                          style: displayStyle(context, 30)),
                      const SizedBox(height: 8),
                      const Text(
                        'Join SkillPath and get AI-powered resume insights\nin under 30 seconds.',
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
                      autovalidateMode: AutovalidateMode.onUserInteraction,
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

                          // First + Last name row
                          Row(
                            children: [
                              Expanded(
                                child: _FieldLabel(
                                  label: 'First name',
                                  child: TextFormField(
                                    controller: _firstName,
                                    textInputAction: TextInputAction.next,
                                    autofillHints: const [AutofillHints.givenName],
                                    decoration: const InputDecoration(
                                      hintText: 'First',
                                      prefixIcon: Icon(Icons.person_outline, size: 18, color: T.textLight),
                                    ),
                                    validator: (v) =>
                                        (v == null || v.trim().isEmpty) ? 'Required' : null,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _FieldLabel(
                                  label: 'Last name',
                                  optional: true,
                                  child: TextFormField(
                                    controller: _lastName,
                                    textInputAction: TextInputAction.next,
                                    autofillHints: const [AutofillHints.familyName],
                                    decoration: const InputDecoration(
                                      hintText: 'Last',
                                      prefixIcon: Icon(Icons.person_outline, size: 18, color: T.textLight),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 14),

                          // Username
                          _FieldLabel(
                            label: 'Username',
                            trailing: switch (_usernameState) {
                              _UsernameState.available =>
                                const Row(mainAxisSize: MainAxisSize.min, children: [
                                  Icon(Icons.check, size: 11, color: T.success),
                                  SizedBox(width: 3),
                                  Text('Available', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: T.success)),
                                ]),
                              _UsernameState.taken =>
                                const Row(mainAxisSize: MainAxisSize.min, children: [
                                  Icon(Icons.close, size: 11, color: T.error),
                                  SizedBox(width: 3),
                                  Text('Taken', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: T.error)),
                                ]),
                              _ => const SizedBox.shrink(),
                            },
                            child: TextFormField(
                              controller: _username,
                              onChanged: _onUsernameChanged,
                              textInputAction: TextInputAction.next,
                              autofillHints: const [AutofillHints.newUsername],
                              decoration: InputDecoration(
                                hintText: 'choose-a-handle',
                                prefixIcon: const Icon(Icons.alternate_email, size: 18, color: T.textLight),
                                suffixIcon: _usernameSuffix == null
                                    ? null
                                    : Padding(
                                        padding: const EdgeInsets.only(right: 12),
                                        child: _usernameSuffix,
                                      ),
                                suffixIconConstraints:
                                    const BoxConstraints(minHeight: 18, minWidth: 18),
                              ),
                              validator: (v) {
                                final value = v?.trim() ?? '';
                                if (!_usernamePattern.hasMatch(value)) {
                                  return '3-50 chars; letters, digits, . _ - only';
                                }
                                if (_usernameState == _UsernameState.taken) {
                                  return 'Username is already taken';
                                }
                                return null;
                              },
                            ),
                          ),
                          if (_usernameState == _UsernameState.idle &&
                              _username.text.isNotEmpty &&
                              _username.text.length < 3)
                            const Padding(
                              padding: EdgeInsets.only(top: 6, left: 2),
                              child: Text('Minimum 3 characters.',
                                  style: TextStyle(fontSize: 11, color: T.textLight)),
                            ),
                          const SizedBox(height: 14),

                          // Email
                          _FieldLabel(
                            label: 'Email',
                            child: TextFormField(
                              controller: _email,
                              keyboardType: TextInputType.emailAddress,
                              textInputAction: TextInputAction.next,
                              autofillHints: const [AutofillHints.email],
                              decoration: const InputDecoration(
                                hintText: 'you@example.com',
                                prefixIcon: Icon(Icons.mail_outline, size: 18, color: T.textLight),
                              ),
                              validator: (v) => !_emailPattern.hasMatch(v?.trim() ?? '')
                                  ? 'Enter a valid email'
                                  : null,
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Password
                          _FieldLabel(
                            label: 'Password',
                            trailing: InkWell(
                              onTap: () => setState(() => _showPass = !_showPass),
                              borderRadius: BorderRadius.circular(6),
                              child: Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(_showPass ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                        size: 13, color: T.secondaryDark),
                                    const SizedBox(width: 4),
                                    Text(_showPass ? 'Hide' : 'Show',
                                        style: const TextStyle(
                                            fontSize: 12, fontWeight: FontWeight.w600, color: T.secondaryDark)),
                                  ],
                                ),
                              ),
                            ),
                            child: TextFormField(
                              controller: _password,
                              obscureText: !_showPass,
                              textInputAction: TextInputAction.next,
                              autofillHints: const [AutofillHints.newPassword],
                              onChanged: (_) => setState(() {}),
                              decoration: const InputDecoration(
                                hintText: 'At least 8 characters',
                                prefixIcon: Icon(Icons.lock_outline, size: 18, color: T.textLight),
                              ),
                              validator: (v) =>
                                  (v == null || v.length < 8) ? 'At least 8 characters' : null,
                            ),
                          ),
                          if (_password.text.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(100),
                              child: LinearProgressIndicator(
                                value: strength / 5,
                                minHeight: 4,
                                backgroundColor: T.borderLight,
                                valueColor: AlwaysStoppedAnimation(_strengthColor(strength)),
                              ),
                            ),
                            const SizedBox(height: 6),
                            Row(
                              children: [
                                if (strength >= 4)
                                  const Icon(Icons.check_circle, size: 12, color: T.success),
                                if (strength >= 4) const SizedBox(width: 4),
                                Text(_strengthLabel(strength),
                                    style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w700,
                                        color: _strengthColor(strength))),
                                if (strength > 0 && strength < 5)
                                  const Text(' — try mixing uppercase, numbers & symbols.',
                                      style: TextStyle(fontSize: 11, color: T.textLight)),
                              ],
                            ),
                          ],
                          const SizedBox(height: 14),

                          // Confirm
                          _FieldLabel(
                            label: 'Confirm password',
                            trailing: _passwordsMatch
                                ? const Row(mainAxisSize: MainAxisSize.min, children: [
                                    Icon(Icons.check, size: 11, color: T.success),
                                    SizedBox(width: 3),
                                    Text('Matches', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: T.success)),
                                  ])
                                : _passwordsMismatch
                                    ? const Row(mainAxisSize: MainAxisSize.min, children: [
                                        Icon(Icons.close, size: 11, color: T.error),
                                        SizedBox(width: 3),
                                        Text("Doesn't match",
                                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: T.error)),
                                      ])
                                    : const SizedBox.shrink(),
                            child: TextFormField(
                              controller: _confirm,
                              obscureText: !_showPass,
                              autofillHints: const [AutofillHints.newPassword],
                              onChanged: (_) => setState(() {}),
                              decoration: InputDecoration(
                                hintText: 'Re-enter your password',
                                prefixIcon: const Icon(Icons.lock_outline, size: 18, color: T.textLight),
                                suffixIcon: _passwordsMatch
                                    ? const Icon(Icons.check_circle, color: T.success, size: 20)
                                    : _passwordsMismatch
                                        ? const Icon(Icons.cancel, color: T.error, size: 20)
                                        : null,
                              ),
                              validator: (v) => v != _password.text ? 'Passwords do not match' : null,
                            ),
                          ),
                          if (_passwordsMismatch)
                            const Padding(
                              padding: EdgeInsets.only(top: 6, left: 2),
                              child: Text('Passwords do not match — please re-enter.',
                                  style: TextStyle(fontSize: 11, color: T.error, fontWeight: FontWeight.w600)),
                            ),
                          const SizedBox(height: 18),

                          // Submit
                          FilledButton(
                            onPressed: canSubmit ? _submit : null,
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
                                      Icon(Icons.person_add_alt_1, size: 18, color: Colors.white),
                                      SizedBox(width: 8),
                                      Text('Create account',
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
                            icon: _GoogleIcon(),
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
                      const Text('Already have an account?',
                          style: TextStyle(fontSize: 13.5, color: T.textMuted)),
                      TextButton(
                        onPressed: () => context.go(Routes.login),
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: const Text('Sign in',
                            style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: T.secondaryDark)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text.rich(
                    TextSpan(
                      style: const TextStyle(fontSize: 11, color: T.textLight, height: 1.5),
                      children: [
                        const TextSpan(text: 'By creating an account you agree to our '),
                        TextSpan(
                            text: 'Terms',
                            style: TextStyle(color: T.textMuted, decoration: TextDecoration.underline, decorationColor: T.border)),
                        const TextSpan(text: ' and '),
                        TextSpan(
                            text: 'Privacy Policy',
                            style: TextStyle(color: T.textMuted, decoration: TextDecoration.underline, decorationColor: T.border)),
                        const TextSpan(text: '.'),
                      ],
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  // Checkbox row (visual only, agreed defaults true)
                  InkWell(
                    onTap: () => setState(() => _agreed = !_agreed),
                    borderRadius: BorderRadius.circular(8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          height: 20, width: 20,
                          child: Checkbox(
                            value: _agreed,
                            onChanged: (v) => setState(() => _agreed = v ?? false),
                            activeColor: T.primary,
                            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            visualDensity: VisualDensity.compact,
                            side: const BorderSide(color: T.border, width: 1.2),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                          ),
                        ),
                        const SizedBox(width: 6),
                        const Text('I agree to the Terms and Privacy Policy',
                            style: TextStyle(fontSize: 12, color: T.textMuted, fontWeight: FontWeight.w500)),
                      ],
                    ),
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

class _FieldLabel extends StatelessWidget {
  final String label;
  final Widget child;
  final bool optional;
  final Widget? trailing;
  const _FieldLabel({required this.label, required this.child, this.optional = false, this.trailing});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
            if (optional)
              const Text('  (optional)',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: T.textLight)),
            const Spacer(),
            if (trailing case final t?) t,
          ],
        ),
        const SizedBox(height: 6),
        child,
      ],
    );
  }
}

class _GoogleIcon extends StatelessWidget {
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
    // Simplified Google “G” using colored arcs - fallback to generic if needed
    // Draw four colored segments roughly
    final paint = Paint()..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round;
    // Use circles approach: draw colored G
    // For simplicity, draw text G with colors - just draw a generic icon
    // We'll draw a simple multicolor G via paths approximation
    paint.color = const Color(0xFF4285F4);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), -0.6, 1.9, false, paint);
    paint.color = const Color(0xFF34A853);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), 1.3, 1.4, false, paint);
    paint.color = const Color(0xFFFBBC05);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), 2.7, 1.2, false, paint);
    paint.color = const Color(0xFFEA4335);
    canvas.drawArc(Rect.fromCircle(center: center, radius: r - 2), 3.9, 1.1, false, paint);
    // inner horizontal
    paint.style = PaintingStyle.fill;
    paint.color = const Color(0xFF4285F4);
    canvas.drawRect(Rect.fromLTWH(center.dx - 1, center.dy - 1, r - 1, 2), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
