import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:skillpath/widgets/onboarding/resume_audit_illustration.dart';

void main() {
  testWidgets('ResumeAuditIllustration renders resume header and structure', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: ResumeAuditIllustration(),
          ),
        ),
      ),
    );

    expect(find.byType(ResumeAuditIllustration), findsOneWidget);
    expect(find.text('Your Resume'), findsOneWidget);
    expect(find.byIcon(Icons.check), findsNWidgets(3));
    expect(find.byIcon(Icons.person_rounded), findsOneWidget);
  });
}
