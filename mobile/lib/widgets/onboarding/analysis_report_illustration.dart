import 'dart:math' as math;
import 'package:flutter/material.dart';

/// Step 2 Onboarding Illustration Widget: Analysis Report
///
/// Displays an elevated report card with radial score gauge,
/// metric checklist, and actionable tip banner against an ambient backdrop.
class AnalysisReportIllustration extends StatelessWidget {
  const AnalysisReportIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 300,
      height: 260,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Soft organic ambient backdrop aura
          Container(
            width: 290,
            height: 246,
            decoration: BoxDecoration(
              color: const Color(0xFFE2EDFB),
              borderRadius: BorderRadius.circular(32),
            ),
          ),

          // Elevated white card
          Container(
            width: 270,
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x0F0A1628),
                  blurRadius: 20,
                  offset: Offset(0, 6),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header on card
                const Text(
                  'Analysis Report',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 15.5,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF0A1628),
                  ),
                ),
                const SizedBox(height: 14),

                // Center row: Radial progress gauge + checklist
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    // Radial progress gauge
                    SizedBox(
                      width: 80,
                      height: 80,
                      child: CustomPaint(
                        painter: const _RadialScorePainter(
                          progress: 0.78,
                          trackColor: Color(0xFFE2E8F0),
                          progressColor: Color(0xFF22C55E),
                          strokeWidth: 7.5,
                        ),
                        child: const Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                '78',
                                style: TextStyle(
                                  fontSize: 26,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF0A1628),
                                  height: 1.0,
                                ),
                              ),
                              SizedBox(height: 2),
                              Text(
                                '/100',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF64748B),
                                  height: 1.0,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),

                    // Metric checklist rows
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: const [
                          _MetricRow(
                            icon: Icons.check_circle,
                            iconColor: Color(0xFF22C55E),
                            text: 'Strong points',
                          ),
                          SizedBox(height: 8),
                          _MetricRow(
                            icon: Icons.error,
                            iconColor: Color(0xFFF59E0B),
                            text: 'Areas to improve',
                          ),
                          SizedBox(height: 8),
                          _MetricRow(
                            icon: Icons.info,
                            iconColor: Color(0xFF3B82F6),
                            text: 'Suggestions',
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // Bottom banner inside the card
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF3C7),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.lightbulb_outline,
                        size: 16,
                        color: Color(0xFFD97706),
                      ),
                      SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          'Actionable tips to stand out',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF78350F),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricRow extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String text;

  const _MetricRow({
    required this.icon,
    required this.iconColor,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: iconColor,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: Color(0xFF334155),
            ),
          ),
        ),
      ],
    );
  }
}

class _RadialScorePainter extends CustomPainter {
  final double progress;
  final Color trackColor;
  final Color progressColor;
  final double strokeWidth;

  const _RadialScorePainter({
    required this.progress,
    required this.trackColor,
    required this.progressColor,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Background track circle
    final trackPaint = Paint()
      ..color = trackColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, trackPaint);

    // Progress arc
    final progressPaint = Paint()
      ..color = progressColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _RadialScorePainter oldDelegate) {
    return oldDelegate.progress != progress ||
        oldDelegate.trackColor != trackColor ||
        oldDelegate.progressColor != progressColor ||
        oldDelegate.strokeWidth != strokeWidth;
  }
}
