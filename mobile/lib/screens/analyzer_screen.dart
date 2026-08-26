import 'dart:io';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../router.dart';
import '../services/api_client.dart';

/// Fallback target roles when GET /api/job-roles is unavailable.
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
      final roles =
          (raw as List?)
              ?.map((r) => r.toString())
              .where((r) => r.isNotEmpty)
              .toList() ??
          const <String>[];
      if (!mounted) return;
      setState(() {
        _roles = roles.isNotEmpty ? roles : List.of(_fallbackRoles);
        if (!_roles.contains(_selectedRole)) {
          _selectedRole = _roles.first;
        }
        _loadingRoles = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _roles = List.of(_fallbackRoles);
        if (!_roles.contains(_selectedRole)) {
          _selectedRole = _roles.first;
        }
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
      if (picked == null) return; // user canceled
      final size = await picked.length();
      if (!mounted) return;
      setState(() {
        _file = picked;
        _fileSize = size;
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(Api.errorMessage(e))));
    }
  }

  String? get _fileError {
    if (_file == null) return null;
    if (_fileSize == null || _fileSize! > _maxUploadBytes) {
      return 'File exceeds the 5 MB limit.';
    }
    return null;
  }

  String _fileSizeLabel(int bytes) {
    if (bytes >= 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
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
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(Api.errorMessage(e))));
      return;
    }
    if (!mounted) return;

    setState(() => _uploading = true);
    try {
      final form = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: file.name),
        'target_role': role,
      });
      final res = await Api.instance.dio.post('/api/analyze', data: form);
      final data = res.data;
      if (!mounted) return;
      if (data is Map && data['error'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(data['message']?.toString() ?? 'Analysis failed.'),
          ),
        );
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Analysis complete')));
      context.go(Routes.result);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(Api.errorMessage(e))));
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  /// Read picked-file bytes whether they are cached or behind a local path.
  Future<Uint8List> _readBytes(PlatformFile file) async {
    final path = file.path;
    if (path != null) return File(path).readAsBytes();
    return file.readAsBytes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Resume Analyzer')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              margin: EdgeInsets.zero,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Target role',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    if (_loadingRoles)
                      const LinearProgressIndicator(minHeight: 2)
                    else
                      DropdownButtonFormField<String>(
                        initialValue: _selectedRole,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.work_outline),
                        ),
                        items: [
                          for (final role in _roles)
                            DropdownMenuItem(value: role, child: Text(role)),
                        ],
                        onChanged: (value) =>
                            setState(() => _selectedRole = value),
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              margin: EdgeInsets.zero,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Resume file',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    OutlinedButton.icon(
                      onPressed: _uploading ? null : _pickFile,
                      icon: const Icon(Icons.upload_file_outlined),
                      label: const Text('Choose PDF or DOCX'),
                    ),
                    if (_file != null) ...[
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Icon(
                            Icons.description_outlined,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _file!.name,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: Theme.of(context).textTheme.bodyLarge,
                                ),
                                Text(
                                  _fileSizeLabel(_fileSize ?? 0),
                                  style: Theme.of(context).textTheme.bodySmall
                                      ?.copyWith(
                                        color: Theme.of(
                                          context,
                                        ).colorScheme.onSurfaceVariant,
                                      ),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            tooltip: 'Remove file',
                            onPressed: _uploading
                                ? null
                                : () => setState(() {
                                    _file = null;
                                    _fileSize = null;
                                  }),
                            icon: const Icon(Icons.close),
                          ),
                        ],
                      ),
                    ],
                    if (_fileError != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text(
                          _fileError!,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (_uploading) ...[
              const Center(child: CircularProgressIndicator()),
              const SizedBox(height: 12),
              Text(
                'Analyzing your resume — this can take up to 90 seconds.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 12),
            ] else
              FilledButton.icon(
                onPressed:
                    (_file != null && _selectedRole != null && !_loadingRoles)
                    ? _analyze
                    : null,
                icon: const Icon(Icons.auto_awesome_outlined),
                label: const Text('Analyze my resume'),
              ),
          ],
        ),
      ),
    );
  }
}
