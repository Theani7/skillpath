import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../services/api_client.dart';
import '../theme.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullName = TextEditingController();
  final _phone = TextEditingController();
  final _location = TextEditingController();
  final _bio = TextEditingController();
  final _role = TextEditingController();
  final _exp = TextEditingController();
  final _linkedin = TextEditingController();
  final _github = TextEditingController();

  bool _loading = true;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _fullName.dispose();
    _phone.dispose();
    _location.dispose();
    _bio.dispose();
    _role.dispose();
    _exp.dispose();
    _linkedin.dispose();
    _github.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final res = await Api.instance.dio.get('/api/user/profile');
      final p = (res.data is Map ? (res.data as Map)['profile'] : null) as Map?;
      if (p != null) {
        _fullName.text = p['full_name']?.toString() ?? '';
        _phone.text = p['phone']?.toString() ?? '';
        _location.text = p['location']?.toString() ?? '';
        _bio.text = p['bio']?.toString() ?? '';
        _role.text = p['current_role']?.toString() ?? p['current_job_role']?.toString() ?? '';
        _exp.text = p['experience_years']?.toString() ?? '';
        _linkedin.text = p['linkedin_url']?.toString() ?? '';
        _github.text = p['github_url']?.toString() ?? '';
      }
    } catch (e) {
      _error = Api.errorMessage(e);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _saving = true; _error = null; });
    try {
      final res = await Api.instance.dio.put('/api/user/profile', data: {
        'full_name': _fullName.text.trim(),
        'phone': _phone.text.trim(),
        'location': _location.text.trim(),
        'bio': _bio.text.trim(),
        'current_role': _role.text.trim(),
        'experience_years': _exp.text.trim(),
        'linkedin_url': _linkedin.text.trim(),
        'github_url': _github.text.trim(),
      });
      if (!mounted) return;
      if (res.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Profile updated')));
        context.pop(true);
      } else {
        setState(() => _error = (res.data is Map ? (res.data as Map)['detail']?.toString() : null) ?? 'Failed to update');
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = Api.errorMessage(e));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      appBar: AppBar(title: const Text('Edit Profile'), backgroundColor: T.bg, elevation: 0, leading: IconButton(icon: const Icon(Icons.close), onPressed: () => context.pop())),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: T.secondary))
          : SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 520),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                        child: Column(children: [
                          if (_error != null) ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(color: T.errorLight, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: const Color(0xFFFECACA))),
                              child: Row(children: [const Icon(Icons.error_outline, size: 16, color: T.error), const SizedBox(width: 8), Expanded(child: Text(_error!, style: const TextStyle(fontSize: 12, color: T.error)))]),
                            ),
                            const SizedBox(height: 14),
                          ],
                          _field(label: 'Full name', ctrl: _fullName, icon: Icons.person_outline, hint: 'Jane Doe', validator: (v) => null),
                          const SizedBox(height: 12),
                          _field(label: 'Current role', ctrl: _role, icon: Icons.work_outline, hint: 'Data Scientist'),
                          const SizedBox(height: 12),
                          Row(children: [
                            Expanded(child: _field(label: 'Phone', ctrl: _phone, icon: Icons.phone_outlined, hint: '+1 555...', keyboard: TextInputType.phone)),
                            const SizedBox(width: 12),
                            Expanded(child: _field(label: 'Experience (yrs)', ctrl: _exp, icon: Icons.timeline_outlined, hint: '2.5', keyboard: TextInputType.number, validator: (v) { if (v != null && v.isNotEmpty && double.tryParse(v) == null) return 'Number'; return null; })),
                          ]),
                          const SizedBox(height: 12),
                          _field(label: 'Location', ctrl: _location, icon: Icons.location_on_outlined, hint: 'Bangalore, IN'),
                          const SizedBox(height: 12),
                          _field(label: 'Bio', ctrl: _bio, icon: Icons.notes_outlined, hint: 'Short bio (500 chars)', maxLines: 3),
                          const SizedBox(height: 12),
                          _field(label: 'LinkedIn', ctrl: _linkedin, icon: Icons.link, hint: 'https://linkedin.com/in/...', validator: (v) { if (v != null && v.isNotEmpty && !v.contains('linkedin.com')) return 'Must be linkedin.com'; return null; }),
                          const SizedBox(height: 12),
                          _field(label: 'GitHub', ctrl: _github, icon: Icons.code, hint: 'https://github.com/...', validator: (v) { if (v != null && v.isNotEmpty && !v.contains('github.com')) return 'Must be github.com'; return null; }),
                        ]),
                      ),
                      const SizedBox(height: 16),
                      FilledButton.icon(onPressed: _saving ? null : _save, icon: _saving ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.check, size: 18, color: Colors.white), label: Text(_saving ? 'Saving…' : 'Save changes', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)), style: FilledButton.styleFrom(backgroundColor: T.primary, minimumSize: const Size.fromHeight(48), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)))),
                    ],
                  ),
                ),
              ),
            ),
    );
  }

  Widget _field({required String label, required TextEditingController ctrl, required IconData icon, String? hint, TextInputType? keyboard, int maxLines = 1, String? Function(String?)? validator}) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
      const SizedBox(height: 6),
      TextFormField(controller: ctrl, keyboardType: keyboard, maxLines: maxLines, validator: validator, decoration: InputDecoration(hintText: hint, prefixIcon: Icon(icon, size: 18, color: T.textLight))),
    ]);
  }
}
