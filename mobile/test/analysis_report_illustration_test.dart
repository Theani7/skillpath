import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:skillpath/widgets/onboarding/analysis_report_illustration.dart';

void main() {
  testWidgets('AnalysisReportIllustration renders report title, score, checklist, and banner', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: AnalysisReportIllustration(),
          ),
        ),
      ),
    );

    expect(find.byType(AnalysisReportIllustration), findsOneWidget);
    expect(find.text('Analysis Report'), findsOneWidget);
    expect(find.text('78'), findsOneWidget);
    expect(find.text('/100'), findsOneWidget);
    expect(find.text('Strong points'), findsOneWidget);
    expect(find.text('Areas to improve'), findsOneWidget);
    expect(find.text('Suggestions'), findsOneWidget);
    expect(find.text('Actionable tips to stand out'), findsOneWidget);
  });
}
