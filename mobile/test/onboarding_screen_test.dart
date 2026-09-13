import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:skillpath/screens/onboarding_screen.dart';
import 'package:skillpath/widgets/onboarding/analysis_report_illustration.dart';
import 'package:skillpath/widgets/onboarding/career_ascent_illustration.dart';
import 'package:skillpath/widgets/onboarding/resume_audit_illustration.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('OnboardingScreen displays 3 steps with headlines, illustrations, and navigation', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: OnboardingScreen(),
      ),
    );

    // ── Page 1 ──
    expect(find.text('Get a Clear Picture of Your Resume'), findsOneWidget);
    expect(find.text('Upload your resume and let AI analyze it in seconds.'), findsOneWidget);
    expect(find.byType(ResumeAuditIllustration), findsOneWidget);
    expect(find.text('Next'), findsOneWidget);
    expect(find.text('Skip'), findsOneWidget);

    // Tap Next -> Page 2
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();

    // ── Page 2 ──
    expect(find.text('Get Detailed Feedback'), findsOneWidget);
    expect(find.text("Find out what's working, what can be improved, and how to make your resume stronger."), findsOneWidget);
    expect(find.byType(AnalysisReportIllustration), findsOneWidget);
    expect(find.text('Next'), findsOneWidget);

    // Tap Next -> Page 3
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();

    // ── Page 3 ──
    expect(find.text('Build a Stronger You'), findsOneWidget);
    expect(find.text('Create a better resume, unlock new opportunities, and take the next step in your career.'), findsOneWidget);
    expect(find.byType(CareerAscentIllustration), findsOneWidget);
    expect(find.text('Get Started'), findsOneWidget);
  });

  testWidgets('OnboardingScreen handles small screen dimensions without RenderFlex overflow', (tester) async {
    tester.view.physicalSize = const Size(360, 640);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() => tester.view.resetPhysicalSize());

    await tester.pumpWidget(
      const MaterialApp(
        home: OnboardingScreen(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Get a Clear Picture of Your Resume'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
