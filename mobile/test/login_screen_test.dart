import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:skillpath/screens/auth/login_screen.dart';
import 'package:skillpath/state/session.dart';

void main() {
  Widget buildTestApp({Session? session}) {
    return ChangeNotifierProvider<Session>.value(
      value: session ?? Session(),
      child: const MaterialApp(
        home: LoginScreen(),
      ),
    );
  }

  testWidgets('LoginScreen renders Step 1 with email field, Continue, and Google SSO', (tester) async {
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    // Step 1 Header
    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('SECURE SIGN IN • STEP 1'), findsOneWidget);
    expect(find.text('Email address'), findsOneWidget);

    // Buttons
    expect(find.text('Continue'), findsOneWidget);
    expect(find.text('Continue with Google'), findsOneWidget);

    // Password field should NOT exist on Step 1
    expect(find.text('Enter your password'), findsNothing);
    expect(find.text('Password'), findsNothing);
  });

  testWidgets('LoginScreen shows validation error for invalid email', (tester) async {
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    // Tap Continue without typing
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    expect(find.text('Email is required'), findsOneWidget);

    // Enter invalid email
    await tester.enterText(find.byType(TextFormField), 'notanemail');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    expect(find.text('Enter a valid email address'), findsOneWidget);
  });

  testWidgets('LoginScreen advances to Step 2 and allows tapping Change to return to Step 1', (tester) async {
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    // Enter valid email
    await tester.enterText(find.byType(TextFormField), 'alice@example.com');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();

    // Fallback/direct check advances to Step 2
    expect(find.text('Enter your password'), findsOneWidget);
    expect(find.text('ENTER PASSWORD • STEP 2'), findsOneWidget);
    expect(find.text('alice@example.com'), findsOneWidget);
    expect(find.text('Change'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);

    // Tap "Change" to return to Step 1
    await tester.tap(find.text('Change'));
    await tester.pumpAndSettle();

    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
  });
}
