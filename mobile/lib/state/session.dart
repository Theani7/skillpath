import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/api_client.dart';

/// Global session state. Reads /api/auth/me on startup to restore
/// the cookie-backed session.
class Session extends ChangeNotifier {
  UserProfile? user;
  bool loading = true;

  bool get isAuthenticated => user != null;

  Future<void> restore() async {
    loading = true;
    notifyListeners();
    try {
      final res = await Api.instance.dio.get('/api/auth/me');
      if (res.statusCode == 200) {
        user = UserProfile.fromJson((res.data as Map).cast<String, dynamic>());
      } else {
        user = null;
      }
    } catch (_) {
      user = null;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<String?> login(String username, String password) async {
    try {
      final res = await Api.instance.dio.post(
        '/api/auth/login',
        // FastAPI OAuth2PasswordRequestForm: form-encoded, not JSON.
        data: {'username': username, 'password': password},
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );
      if (res.statusCode == 200) {
        await restore();
        return null;
      }
      return Api.errorMessage(res.data ?? 'Login failed');
    } catch (e) {
      return Api.errorMessage(e);
    }
  }

  Future<void> logout() async {
    try {
      await Api.instance.dio.post('/api/auth/logout');
    } catch (_) {
      /* noop */
    }
    Api.instance.clearSession();
    user = null;
    notifyListeners();
  }
}
