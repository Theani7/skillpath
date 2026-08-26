import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../router.dart';
import '../../services/auth_service.dart';

/// Enter the 6-digit code emailed to you. `purpose` is either `register`
/// or `password_reset` (backend contract).
class OtpScreen extends StatefulWidget {
  final String email;
  final String purpose;

  /// Dev hint surfaced when the backend SMTP is unconfigured and the
  /// register response contains `debug_otp`. Cleared once displayed.
  static String? devHint;

  const OtpScreen({super.key, required this.email, this.purpose = 'register'});

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  final _otp = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _verifying = false;
  bool _resending = false;
  String? _error;
  String? _devHint;
  Timer? _cooldownTimer;
  int _cooldown = 0;

  bool get _isRegister => widget.purpose == 'register';

  @override
  void initState() {
    super.initState();
    _devHint = _isRegister ? OtpScreen.devHint : null;
    OtpScreen.devHint = null;
  }

  @override
  void dispose() {
    _cooldownTimer?.cancel();
    _otp.dispose();
    super.dispose();
  }

  void _startCooldown() {
    _cooldownTimer?.cancel();
    setState(() => _cooldown = 30);
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) return t.cancel();
      setState(() => _cooldown--);
      if (_cooldown <= 0) t.cancel();
    });
  }

  Future<void> _verify() async {
    if (!_formKey.currentState!.validate()) return;
    if (!_isRegister) {
      setState(
        () =>
            _error = 'Continue in the password-reset flow to verify this code.',
      );
      return;
    }
    setState(() {
      _verifying = true;
      _error = null;
    });
    final error = await AuthService.verifyEmail(widget.email, _otp.text.trim());
    if (!mounted) return;
    if (error == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Email verified. You can sign in.')),
      );
      context.go(Routes.login);
      return;
    }
    setState(() {
      _verifying = false;
      _error = error;
    });
  }

  Future<void> _resend() async {
    setState(() => _resending = true);
    final error = await AuthService.resendOtp(
      widget.email,
      purpose: widget.purpose,
    );
    if (!mounted) return;
    setState(() => _resending = false);
    _startCooldown();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(error ?? 'Code sent to ${widget.email}')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Verify email')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'We sent a 6-digit code to',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.email.isEmpty ? '(no email)' : widget.email,
                      style: Theme.of(context).textTheme.titleMedium,
                      textAlign: TextAlign.center,
                    ),
                    if (_devHint != null) ...[
                      const SizedBox(height: 12),
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Text(
                            'Dev mode (SMTP unconfigured): your code is $_devHint',
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ),
                    ],
                    const SizedBox(height: 24),
                    TextFormField(
                      controller: _otp,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.headlineSmall,
                      decoration: const InputDecoration(
                        labelText: '6-digit code',
                        counterText: '',
                      ),
                      autofocus: true,
                      onFieldSubmitted: (_) => _verify(),
                      validator: (v) => RegExp(r'^\d{6}$').hasMatch(v ?? '')
                          ? null
                          : 'Enter the 6-digit code',
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        _error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                    const SizedBox(height: 24),
                    FilledButton(
                      onPressed: _verifying ? null : _verify,
                      child: _verifying
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Verify'),
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: (_resending || _cooldown > 0) ? null : _resend,
                      child: Text(
                        _resending
                            ? 'Sending…'
                            : _cooldown > 0
                            ? 'Resend code (${_cooldown}s)'
                            : 'Resend code',
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
