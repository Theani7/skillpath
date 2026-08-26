import '../services/api_client.dart';

class AuthService {
  /// GET /api/auth/check-username/{username} -> {available: bool}
  static Future<bool> checkUsername(String username) async {
    final res = await Api.instance.dio.get(
      '/api/auth/check-username/$username',
    );
    return (res.data as Map)['available'] == true;
  }

  /// POST /api/auth/register -> {message, otp_sent}
  static Future<(String?, bool)> register({
    required String username,
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      final res = await Api.instance.dio.post(
        '/api/auth/register',
        data: {
          'username': username,
          'email': email,
          'password': password,
          'full_name': fullName,
        },
      );
      final map = (res.data as Map?)?.cast<String, dynamic>() ?? {};
      return (
        res.statusCode == 200
            ? null
            : (map['message']?.toString() ?? 'Registration failed'),
        map['otp_sent'] == true,
      );
    } catch (e) {
      return (Api.errorMessage(e), false);
    }
  }

  /// POST /api/auth/verify-email {email, otp}
  static Future<String?> verifyEmail(String email, String otp) async {
    try {
      await Api.instance.dio.post(
        '/api/auth/verify-email',
        data: {'email': email, 'otp': otp},
      );
      return null;
    } catch (e) {
      return Api.errorMessage(e);
    }
  }

  /// POST /api/auth/resend-otp {email, purpose}
  static Future<String?> resendOtp(
    String email, {
    String purpose = 'register',
  }) async {
    try {
      await Api.instance.dio.post(
        '/api/auth/resend-otp',
        data: {'email': email, 'purpose': purpose},
      );
      return null;
    } catch (e) {
      return Api.errorMessage(e);
    }
  }

  /// POST /api/auth/request-password-reset {email}
  static Future<String?> requestPasswordReset(String email) async {
    try {
      await Api.instance.dio.post(
        '/api/auth/request-password-reset',
        data: {'email': email},
      );
      return null;
    } catch (e) {
      return Api.errorMessage(e);
    }
  }

  /// POST /api/auth/verify-reset-otp {email, otp} -> {reset_token}
  static Future<(String? error, String? resetToken)> verifyResetOtp(
    String email,
    String otp,
  ) async {
    try {
      final res = await Api.instance.dio.post(
        '/api/auth/verify-reset-otp',
        data: {'email': email, 'otp': otp},
      );
      return (null, ((res.data as Map)['reset_token'] ?? '').toString());
    } catch (e) {
      return (Api.errorMessage(e), null);
    }
  }

  /// POST /api/auth/reset-password {token, new_password}
  static Future<String?> resetPassword(String token, String newPassword) async {
    try {
      await Api.instance.dio.post(
        '/api/auth/reset-password',
        data: {'token': token, 'new_password': newPassword},
      );
      return null;
    } catch (e) {
      return Api.errorMessage(e);
    }
  }

  /// POST /api/auth/change-password (authenticated)
  static Future<String?> changePassword(
    String currentPassword,
    String newPassword,
  ) async {
    try {
      await Api.instance.dio.post(
        '/api/auth/change-password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      );
      return null;
    } catch (e) {
      return Api.errorMessage(e);
    }
  }
}
