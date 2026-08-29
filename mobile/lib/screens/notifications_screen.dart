import 'package:flutter/material.dart';
import '../services/api_client.dart';
import '../theme.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});
  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;
  @override
  void initState() { super.initState(); _load(); }
  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final res = await Api.instance.dio.get('/api/notifications');
      final list = (res.data is Map ? (res.data as Map)['notifications'] : null) as List?;
      _items = (list ?? []).whereType<Map>().map((m) => m.cast<String, dynamic>()).toList();
    } catch (_) {
      _items = [];
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      appBar: AppBar(title: const Text('Notifications'), backgroundColor: T.bg, elevation: 0),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: T.secondary))
          : _items.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(mainAxisSize: MainAxisSize.min, children: [
                      Container(height: 48, width: 48, decoration: BoxDecoration(color: T.navy100, shape: BoxShape.circle), child: const Icon(Icons.notifications_none, color: T.primary)),
                      const SizedBox(height: 12),
                      const Text('No notifications', style: TextStyle(fontWeight: FontWeight.w700, color: T.text)),
                      const SizedBox(height: 4),
                      const Text('You\'re all caught up', style: TextStyle(fontSize: 12.5, color: T.textMuted)),
                    ]),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  color: T.secondary,
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: _items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 10),
                    itemBuilder: (ctx, i) {
                      final n = _items[i];
                      final msg = n['message']?.toString() ?? '';
                      final ch = n['channel']?.toString() ?? 'email';
                      final status = n['status']?.toString() ?? 'pending';
                      return Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusLg), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                        child: Row(
                          children: [
                            Container(height: 36, width: 36, decoration: BoxDecoration(color: status == 'pending' ? const Color(0xFFFFEDD5) : T.successLight, borderRadius: BorderRadius.circular(10)), child: Icon(ch == 'push' ? Icons.phone_iphone : ch == 'sms' ? Icons.sms_outlined : Icons.mail_outline, size: 18, color: status == 'pending' ? T.secondaryDark : T.success)),
                            const SizedBox(width: 12),
                            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(msg, style: const TextStyle(fontSize: 13, color: T.text, height: 1.4)), const SizedBox(height: 4), Text('${ch.toUpperCase()} • $status', style: const TextStyle(fontSize: 11, color: T.textLight, fontWeight: FontWeight.w700))])),
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
