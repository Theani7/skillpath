import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:skillpath/widgets/onboarding/career_ascent_illustration.dart';

void main() {
  group('CareerAscentIllustration Tests', () {
    testWidgets('renders all milestone texts and widget successfully', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Center(
              child: CareerAscentIllustration(),
            ),
          ),
        ),
      );

      // Verify CareerAscentIllustration is present
      expect(find.byType(CareerAscentIllustration), findsOneWidget);

      // Verify 3 milestone pill badge texts
      expect(find.text('Brighter\nFuture'), findsOneWidget);
      expect(find.text('Better Resume'), findsOneWidget);
      expect(find.text('More\nOpportunities'), findsOneWidget);

      // Verify milestone badge icons
      expect(find.byIcon(Icons.emoji_events_rounded), findsOneWidget);
      expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
      expect(find.byIcon(Icons.bar_chart_rounded), findsOneWidget);
    });

    testWidgets('renders with custom dimensions without overflow', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Center(
              child: CareerAscentIllustration(
                width: 280,
                height: 240,
              ),
            ),
          ),
        ),
      );

      expect(find.byType(CareerAscentIllustration), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  });
}
