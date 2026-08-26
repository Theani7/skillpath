import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../router.dart';
import '../../services/api_client.dart';
import '../../services/auth_service.dart';
import 'otp_screen.dart';

final _usernamePattern = RegExp(r'^[A-Za-z0-9_.-]{3,50}$');
final _emailPattern = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

enum _UsernameState { idle, checking, available, taken }

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _fullName = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  Timer? _debounce;
  bool _submitting = false;
  _UsernameState _usernameState = _UsernameState.idle;
  String? _error;

  @override
  void dispose() {
    _debounce?.cancel();
    _username.dispose();
    _fullName.dispose();
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
          height: 18,
          width: 18,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      case _UsernameState.available:
        return const Icon(Icons.check_circle_outline, color: Colors.green);
      case _UsernameState.taken:
        return const Icon(Icons.error_outline, color: Colors.red);
      case _UsernameState.idle:
        return null;
    }
  }

  String? get _usernameHelper {
    switch (_usernameState) {
      case _UsernameState.available:
        return 'Username is available';
      case _UsernameState.taken:
        return 'Username is already taken';
      default:
        return null;
    }
  }

  /// POST /api/auth/register directly so we can surface `debug_otp`
  /// when the backend SMTP is unconfigured (AuthService.register drops it).
  Future<Response> _registerRaw() => Api.instance.dio.post(
    '/api/auth/register',
    data: {
      'username': _username.text.trim(),
      'email': _email.text.trim(),
      'password': _password.text,
      'full_name': _fullName.text.trim(),
    },
  );

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
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
    return Scaffold(
      appBar: AppBar(title: const Text('Create account')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Form(
                key: _formKey,
                autovalidateMode: AutovalidateMode.onUserInteraction,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextFormField(
                      controller: _username,
                      decoration: InputDecoration(
                        labelText: 'Username',
                        prefixIcon: const Icon(Icons.alternate_email),
                        suffixIcon: _usernameSuffix,
                        helperText: _usernameHelper,
                      ),
                      onChanged: _onUsernameChanged,
                      textInputAction: TextInputAction.next,
                      autofillHints: const [AutofillHints.newUsername],
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
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _fullName,
                      decoration: const InputDecoration(
                        labelText: 'Full name',
                        prefixIcon: Icon(Icons.badge_outlined),
                      ),
                      textInputAction: TextInputAction.next,
                      autofillHints: const [AutofillHints.name],
                      validator: (v) =>
                          (v == null || v.trim().isEmpty) ? 'Required' : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _email,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        prefixIcon: Icon(Icons.mail_outline),
                      ),
                      textInputAction: TextInputAction.next,
                      autofillHints: const [AutofillHints.email],
                      validator: (v) => !_emailPattern.hasMatch(v?.trim() ?? '')
                          ? 'Enter a valid email'
                          : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _password,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Password',
                        prefixIcon: Icon(Icons.lock_outline),
                      ),
                      textInputAction: TextInputAction.next,
                      autofillHints: const [AutofillHints.newPassword],
                      validator: (v) => (v == null || v.length < 8)
                          ? 'At least 8 characters'
                          : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _confirm,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Confirm password',
                        prefixIcon: Icon(Icons.lock_outline),
                      ),
                      autofillHints: const [AutofillHints.newPassword],
                      validator: (v) =>
                          v != _password.text ? 'Passwords do not match' : null,
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
                      onPressed: _submitting ? null : _submit,
                      child: _submitting
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Create Account'),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text('Already have an account?'),
                        TextButton(
                          onPressed: () => context.go(Routes.login),
                          child: const Text('Log In'),
                        ),
                      ],
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
