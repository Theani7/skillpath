import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../router.dart';
import '../../services/auth_service.dart';

final _emailPattern = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _otp = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();

  int _step = 0; // 0 = email, 1 = otp, 2 = new password
  bool _busy = false;
  String? _error;
  String? _resetToken;

  @override
  void dispose() {
    _email.dispose();
    _otp.dispose();
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  Future<void> _requestReset() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    final error = await AuthService.requestPasswordReset(_email.text.trim());
    if (!mounted) return;
    if (error == null) {
      setState(() {
        _busy = false;
        _step = 1;
      });
      return;
    }
    setState(() {
      _busy = false;
      _error = error;
    });
  }

  Future<void> _verifyOtp() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    final (error, token) = await AuthService.verifyResetOtp(
      _email.text.trim(),
      _otp.text.trim(),
    );
    if (!mounted) return;
    if (token != null) {
      setState(() {
        _busy = false;
        _resetToken = token;
        _step = 2;
      });
      return;
    }
    setState(() {
      _busy = false;
      _error = error ?? 'Invalid code';
    });
  }

  Future<void> _setNewPassword() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    final error = await AuthService.resetPassword(_resetToken!, _password.text);
    if (!mounted) return;
    if (error == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Password updated. You can sign in.')),
      );
      context.go(Routes.login);
      return;
    }
    setState(() {
      _busy = false;
      _error = error;
    });
  }

  String get _title => switch (_step) {
    0 => 'Reset password',
    1 => 'Enter code',
    _ => 'Choose a new password',
  };

  String get _subtitle => switch (_step) {
    0 => "We'll email you a 6-digit code.",
    1 => 'Code sent to ${_email.text.trim()}',
    _ => 'At least 8 characters.',
  };

  Future<void> Function() get _advance => switch (_step) {
    0 => _requestReset,
    1 => _verifyOtp,
    _ => _setNewPassword,
  };

  List<Widget> _steps() => [
    TextFormField(
      controller: _email,
      keyboardType: TextInputType.emailAddress,
      enabled: _step == 0,
      decoration: const InputDecoration(
        labelText: 'Email',
        prefixIcon: Icon(Icons.mail_outline),
      ),
      textInputAction: TextInputAction.done,
      onFieldSubmitted: (_) => _advance(),
      validator: (v) => !_emailPattern.hasMatch(v?.trim() ?? '')
          ? 'Enter a valid email'
          : null,
    ),
    if (_step >= 1) ...[
      const SizedBox(height: 16),
      TextFormField(
        controller: _otp,
        keyboardType: TextInputType.number,
        maxLength: 6,
        enabled: _step == 1,
        textAlign: TextAlign.center,
        style: Theme.of(context).textTheme.headlineSmall,
        decoration: const InputDecoration(
          labelText: '6-digit code',
          counterText: '',
        ),
        autofocus: _step == 1,
        textInputAction: TextInputAction.done,
        onFieldSubmitted: (_) => _advance(),
        validator: (v) => RegExp(r'^\d{6}$').hasMatch(v ?? '')
            ? null
            : 'Enter the 6-digit code',
      ),
    ],
    if (_step >= 2) ...[
      const SizedBox(height: 16),
      TextFormField(
        controller: _password,
        obscureText: true,
        enabled: _step == 2,
        decoration: const InputDecoration(
          labelText: 'New password',
          prefixIcon: Icon(Icons.lock_outline),
        ),
        autofillHints: const [AutofillHints.newPassword],
        textInputAction: TextInputAction.next,
        validator: (v) =>
            (v == null || v.length < 8) ? 'At least 8 characters' : null,
      ),
      const SizedBox(height: 16),
      TextFormField(
        controller: _confirm,
        obscureText: true,
        enabled: _step == 2,
        decoration: const InputDecoration(
          labelText: 'Confirm new password',
          prefixIcon: Icon(Icons.lock_outline),
        ),
        autofillHints: const [AutofillHints.newPassword],
        onFieldSubmitted: (_) => _advance(),
        validator: (v) => v != _password.text ? 'Passwords do not match' : null,
      ),
    ],
  ];

  @override
  Widget build(BuildContext context) {
    final actionLabel = switch (_step) {
      0 => 'Send code',
      1 => 'Verify code',
      _ => 'Update password',
    };
    return Scaffold(
      appBar: AppBar(title: Text(_title)),
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
                    Text(_subtitle, textAlign: TextAlign.center),
                    const SizedBox(height: 24),
                    ..._steps(),
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
                      onPressed: _busy ? null : _advance,
                      child: _busy
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : Text(actionLabel),
                    ),
                    if (_step == 0)
                      TextButton(
                        onPressed: () => context.go(Routes.login),
                        child: const Text('Back to log in'),
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
