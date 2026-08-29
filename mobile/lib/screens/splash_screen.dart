import 'package:flutter/material.dart';
import '../theme.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: T.bg,
      body: Stack(
        children: [
          Positioned(
            top: -120, right: -100,
            child: Container(width: 360, height: 360, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.primary.withValues(alpha: 0.06), Colors.transparent]))),
          ),
          Positioned(
            bottom: -140, left: -140,
            child: Container(width: 380, height: 380, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [T.secondary.withValues(alpha: 0.05), Colors.transparent]))),
          ),
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Hero(
                  tag: 'skillpath-logo',
                  child: Container(
                    height: 84, width: 84,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(20), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
                    child: ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.asset('assets/icon.png', fit: BoxFit.contain)),
                  ),
                ),
                const SizedBox(height: 16),
                Text('SkillPath', style: displayStyle(context, 22)),
                const SizedBox(height: 4),
                const Text('AI-powered career growth', style: TextStyle(fontSize: 12.5, color: T.textMuted, fontWeight: FontWeight.w600, letterSpacing: 0.04 * 12.5)),
                const SizedBox(height: 28),
                const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2.5, color: T.secondary)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
