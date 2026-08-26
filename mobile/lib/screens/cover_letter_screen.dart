import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../services/api_client.dart';

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

  /// Best-effort prefill from the user's latest analysis. If it fails,
  /// the form stays empty and resume_data is sent as {}.
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
          if (_roleCtrl.text.isEmpty && targetRole.isNotEmpty) {
            _roleCtrl.text = targetRole;
          }
          _prefilling = false;
        });
        return;
      }
    } catch (_) {
      /* fall through to manual entry */
    }
    if (mounted) setState(() => _prefilling = false);
  }

  Future<void> _generate() async {
    if (!_formKey.currentState!.validate() || _generating) return;
    FocusManager.instance.primaryFocus?.unfocus();
    setState(() => _generating = true);
    try {
      final res = await Api.instance.dio.post(
        '/api/cover-letter/generate',
        data: {
          'resume_data': _resumeData,
          'target_role': _roleCtrl.text.trim(),
          'company_name': _companyCtrl.text.trim(),
          'job_description': _jdCtrl.text.trim().isEmpty
              ? null
              : _jdCtrl.text.trim(),
          'hiring_manager': _hmCtrl.text.trim().isEmpty
              ? null
              : _hmCtrl.text.trim(),
        },
      );
      if (!mounted) return;
      if (res.data == null || res.data is! Map) {
        setState(() {
          _result = _Result.error;
          _errorMessage =
              'The server returned an unexpected response. Please try again.';
          _generating = false;
        });
        return;
      }
      final data = res.data as Map;
      if (data['error'] == true) {
        setState(() {
          _result = _Result.error;
          _errorMessage =
              data['message']?.toString() ??
              'Could not generate the cover letter.';
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
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Cover letter copied to clipboard.')),
    );
  }

  void _editAgain() {
    setState(() => _result = _Result.none);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cover Letter'),
        actions: [
          if (_result == _Result.letter)
            IconButton(
              tooltip: 'Copy',
              icon: const Icon(Icons.copy_rounded),
              onPressed: _copyLetter,
            ),
        ],
      ),
      body: switch (_result) {
        _Result.none => _buildForm(),
        _Result.error => _buildError(),
        _Result.letter => _buildLetter(),
      },
    );
  }

  Widget _buildForm() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Form(
          key: _formKey,
          autovalidateMode: AutovalidateMode.onUserInteraction,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (_prefilling)
                const Padding(
                  padding: EdgeInsets.only(bottom: 12),
                  child: LinearProgressIndicator(minHeight: 2),
                ),
              TextFormField(
                controller: _roleCtrl,
                decoration: const InputDecoration(
                  labelText: 'Target role *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.work_outline),
                ),
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _companyCtrl,
                decoration: const InputDecoration(
                  labelText: 'Company name *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.business_outlined),
                ),
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _jdCtrl,
                minLines: 4,
                maxLines: 8,
                decoration: const InputDecoration(
                  labelText: 'Job description (optional)',
                  alignLabelWithHint: true,
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.description_outlined),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _hmCtrl,
                decoration: const InputDecoration(
                  labelText: 'Hiring manager (optional)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person_outline),
                ),
              ),
              const SizedBox(height: 20),
              FilledButton.icon(
                onPressed: _generating ? null : _generate,
                icon: _generating
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.auto_awesome),
                label: Text(
                  _generating
                      ? 'Generating…'
                      : _resumeData.isEmpty
                      ? 'Generate cover letter'
                      : 'Generate from my resume',
                ),
              ),
              if (_resumeData.isEmpty && !_prefilling)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    'No analyzed resume found — fields will be filled manually.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildError() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.warning_amber_rounded,
              size: 48,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Card(
              color: Theme.of(context).colorScheme.errorContainer,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: SelectableText(
                  _errorMessage,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onErrorContainer,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: _editAgain,
              icon: const Icon(Icons.arrow_back),
              label: const Text('Back to form'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLetter() {
    final theme = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          clipBehavior: Clip.antiAlias,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.mail_outline,
                      size: 18,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Your cover letter',
                        style: theme.textTheme.titleMedium,
                      ),
                    ),
                  ],
                ),
                const Divider(height: 24),
                SelectableText(
                  _fullText.isNotEmpty
                      ? _fullText
                      : _letter.toString(), // fallback for odd payloads
                  style: theme.textTheme.bodyLarge?.copyWith(height: 1.5),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: _copyLetter,
          icon: const Icon(Icons.copy_rounded),
          label: const Text('Copy to clipboard'),
        ),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: _editAgain,
          icon: const Icon(Icons.edit_outlined),
          label: const Text('Edit details & regenerate'),
        ),
        const SizedBox(height: 16),
      ],
    );
  }
}
