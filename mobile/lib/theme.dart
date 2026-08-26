import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// SkillPath "Launchpad" design tokens — mirrors frontend/src/styles/tokens.css.
abstract final class T {
  // Colors
  static const bg = Color(0xFFF8F6F3); // --color-bg
  static const surface = Color(0xFFFFFFFF); // --color-surface
  static const primary = Color(0xFF0A1628); // --color-primary (navy-950)
  static const primaryLight = Color(0xFF1A2D4A); // --color-primary-light
  static const secondary = Color(0xFFFF6B35); // --color-secondary (orange)
  static const secondaryLight = Color(0xFFFF8A5C); // --color-secondary-light
  static const secondaryDark = Color(0xFFE55A2B); // --color-secondary-dark
  static const text = Color(0xFF0A1628); // --color-text
  static const textMuted = Color(0xFF5A6577); // --color-text-muted
  static const textLight = Color(0xFF8B95A5); // --color-text-light
  static const success = Color(0xFF22C55E); // --color-success
  static const successLight = Color(0xFFDCFCE7); // --color-success-light
  static const warning = Color(0xFFF59E0B); // --color-warning
  static const warningLight = Color(0xFFFEF3C7); // --color-warning-light
  static const error = Color(0xFFEF4444); // --color-error
  static const errorLight = Color(0xFFFEE2E2); // --color-error-light
  static const border = Color(0xFFE5E2DC); // --color-border
  static const borderLight = Color(0xFFF0EDE8); // --color-border-light

  // Navy scale
  static const navy100 = Color(0xFFD9E2EC);
  static const navy500 = Color(0xFF627D98);
  static const navy900 = Color(0xFF102A43);

  // Radii (tokens.css: lg=12, xl=16, 2xl=20)
  static const radiusLg = 12.0;
  static const radiusXl = 16.0;

  // Signature shadows
  static final cardShadow = [
    BoxShadow(
      offset: const Offset(0, 4),
      blurRadius: 20,
      spreadRadius: -2,
      color: const Color(0xFF0A1628).withValues(alpha: 0.08),
    ),
  ];
  static final buttonShadow = [
    BoxShadow(
      offset: const Offset(0, 4),
      blurRadius: 14,
      color: const Color(0xFFFF6B35).withValues(alpha: 0.3),
    ),
  ];
}

ThemeData buildTheme() {
  final scheme = ColorScheme.light(
    primary: T.primary,
    onPrimary: T.surface,
    primaryContainer: T.navy100,
    onPrimaryContainer: T.primary,
    secondary: T.secondary,
    onSecondary: T.surface,
    secondaryContainer: const Color(0xFFFFEDD5), // orange-100
    onSecondaryContainer: T.secondaryDark,
    surface: T.surface,
    onSurface: T.text,
    surfaceContainerHighest: T.borderLight,
    onSurfaceVariant: T.textMuted,
    error: T.error,
    errorContainer: T.errorLight,
    onError: T.surface,
    onErrorContainer: T.error,
    outline: T.border,
    outlineVariant: T.borderLight,
  );

  final body = GoogleFonts.plusJakartaSansTextTheme().apply(
    bodyColor: T.text,
    displayColor: T.text,
  );
  final display = GoogleFonts.spaceGroteskTextTheme().apply(
    bodyColor: T.text,
    displayColor: T.text,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: T.bg,
    textTheme: body,
    primaryTextTheme: display,
    appBarTheme: AppBarTheme(
      backgroundColor: T.bg,
      foregroundColor: T.primary,
      elevation: 0,
      scrolledUnderElevation: 0,
      titleTextStyle: GoogleFonts.spaceGrotesk(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        color: T.primary,
        letterSpacing: -0.02 * 24,
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: T.surface,
      hintStyle: const TextStyle(color: T.textLight),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(T.radiusLg),
        borderSide: const BorderSide(color: T.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(T.radiusLg),
        borderSide: const BorderSide(color: T.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(T.radiusLg),
        borderSide: const BorderSide(color: T.secondary, width: 1.5),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style:
          FilledButton.styleFrom(
            backgroundColor: T.secondary,
            foregroundColor: T.surface,
            minimumSize: const Size.fromHeight(48),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(T.radiusLg),
            ),
            textStyle: GoogleFonts.plusJakartaSans(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
            elevation: 0,
          ).copyWith(
            overlayColor: WidgetStateProperty.all(
              T.surface.withValues(alpha: 0.2),
            ),
          ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: T.primary,
        minimumSize: const Size.fromHeight(48),
        side: const BorderSide(color: T.border),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(T.radiusLg),
        ),
        textStyle: GoogleFonts.plusJakartaSans(
          fontSize: 15,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: T.secondaryDark,
        textStyle: GoogleFonts.plusJakartaSans(
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    cardTheme: CardThemeData(
      elevation: 0,
      color: T.surface,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(T.radiusXl),
        side: const BorderSide(color: T.borderLight),
      ),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: T.surface,
      indicatorColor: const Color(0xFFFFEDD5), // orange-100
      surfaceTintColor: T.surface,
      elevation: 0,
      height: 68,
      labelTextStyle: WidgetStatePropertyAll(
        GoogleFonts.plusJakartaSans(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: T.primary,
        ),
      ),
      iconTheme: const WidgetStatePropertyAll(IconThemeData(color: T.navy500)),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: T.navy100,
      labelStyle: const TextStyle(color: T.navy900, fontSize: 13),
      side: BorderSide.none,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(T.radiusLg),
      ),
    ),
    dividerTheme: const DividerThemeData(color: T.borderLight),
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      backgroundColor: T.primary,
      contentTextStyle: GoogleFonts.plusJakartaSans(
        fontSize: 14,
        color: T.surface,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(T.radiusLg),
      ),
    ),
    progressIndicatorTheme: const ProgressIndicatorThemeData(
      color: T.secondary,
      linearTrackColor: T.borderLight,
    ),
    dropdownMenuTheme: const DropdownMenuThemeData(
      menuStyle: MenuStyle(surfaceTintColor: WidgetStatePropertyAll(T.surface)),
    ),
  );
}

/// Display/headline style helper (Space Grotesk, tight tracking) for screens
/// that build large headings outside AppBar.
TextStyle displayStyle(BuildContext context, double size) =>
    GoogleFonts.spaceGrotesk(
      fontSize: size,
      fontWeight: FontWeight.w700,
      color: T.primary,
      letterSpacing: -0.02 * size,
    );
