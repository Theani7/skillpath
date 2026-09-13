import 'dart:math' as math;
import 'package:flutter/material.dart';

/// Step 3 onboarding illustration displaying career ascent:
/// ascending gradient stair steps, upward surge momentum arrow,
/// stylized climbing professional with portfolio, and floating milestone badges.
class CareerAscentIllustration extends StatelessWidget {
  final double width;
  final double height;

  const CareerAscentIllustration({
    super.key,
    this.width = 300,
    this.height = 260,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: FittedBox(
        fit: BoxFit.contain,
        child: SizedBox(
          width: 300,
          height: 260,
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              // 1. Soft organic ambient backdrop aura
              Positioned(
                left: 20,
                right: 20,
                top: 15,
                bottom: 15,
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: const BorderRadius.all(
                      Radius.elliptical(130, 110),
                    ),
                    gradient: RadialGradient(
                      center: const Alignment(-0.05, -0.1),
                      radius: 0.9,
                      colors: [
                        const Color(0xFFE2EDFB),
                        const Color(0xFFEAF2FD).withValues(alpha: 0.8),
                        const Color(0xFFF3F7FD).withValues(alpha: 0.4),
                        Colors.transparent,
                      ],
                      stops: const [0.0, 0.45, 0.75, 1.0],
                    ),
                  ),
                ),
              ),

              // Decorative soft background glow orb
              Positioned(
                top: 30,
                right: 40,
                child: Container(
                  width: 90,
                  height: 90,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        const Color(0xFFBFDBFE).withValues(alpha: 0.35),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),

              // 2. Diagonal upward surge arrow behind/alongside the stairs
              Positioned(
                left: 100,
                bottom: 25,
                child: CustomPaint(
                  size: const Size(160, 180),
                  painter: _SurgeArrowPainter(),
                ),
              ),

              // 3. Ground baseline bar under stairs
              Positioned(
                left: 122,
                bottom: 28,
                child: Container(
                  width: 144,
                  height: 3,
                  decoration: BoxDecoration(
                    color: const Color(0xFFBFDBFE),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),

              // 4. Ascending 3 vertical gradient bar steps
              // Step 1 (height 40, width 36)
              Positioned(
                left: 130,
                bottom: 30,
                child: _buildStairStep(height: 40, width: 36),
              ),

              // Step 2 (height 75, width 36)
              Positioned(
                left: 174,
                bottom: 30,
                child: _buildStairStep(height: 75, width: 36),
              ),

              // Step 3 (height 115, width 36)
              Positioned(
                left: 218,
                bottom: 30,
                child: _buildStairStep(height: 115, width: 36),
              ),

              // 5. Stylized climber figure / ascending professional icon
              // Positioned ascending from step 2 toward step 3
              Positioned(
                left: 168,
                bottom: 95,
                child: CustomPaint(
                  size: const Size(54, 76),
                  painter: _ClimberPainter(),
                ),
              ),

              // 6. Floating milestone pill badges
              // Top Right: Warm yellow badge + trophy icon + 'Brighter\nFuture'
              const Positioned(
                top: 14,
                right: 8,
                child: _MilestonePillBadge(
                  background: Color(0xFFFEF9C3),
                  borderColor: Color(0xFFFEF08A),
                  icon: Icons.emoji_events_rounded,
                  iconColor: Color(0xFFD97706),
                  text: 'Brighter\nFuture',
                  textColor: Color(0xFF854D0E),
                  multiline: true,
                ),
              ),

              // Mid Left: Mint green badge + check icon + 'Better Resume'
              const Positioned(
                top: 96,
                left: 8,
                child: _MilestonePillBadge(
                  background: Color(0xFFDCFCE7),
                  borderColor: Color(0xFFBBF7D0),
                  icon: Icons.check_circle_rounded,
                  iconColor: Color(0xFF16A34A),
                  text: 'Better Resume',
                  textColor: Color(0xFF166534),
                  multiline: false,
                ),
              ),

              // Lower Left: Lavender badge + purple chart icon + 'More\nOpportunities'
              const Positioned(
                bottom: 18,
                left: 8,
                child: _MilestonePillBadge(
                  background: Color(0xFFEDE9FE),
                  borderColor: Color(0xFFDDD6FE),
                  icon: Icons.bar_chart_rounded,
                  iconColor: Color(0xFF4F46E5),
                  text: 'More\nOpportunities',
                  textColor: Color(0xFF3730A3),
                  multiline: true,
                ),
              ),

              // Subtle decorative sparkles
              Positioned(
                top: 72,
                left: 120,
                child: _buildSparkle(size: 8, color: const Color(0xFF93C5FD)),
              ),
              Positioned(
                top: 40,
                left: 180,
                child: _buildSparkle(
                  size: 10,
                  color: const Color(0xFFFBBF24).withValues(alpha: 0.8),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static Widget _buildStairStep({
    required double height,
    required double width,
  }) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFFE0EFFF), Color(0xFFBDDCFE)],
        ),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
        border: Border.all(color: const Color(0xFF93C5FD), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF3B82F6).withValues(alpha: 0.08),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Align(
        alignment: Alignment.topCenter,
        child: Container(
          height: 3,
          margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(2),
          ),
        ),
      ),
    );
  }

  static Widget _buildSparkle({required double size, required Color color}) {
    return Icon(Icons.auto_awesome, size: size, color: color);
  }
}

/// Floating milestone pill badge widget with colored background, border, icon, and text.
class _MilestonePillBadge extends StatelessWidget {
  final Color background;
  final Color borderColor;
  final IconData icon;
  final Color iconColor;
  final String text;
  final Color textColor;
  final bool multiline;

  const _MilestonePillBadge({
    required this.background,
    required this.borderColor,
    required this.icon,
    required this.iconColor,
    required this.text,
    required this.textColor,
    required this.multiline,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: 10,
        vertical: multiline ? 6 : 7,
      ),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor, width: 1.2),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0A1628).withValues(alpha: 0.06),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(icon, size: 18, color: iconColor),
          const SizedBox(width: 6),
          Text(
            text,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: textColor,
              height: 1.15,
              letterSpacing: -0.1,
            ),
          ),
        ],
      ),
    );
  }
}

/// Custom painter for the diagonal upward momentum surge arrow.
class _SurgeArrowPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Secondary dashed trail
    final trailPaint =
        Paint()
          ..color = const Color(0xFFBFDBFE).withValues(alpha: 0.5)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2.0
          ..strokeCap = StrokeCap.round;

    final trailPath =
        Path()
          ..moveTo(10, size.height - 15)
          ..quadraticBezierTo(
            size.width * 0.45,
            size.height * 0.7,
            size.width * 0.75,
            size.height * 0.35,
          );
    canvas.drawPath(trailPath, trailPaint);

    // Main surge curve
    final mainPaint =
        Paint()
          ..shader = const LinearGradient(
            colors: [
              Color(0xFFBFDBFE),
              Color(0xFF93C5FD),
              Color(0xFF60A5FA),
            ],
          ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3.5
          ..strokeCap = StrokeCap.round;

    final arrowPath =
        Path()
          ..moveTo(18, size.height - 10)
          ..quadraticBezierTo(
            size.width * 0.52,
            size.height * 0.55,
            size.width - 16,
            18,
          );
    canvas.drawPath(arrowPath, mainPaint);

    // Arrowhead at the top tip
    final headPaint =
        Paint()
          ..color = const Color(0xFF60A5FA)
          ..style = PaintingStyle.fill;

    final tip = Offset(size.width - 12, 14);
    final arrowHead =
        Path()
          ..moveTo(tip.dx, tip.dy)
          ..lineTo(tip.dx - 14, tip.dy + 4)
          ..lineTo(tip.dx - 8, tip.dy + 12)
          ..close();
    canvas.drawPath(arrowHead, headPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Custom painter for the stylized professional climber ascending the stairs with a portfolio.
class _ClimberPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final bodyPaint =
        Paint()
          ..color = const Color(0xFF1E3A8A)
          ..style = PaintingStyle.fill;

    final accentPaint =
        Paint()
          ..color = const Color(0xFF2563EB)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 4.0
          ..strokeCap = StrokeCap.round;

    final limbPaint =
        Paint()
          ..color = const Color(0xFF1E293B)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3.5
          ..strokeCap = StrokeCap.round;

    // 1. Trailing leg (back, pushing off step)
    final backLeg =
        Path()
          ..moveTo(22, 42)
          ..lineTo(14, 56)
          ..lineTo(8, 70);
    canvas.drawPath(backLeg, limbPaint);

    // 2. Leading climbing leg (stepping up onto next step)
    final frontLeg =
        Path()
          ..moveTo(26, 42)
          ..lineTo(36, 50)
          ..lineTo(42, 64);
    canvas.drawPath(frontLeg, limbPaint);

    // 3. Torso (angled forward dynamically)
    final torsoPath =
        Path()
          ..moveTo(24, 20)
          ..lineTo(34, 24)
          ..lineTo(26, 43)
          ..lineTo(19, 40)
          ..close();
    canvas.drawPath(torsoPath, bodyPaint);

    // Torso highlight line / tie accent
    canvas.drawLine(const Offset(27, 22), const Offset(23, 36), accentPaint);

    // 4. Head (round with slight forward angle)
    canvas.drawCircle(const Offset(31, 12), 7.0, bodyPaint);

    // 5. Climbing arm reaching forward / upward
    final reachArm =
        Path()
          ..moveTo(31, 25)
          ..lineTo(44, 20)
          ..lineTo(48, 14);
    canvas.drawPath(reachArm, limbPaint);

    // 6. Arm holding portfolio / briefcase
    final carryArm =
        Path()
          ..moveTo(22, 26)
          ..lineTo(16, 34)
          ..lineTo(18, 42);
    canvas.drawPath(carryArm, limbPaint);

    // Portfolio / briefcase held by hand
    final portfolioPaint =
        Paint()
          ..color = const Color(0xFFD97706)
          ..style = PaintingStyle.fill;
    final portfolioBorder =
        Paint()
          ..color = const Color(0xFFB45309)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.0;

    final portfolioRect = RRect.fromRectAndRadius(
      const Rect.fromLTWH(8, 38, 16, 12),
      const Radius.circular(2.5),
    );
    canvas.drawRRect(portfolioRect, portfolioPaint);
    canvas.drawRRect(portfolioRect, portfolioBorder);

    // Portfolio handle
    final handlePaint =
        Paint()
          ..color = const Color(0xFF92400E)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.2;
    canvas.drawArc(
      const Rect.fromLTWH(13, 35, 6, 5),
      math.pi,
      math.pi,
      false,
      handlePaint,
    );

    // Portfolio gold clasp accent
    final claspPaint =
        Paint()
          ..color = const Color(0xFFFEF08A)
          ..style = PaintingStyle.fill;
    canvas.drawRect(const Rect.fromLTWH(14.5, 42, 3, 2), claspPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
