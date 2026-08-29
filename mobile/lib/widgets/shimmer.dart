import 'package:flutter/material.dart';
import '../theme.dart';

/// Premium shimmer — mimics web .shimmer gradient (indigo-100 ↔ violet-100) with 1.5s sweep.
class AdvancedShimmer extends StatefulWidget {
  final Widget child;
  final Color baseColor;
  final Color highlightColor;
  const AdvancedShimmer({super.key, required this.child, this.baseColor = const Color(0xFFF0EDE8), this.highlightColor = Colors.white});

  @override
  State<AdvancedShimmer> createState() => _AdvancedShimmerState();
}

class _AdvancedShimmerState extends State<AdvancedShimmer> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 1400))..repeat();
    _anim = Tween<double>(begin: -2, end: 2).animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (rect) {
            final dx = _anim.value * rect.width;
            return LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [widget.baseColor, widget.highlightColor, widget.baseColor],
              stops: const [0.25, 0.5, 0.75],
              transform: GradientRotation(0),
            ).createShader(Rect.fromLTWH(dx - rect.width, 0, rect.width * 3, rect.height));
          },
          blendMode: BlendMode.srcATop,
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

/// Single skeleton block (rounded).
class SkeletonBlock extends StatelessWidget {
  final double? height;
  final double? width;
  final double radius;
  final EdgeInsetsGeometry? margin;
  const SkeletonBlock({super.key, this.height, this.width, this.radius = 8, this.margin});

  @override
  Widget build(BuildContext context) {
    final block = Container(height: height, width: width, decoration: BoxDecoration(color: T.borderLight, borderRadius: BorderRadius.circular(radius)));
    return Padding(padding: margin ?? EdgeInsets.zero, child: AdvancedShimmer(child: block));
  }
}

/// Skeleton primitives.
class Skeleton {
  static Widget line({double? width, double height = 12, double radius = 6, EdgeInsetsGeometry? margin}) =>
      SkeletonBlock(width: width, height: height, radius: radius, margin: margin);
  static Widget circle(double size) => SkeletonBlock(height: size, width: size, radius: size / 2);
  static Widget card({required Widget child}) => Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: T.surface, borderRadius: BorderRadius.circular(T.radiusXl), border: Border.all(color: T.borderLight), boxShadow: T.cardShadow),
        child: child,
      );
}
