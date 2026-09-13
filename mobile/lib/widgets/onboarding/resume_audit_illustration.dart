import 'dart:math' as math;
import 'package:flutter/material.dart';

import '../../theme.dart';

/// Step 1 onboarding illustration: Resume audit with magnifying glass inspection.
class ResumeAuditIllustration extends StatelessWidget {
  const ResumeAuditIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 300,
      height: 260,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Ambient organic backdrop aura
          Positioned(
            left: 14,
            top: 10,
            width: 272,
            height: 236,
            child: Container(
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(42),
                  topRight: Radius.circular(26),
                  bottomLeft: Radius.circular(30),
                  bottomRight: Radius.circular(50),
                ),
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFFE2EDFB),
                    Color(0xFFEDF4FD),
                  ],
                ),
              ),
            ),
          ),

          // Elevated white resume card
          Positioned(
            left: 20,
            top: 18,
            width: 220,
            height: 198,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: T.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: const Color(0xFFF0EDE8),
                  width: 1,
                ),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x0F0A1628),
                    blurRadius: 20,
                    offset: Offset(0, 6),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header row: Avatar circle + bold title
                  Row(
                    children: [
                      Container(
                        width: 32,
                        height: 32,
                        decoration: const BoxDecoration(
                          color: Color(0xFFE2EDFB),
                          shape: BoxShape.circle,
                        ),
                        alignment: Alignment.center,
                        child: const Icon(
                          Icons.person_rounded,
                          size: 18,
                          color: Color(0xFF102A43),
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Expanded(
                        child: Text(
                          'Your Resume',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF0A1628),
                            letterSpacing: -0.2,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Body of resume: 5 skeleton rounded bars with varying widths
                  _buildSkeletonBar(
                    width: 120,
                    color: const Color(0xFFCBD5E1),
                  ),
                  const SizedBox(height: 10),
                  _buildSkeletonBar(
                    width: 180,
                    color: const Color(0xFFE2E8F0),
                  ),
                  const SizedBox(height: 10),
                  _buildSkeletonBar(
                    width: 140,
                    color: const Color(0xFFE2E8F0),
                  ),
                  const SizedBox(height: 10),
                  _buildSkeletonBar(
                    width: 90,
                    color: const Color(0xFFCBD5E1),
                  ),
                  const SizedBox(height: 10),
                  _buildSkeletonBar(
                    width: 155,
                    color: const Color(0xFFE2E8F0),
                  ),
                ],
              ),
            ),
          ),

          // Magnifying glass overlay positioned over lower-right of resume
          Positioned(
            left: 165,
            top: 124,
            child: _buildMagnifyingGlass(),
          ),
        ],
      ),
    );
  }

  Widget _buildSkeletonBar({
    required double width,
    required Color color,
    double height = 7,
  }) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(height / 2),
      ),
    );
  }

  Widget _buildMagnifyingGlass() {
    return SizedBox(
      width: 120,
      height: 120,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Angled handle (slanted at 45 deg down-right)
          Positioned(
            left: 84,
            top: 72,
            child: Transform.rotate(
              angle: -math.pi / 4,
              child: Container(
                width: 11,
                height: 38,
                decoration: BoxDecoration(
                  color: const Color(0xFF102A43),
                  borderRadius: BorderRadius.circular(5.5),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x220A1628),
                      blurRadius: 6,
                      offset: Offset(2, 2),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Glass lens with dark rim
          Container(
            width: 92,
            height: 92,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white.withValues(alpha: 0.95),
              border: Border.all(
                color: const Color(0xFF102A43),
                width: 4,
              ),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x1F0A1628),
                  blurRadius: 16,
                  offset: Offset(0, 6),
                ),
              ],
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildCheckItem(lineWidth: 30),
                const SizedBox(height: 7),
                _buildCheckItem(lineWidth: 38),
                const SizedBox(height: 7),
                _buildCheckItem(lineWidth: 26),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCheckItem({required double lineWidth}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: const BoxDecoration(
            color: Color(0xFF22C55E),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: const Icon(
            Icons.check,
            size: 10,
            color: Colors.white,
          ),
        ),
        const SizedBox(width: 6),
        Container(
          width: lineWidth,
          height: 5,
          decoration: BoxDecoration(
            color: const Color(0xFF94A3B8),
            borderRadius: BorderRadius.circular(2.5),
          ),
        ),
      ],
    );
  }
}
