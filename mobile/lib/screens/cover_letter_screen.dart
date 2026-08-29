import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../services/api_client.dart';
import '../theme.dart';

class CoverLetterScreen extends StatefulWidget {
  const CoverLetterScreen({super.key});

  @override
  State<CoverLetterScreen> createState() => _CoverLetterScreenState();
}

enum _Result { none, error, letter }

class _CoverLetterScreenState extends State<CoverLetterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _roleCtrl = TextEditingController();
  final _companyCtrl = TextEditingController();
  final _jdCtrl = TextEditingController();
  final _hmCtrl = TextEditingController();

  Map<String, dynamic> _resumeData = {};
  bool _prefilling = true;

  _Result _result = _Result.none;
  String _errorMessage = '';
  Map<String, dynamic> _letter = {};
  String _fullText = '';
  bool _generating = false;

  @override
  void initState() {
    super.initState();
    _loadResumeData();
  }

  @override
  void dispose() {
    _roleCtrl.dispose();
    _companyCtrl.dispose();
    _jdCtrl.dispose();
    _hmCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadResumeData() async {
    try {
      final res = await Api.instance.dio.get('/api/user/latest-analysis');
      if (res.statusCode == 200 && res.data is Map) {
        final data = res.data as Map;
        final analysis = data['analysis'];
        Map<String, dynamic> resume = {};
        if (analysis is Map && analysis['data'] is Map) {
          resume = Map<String, dynamic>.from(analysis['data'] as Map);
        }
        final targetRole = data['target_role']?.toString() ?? '';
        if (!mounted) return;
        setState(() {
          _resumeData = resume;
          if (_roleCtrl.text.isEmpty && targetRole.isNotEmpty) _roleCtrl.text = targetRole;
          _prefilling = false;
        });
        return;
      }
    } catch (_) {}
    if (mounted) setState(() => _prefilling = false);
  }

  Future<void> _generate() async {
    if (!_formKey.currentState!.validate() || _generating) return;
    FocusManager.instance.primaryFocus?.unfocus();
    setState(() => _generating = true);
    try {
      final res = await Api.instance.dio.post('/api/cover-letter/generate', data: {
        'resume_data': _resumeData,
        'target_role': _roleCtrl.text.trim(),
        'company_name': _companyCtrl.text.trim(),
        'job_description': _jdCtrl.text.trim().isEmpty ? null : _jdCtrl.text.trim(),
        'hiring_manager': _hmCtrl.text.trim().isEmpty ? null : _hmCtrl.text.trim(),
      });
      if (!mounted) return;
      if (res.data == null || res.data is! Map) {
        setState(() {
          _result = _Result.error;
          _errorMessage = 'The server returned an unexpected response. Please try again.';
          _generating = false;
        });
        return;
      }
      final data = res.data as Map;
      if (data['error'] == true) {
        setState(() {
          _result = _Result.error;
          _errorMessage = data['message']?.toString() ?? 'Could not generate the cover letter.';
          _generating = false;
        });
        return;
      }
      final text = data['full_text']?.toString() ?? '';
      setState(() {
        _letter = Map<String, dynamic>.from(data);
        _fullText = text;
        _result = _Result.letter;
        _generating = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _result = _Result.error;
        _errorMessage = Api.errorMessage(e);
        _generating = false;
      });
    }
  }

  Future<void> _copyLetter() async {
    await Clipboard.setData(ClipboardData(text: _fullText));
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cover letter copied to clipboard.')));
  }

  void _editAgain() => setState(() => _result = _Result.none);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          Positioned(top: -120, right: -100, child: Container(width: 360, height: 360, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.primary.withValues(alpha: 0.06), Colors.transparent])))),
          Positioned(bottom: -140, left: -140, child: Container(width: 380, height: 380, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.secondary.withValues(alpha: 0.05), Colors.transparent])))),
          SafeArea(child: switch (_result) {
            _Result.none => _buildForm(),
            _Result.error => _buildError(),
            _Result.letter => _buildLetter(),
          }),
        ],
      ),
    );
  }

  Widget _buildForm() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Column(
            children: [
              Container(
                height: 64, width: 64,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(18), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                child: ClipRRect(borderRadius: BorderRadius.circular(10), child: Image.asset('assets/icon.png', fit: BoxFit.contain)),
              ),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                decoration: BoxDecoration(color: T.navy100.withValues(alpha: 0.6), borderRadius: BorderRadius.circular(100), border: Border.all(color: T.navy100)),
                child: const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.mail_outline, size: 11, color: T.primary), SizedBox(width: 6), Text('AI COVER LETTER • PERSONALIZED', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.08 * 11, color: T.primary))]),
              ),
              const SizedBox(height: 12),
              Text('Craft Your Cover Letter', textAlign: TextAlign.center, style: displayStyle(context, 26)),
              const SizedBox(height: 8),
              const Text('Tailored to your resume and target role — paste a JD for extra precision.', textAlign: TextAlign.center, style: TextStyle(fontSize: 14, height: 1.55, color: T.textMuted)),
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
                decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                child: Form(
                  key: _formKey,
                  autovalidateMode: AutovalidateMode.onUserInteraction,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (_prefilling) ...[
                        const LinearProgressIndicator(minHeight: 2, color: T.secondary, backgroundColor: T.borderLight),
                        const SizedBox(height: 14),
                      ],
                      _FieldLabel(
                        label: 'Target role',
                        required: true,
                        child: TextFormField(
                          controller: _roleCtrl,
                          decoration: const InputDecoration(hintText: 'e.g. Data Scientist', prefixIcon: Icon(Icons.work_outline, size: 18, color: T.textLight)),
                          validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null,
                        ),
                      ),
                      const SizedBox(height: 14),
                      _FieldLabel(
                        label: 'Company name',
                        required: true,
                        child: TextFormField(
                          controller: _companyCtrl,
                          decoration: const InputDecoration(hintText: 'e.g. Acme Inc.', prefixIcon: Icon(Icons.business_outlined, size: 18, color: T.textLight)),
                          validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null,
                        ),
                      ),
                      const SizedBox(height: 14),
                      _FieldLabel(
                        label: 'Job description',
                        optional: true,
                        child: TextFormField(
                          controller: _jdCtrl,
                          minLines: 4,
                          maxLines: 7,
                          decoration: const InputDecoration(hintText: 'Paste the JD to tailor the letter (optional)', alignLabelWithHint: true, prefixIcon: Icon(Icons.description_outlined, size: 18, color: T.textLight)),
                        ),
                      ),
                      const SizedBox(height: 14),
                      _FieldLabel(
                        label: 'Hiring manager',
                        optional: true,
                        child: TextFormField(
                          controller: _hmCtrl,
                          decoration: const InputDecoration(hintText: 'e.g. Jane Doe (optional)', prefixIcon: Icon(Icons.person_outline, size: 18, color: T.textLight)),
                        ),
                      ),
                      const SizedBox(height: 18),
                      FilledButton.icon(
                        onPressed: _generating ? null : _generate,
                        icon: _generating ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.auto_awesome, size: 18, color: Colors.white),
                        label: Text(_generating ? 'Generating…' : _resumeData.isEmpty ? 'Generate cover letter' : 'Generate from my resume', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                        style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48), backgroundColor: T.primary, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg))),
                      ),
                      if (_resumeData.isEmpty && !_prefilling)
                        Padding(
                          padding: const EdgeInsets.only(top: 10),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.info_outline, size: 12, color: T.textLight),
                              const SizedBox(width: 6),
                              Flexible(child: Text('No analyzed resume found — fields will be filled manually.', textAlign: TextAlign.center, style: TextStyle(fontSize: 11.5, color: T.textLight, fontWeight: FontWeight.w500))),
                            ],
                          ),
                        ),
                      if (_resumeData.isNotEmpty) ...[
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                          decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(10), border: Border.all(color: const Color(0xFFBBF7D0))),
                          child: const Row(children: [Icon(Icons.check_circle, size: 14, color: T.success), SizedBox(width: 6), Expanded(child: Text('Using your latest analyzed resume', style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w700, color: Color(0xFF166534))))]),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Container(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
            decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(height: 56, width: 56, decoration: const BoxDecoration(color: T.errorLight, shape: BoxShape.circle), child: const Icon(Icons.warning_amber_rounded, size: 28, color: T.error)),
                const SizedBox(height: 12),
                const Text('Something went wrong', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: T.text)),
                const SizedBox(height: 10),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(color: T.errorLight, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: const Color(0xFFFECACA))),
                  child: SelectableText(_errorMessage, style: const TextStyle(fontSize: 13, height: 1.5, color: Color(0xFF991B1B))),
                ),
                const SizedBox(height: 16),
                FilledButton.icon(onPressed: _editAgain, icon: const Icon(Icons.arrow_back, size: 18, color: Colors.white), label: const Text('Back to form', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)), style: FilledButton.styleFrom(backgroundColor: T.primary, minimumSize: const Size.fromHeight(46), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)))),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLetter() {
    final company = _companyCtrl.text.trim();
    final role = _roleCtrl.text.trim();
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      children: [
        // top actions bar
        Container(
          padding: const EdgeInsets.fromLTRB(14, 10, 14, 10),
          decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
          child: Row(
            children: [
              Container(
                height: 32, width: 32,
                decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
                child: const Icon(Icons.check_circle, size: 16, color: T.success),
              ),
              const SizedBox(width: 10),
              const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Ready to send', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: T.text)), Text('Copy and paste into your application', style: TextStyle(fontSize: 11, color: T.textMuted, fontWeight: FontWeight.w600))])),
              FilledButton.icon(onPressed: _copyLetter, icon: const Icon(Icons.copy_rounded, size: 16, color: Colors.white), label: const Text('Copy', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)), style: FilledButton.styleFrom(backgroundColor: T.primary, padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8), minimumSize: Size.zero, tapTargetSize: MaterialTapTargetSize.shrinkWrap, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)))),
            ],
          ),
        ),
        const SizedBox(height: 14),
        // paper
        Container(
          decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 14),
                decoration: BoxDecoration(color: T.bg.withValues(alpha: 0.6), borderRadius: const BorderRadius.vertical(top: Radius.circular(16)), border: Border(bottom: BorderSide(color: T.borderLight))),
                child: Row(
                  children: [
                    Container(height: 36, width: 36, padding: const EdgeInsets.all(6), decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(10), border: Border.all(color: T.borderLight)), child: ClipRRect(borderRadius: BorderRadius.circular(6), child: Image.asset('assets/icon.png', fit: BoxFit.contain))),
                    const SizedBox(width: 10),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(company.isNotEmpty ? company : 'Your Cover Letter', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: T.text)),
                      Text(role.isNotEmpty ? role : 'Application', style: const TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w600)),
                    ])),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(100), border: Border.all(color: const Color(0xFFDBEAFE))),
                      child: const Text('AI Generated', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.06 * 10, color: Color(0xFF1D4ED8))),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 18, 20, 22),
                child: SelectableText(_fullText.isNotEmpty ? _fullText : _letter.toString(), style: const TextStyle(fontSize: 13.5, height: 1.65, color: T.text)),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(onPressed: _copyLetter, icon: const Icon(Icons.copy_rounded, size: 18, color: Colors.white), label: const Text('Copy to clipboard', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)), style: FilledButton.styleFrom(backgroundColor: T.primary, minimumSize: const Size.fromHeight(48), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)))),
        const SizedBox(height: 10),
        OutlinedButton.icon(onPressed: _editAgain, icon: const Icon(Icons.edit_outlined, size: 16), label: const Text('Edit details & regenerate'), style: OutlinedButton.styleFrom(minimumSize: const Size.fromHeight(48), side: const BorderSide(color: T.border), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)))),
      ],
    );
  }
}

class _FieldLabel extends StatelessWidget {
  final String label;
  final bool required;
  final bool optional;
  final Widget child;
  const _FieldLabel({required this.label, required this.child, this.required = false, this.optional = false});
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
          if (required) const Text(' *', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: T.error)),
          if (optional) const Text('  (optional)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: T.textLight)),
        ]),
        const SizedBox(height: 6),
        child,
      ],
    );
  }
}
