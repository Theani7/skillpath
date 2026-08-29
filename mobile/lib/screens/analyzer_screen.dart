import 'dart:io';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../router.dart';
import '../services/api_client.dart';
import '../theme.dart';
import '../widgets/shimmer.dart';

const _fallbackRoles = [
  'General',
  'Software Engineer',
  'Data Scientist',
  'Web Developer',
  'Product Manager',
];

const _maxUploadBytes = 5 * 1024 * 1024; // 5 MB

class AnalyzerScreen extends StatefulWidget {
  const AnalyzerScreen({super.key});

  @override
  State<AnalyzerScreen> createState() => _AnalyzerScreenState();
}

class _AnalyzerScreenState extends State<AnalyzerScreen> {
  List<String> _roles = List.of(_fallbackRoles);
  String? _selectedRole;
  bool _loadingRoles = true;
  bool _uploading = false;
  String? _inlineError;

  PlatformFile? _file;
  int? _fileSize;

  @override
  void initState() {
    super.initState();
    _loadRoles();
  }

  Future<void> _loadRoles() async {
    try {
      final res = await Api.instance.dio.get('/api/job-roles');
      final raw = res.data is Map ? (res.data as Map)['roles'] : null;
      final roles = (raw as List?)?.map((r) => r.toString()).where((r) => r.isNotEmpty).toList() ?? const <String>[];
      if (!mounted) return;
      setState(() {
        _roles = roles.isNotEmpty ? roles : List.of(_fallbackRoles);
        if (!_roles.contains(_selectedRole)) _selectedRole = _roles.first;
        _loadingRoles = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _roles = List.of(_fallbackRoles);
        if (!_roles.contains(_selectedRole)) _selectedRole = _roles.first;
        _loadingRoles = false;
      });
    }
  }

  Future<void> _pickFile() async {
    try {
      final picked = await FilePicker.pickFile(
        type: FileType.custom,
        allowedExtensions: const ['pdf', 'docx'],
      );
      if (picked == null) return;
      final size = await picked.length();
      if (!mounted) return;
      setState(() {
        _file = picked;
        _fileSize = size;
        _inlineError = null;
      });
      if (size > _maxUploadBytes) {
        setState(() => _inlineError = 'File exceeds the 5 MB limit.');
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _inlineError = Api.errorMessage(e));
    }
  }

  String? get _fileError {
    if (_file == null) return null;
    if (_fileSize == null || _fileSize! > _maxUploadBytes) return 'File exceeds the 5 MB limit.';
    return null;
  }

  String _fileSizeLabel(int bytes) {
    if (bytes >= 1024 * 1024) return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    return '${(bytes / 1024).toStringAsFixed(0)} KB';
  }

  Future<void> _analyze() async {
    final file = _file;
    final role = _selectedRole ?? _roles.first;
    final error = _fileError;
    if (file == null || error != null || _uploading) return;
    Uint8List bytes;
    try {
      bytes = await _readBytes(file);
    } catch (e) {
      if (!mounted) return;
      setState(() => _inlineError = Api.errorMessage(e));
      return;
    }
    if (!mounted) return;
    setState(() {
      _uploading = true;
      _inlineError = null;
    });
    try {
      final form = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: file.name),
        'target_role': role,
      });
      final res = await Api.instance.dio.post('/api/analyze', data: form);
      final data = res.data;
      if (!mounted) return;
      if (data is Map && data['error'] == true) {
        setState(() => _inlineError = data['message']?.toString() ?? 'Analysis failed.');
        return;
      }
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Analysis complete')));
      context.go(Routes.result);
    } catch (e) {
      if (!mounted) return;
      setState(() => _inlineError = Api.errorMessage(e));
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Future<Uint8List> _readBytes(PlatformFile file) async {
    final path = file.path;
    if (path != null) return File(path).readAsBytes();
    return file.readAsBytes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          // soft glows like web
          Positioned(
            top: -120, right: -120,
            child: Container(
              width: 360, height: 360,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [T.primary.withValues(alpha: 0.06), Colors.transparent],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: -140, left: -140,
            child: Container(
              width: 380, height: 380,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [T.secondary.withValues(alpha: 0.05), Colors.transparent],
                ),
              ),
            ),
          ),
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 720),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: 8),
                      _Header(loadingRoles: _loadingRoles),
                      const SizedBox(height: 18),
                      const _StepsIndicator(),
                      const SizedBox(height: 20),
                      // Card
                      Container(
                        clipBehavior: Clip.antiAlias,
                        decoration: BoxDecoration(
                          color: T.surface,
                          borderRadius: BorderRadius.circular(T.radiusXl),
                          border: Border.all(color: T.borderLight),
                          boxShadow: T.cardShadow,
                        ),
                        child: Column(
                          children: [
                            if (_uploading)
                              const LinearProgressIndicator(minHeight: 2, color: T.secondary, backgroundColor: T.borderLight),
                            Padding(
                              padding: const EdgeInsets.fromLTRB(20, 22, 20, 22),
                              child: _uploading
                                  ? _AnalyzingState(role: _selectedRole ?? _roles.first)
                                  : Column(
                                      crossAxisAlignment: CrossAxisAlignment.stretch,
                                      children: [
                                        // Target role
                                        const Text('Target role',
                                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
                                        const SizedBox(height: 8),
                                        if (_loadingRoles)
                                          const AdvancedShimmer(child: SkeletonBlock(height: 46, width: double.infinity, radius: 12))
                                        else
                                          DropdownButtonFormField<String>(
                                            initialValue: _selectedRole,
                                            decoration: const InputDecoration(
                                              prefixIcon: Icon(Icons.work_outline, size: 18, color: T.textLight),
                                            ),
                                            items: [for (final r in _roles) DropdownMenuItem(value: r, child: Text(r, overflow: TextOverflow.ellipsis))],
                                            onChanged: (v) => setState(() => _selectedRole = v),
                                            borderRadius: BorderRadius.circular(T.radiusLg),
                                            isExpanded: true,
                                          ),
                                        const SizedBox(height: 18),
                                        // Drop zone
                                        _DropZone(
                                          fileName: _file?.name,
                                          fileSize: _fileSize,
                                          fileSizeLabel: _fileSize != null ? _fileSizeLabel(_fileSize!) : null,
                                          hasFile: _file != null,
                                          error: _fileError,
                                          onBrowse: _pickFile,
                                          onRemove: () => setState(() {
                                            _file = null;
                                            _fileSize = null;
                                            _inlineError = null;
                                          }),
                                        ),
                                        if (_fileError != null)
                                          Padding(
                                            padding: const EdgeInsets.only(top: 8),
                                            child: Text(_fileError!, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: T.error)),
                                          ),
                                        if (_inlineError != null && _fileError == null)
                                          Container(
                                            margin: const EdgeInsets.only(top: 12),
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                            decoration: BoxDecoration(
                                              color: T.errorLight,
                                              borderRadius: BorderRadius.circular(T.radiusLg),
                                              border: Border.all(color: const Color(0xFFFECACA)),
                                            ),
                                            child: Row(
                                              children: [
                                                const Icon(Icons.error_outline, size: 16, color: T.error),
                                                const SizedBox(width: 8),
                                                Expanded(child: Text(_inlineError!, style: const TextStyle(fontSize: 13, color: T.error, fontWeight: FontWeight.w600))),
                                              ],
                                            ),
                                          ),
                                        const SizedBox(height: 18),
                                        FilledButton.icon(
                                          onPressed: (_file != null && _selectedRole != null && !_loadingRoles && _fileError == null) ? _analyze : null,
                                          icon: const Icon(Icons.bolt, size: 18, color: Colors.white),
                                          label: const Text('Analyze My Resume', style: TextStyle(fontWeight: FontWeight.w700, color: Colors.white)),
                                          style: FilledButton.styleFrom(
                                            minimumSize: const Size.fromHeight(46),
                                            backgroundColor: T.primary,
                                            foregroundColor: Colors.white,
                                            disabledBackgroundColor: T.border,
                                            disabledForegroundColor: T.textLight,
                                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(T.radiusLg)),
                                          ),
                                        ),
                                        const SizedBox(height: 12),
                                        const Row(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Icon(Icons.schedule, size: 11, color: T.textLight),
                                            SizedBox(width: 6),
                                            Text('Analysis usually takes 5–10 seconds',
                                                style: TextStyle(fontSize: 11.5, color: T.textLight, fontWeight: FontWeight.w500)),
                                          ],
                                        ),
                                      ],
                                    ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),
                      // trust strip
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        decoration: BoxDecoration(
                          color: T.surface,
                          borderRadius: BorderRadius.circular(T.radiusLg),
                          border: Border.all(color: T.borderLight),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.verified_user_outlined, size: 14, color: T.success),
                            SizedBox(width: 8),
                            Expanded(child: Text('Your resume stays private • PDF or DOCX up to 5 MB',
                                style: TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w600))),
                            Icon(Icons.lock_outline, size: 12, color: T.textLight),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final bool loadingRoles;
  const _Header({required this.loadingRoles});
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
          decoration: BoxDecoration(
            color: T.navy100.withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(100),
            border: Border.all(color: T.navy100),
          ),
          child: const Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.auto_awesome, size: 11, color: T.primary),
              SizedBox(width: 6),
              Text('AI-POWERED ANALYSIS',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.08 * 11, color: T.primary)),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Text('Resume Intelligence',
            textAlign: TextAlign.center,
            style: displayStyle(context, 28).copyWith(fontSize: 32, height: 1.05)),
        const SizedBox(height: 10),
        const Text(
          'Upload your resume and let our AI identify skill gaps\nand recommend a personalized learning path.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 14.5, height: 1.6, color: T.textMuted),
        ),
      ],
    );
  }
}

class _StepsIndicator extends StatelessWidget {
  const _StepsIndicator();
  @override
  Widget build(BuildContext context) {
    const steps = ['Upload', 'Analyze', 'Get Roadmap'];
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (int i = 0; i < steps.length; i++) ...[
          Row(
            children: [
              Container(
                width: 20, height: 20,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: i == 0 ? T.primary : T.border,
                ),
                child: Center(
                  child: Text('${i + 1}',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: i == 0 ? Colors.white : T.textLight)),
                ),
              ),
              const SizedBox(width: 6),
              Text(steps[i],
                  style: TextStyle(
                      fontSize: 11.5, fontWeight: FontWeight.w700,
                      color: i == 0 ? T.text : T.textLight)),
            ],
          ),
          if (i < steps.length - 1) Container(width: 24, height: 1, color: T.border, margin: const EdgeInsets.symmetric(horizontal: 6)),
        ],
      ],
    );
  }
}

class _DropZone extends StatelessWidget {
  final String? fileName;
  final int? fileSize;
  final String? fileSizeLabel;
  final bool hasFile;
  final String? error;
  final VoidCallback onBrowse;
  final VoidCallback onRemove;
  const _DropZone({
    required this.fileName,
    required this.fileSize,
    required this.fileSizeLabel,
    required this.hasFile,
    required this.error,
    required this.onBrowse,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    final hasError = error != null;
    final bg = hasFile ? const Color(0xFFF0FDF4) : T.bg;
    final border = hasError ? T.error : (hasFile ? T.success : T.border);
    return InkWell(
      onTap: hasFile ? null : onBrowse,
      borderRadius: BorderRadius.circular(T.radiusXl),
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: hasFile ? 14 : 28),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(T.radiusXl),
          border: Border.all(
            color: border,
            width: 1.6,
            // dashed effect via border width + opacity, solid for simplicity but premium
          ),
        ),
        child: hasFile
            ? Row(
                children: [
                  Container(
                    width: 44, height: 44,
                    decoration: BoxDecoration(color: T.success, borderRadius: BorderRadius.circular(T.radiusLg)),
                    child: const Icon(Icons.description_outlined, color: Colors.white, size: 20),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(fileName ?? '',
                            maxLines: 1, overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: T.text)),
                        const SizedBox(height: 2),
                        Row(
                          children: [
                            const Icon(Icons.check_circle, size: 12, color: T.success),
                            const SizedBox(width: 4),
                            Text('${fileSizeLabel ?? ''} • ready to analyze',
                                style: const TextStyle(fontSize: 11.5, color: T.textMuted, fontWeight: FontWeight.w600)),
                          ],
                        ),
                      ],
                    ),
                  ),
                  InkWell(
                    onTap: onRemove,
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      height: 32, width: 32,
                      decoration: BoxDecoration(
                        color: T.surface, borderRadius: BorderRadius.circular(8), border: Border.all(color: T.border),
                      ),
                      child: const Icon(Icons.close, size: 14, color: T.textMuted),
                    ),
                  ),
                ],
              )
            : Column(
                children: [
                  Container(
                    width: 56, height: 56,
                    decoration: BoxDecoration(color: T.navy100, borderRadius: BorderRadius.circular(16)),
                    child: const Icon(Icons.cloud_upload_outlined, size: 26, color: T.primary),
                  ),
                  const SizedBox(height: 12),
                  const Text('Click or drag your resume',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: T.text)),
                  const SizedBox(height: 4),
                  const Text('PDF or DOCX • up to 5 MB',
                      style: TextStyle(fontSize: 12.5, color: T.textMuted, fontWeight: FontWeight.w500)),
                ],
              ),
      ),
    );
  }
}

class _AnalyzingState extends StatelessWidget {
  final String role;
  const _AnalyzingState({required this.role});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 28),
      child: Column(
        children: [
          SizedBox(
            height: 56, width: 56,
            child: Stack(
              alignment: Alignment.center,
              children: [
                const SizedBox(
                  height: 56, width: 56,
                  child: CircularProgressIndicator(strokeWidth: 3, color: T.secondary),
                ),
                Container(
                  height: 44, width: 44,
                  decoration: const BoxDecoration(color: Color(0xFFFFEDD5), shape: BoxShape.circle),
                  child: const Icon(Icons.auto_awesome, size: 20, color: T.secondaryDark),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          const Text('Analyzing your resume…',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: T.text)),
          const SizedBox(height: 6),
          Text('Target: $role • this can take up to 90 seconds',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 12.5, color: T.textMuted)),
        ],
      ),
    );
  }
}
