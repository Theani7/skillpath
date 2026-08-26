import 'package:dio/dio.dart';
import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:path_provider/path_provider.dart';

/// HTTP client wired to the FastAPI backend.
///
/// Auth is cookie-based (httpOnly `skillpath_access` + `skillpath_refresh`
/// set by /api/auth/login). A persistent CookieJar keeps the session alive
/// across app restarts. On 401 we try one silent refresh, then retry.
class Api {
  Api._();
  static final Api instance = Api._();

  late final Dio dio;
  late final PersistCookieJar _cookieJar;

  bool _refreshing = false;

  static Future<Api> init(String baseUrl) async {
    final api = instance;
    final dir = await defaultCookieDir();
    api._cookieJar = PersistCookieJar(storage: FileStorage('$dir/cookies'));
    final dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 20),
        receiveTimeout: const Duration(seconds: 90), // AI analysis is slow
        followRedirects: true,
      ),
    );
    dio.interceptors.add(
      InterceptorsWrapper(
        onError: (e, handler) async {
          final status = e.response?.statusCode;
          final path = e.requestOptions.path;
          if (status == 401 &&
              !path.contains('/auth/me') &&
              !path.contains('/auth/login') &&
              !path.contains('/auth/refresh') &&
              !api._refreshing) {
            final retried = e.requestOptions.extra['__retried'] == true;
            if (!retried) {
              final ok = await api._tryRefresh();
              if (ok) {
                final opts = e.requestOptions..extra['__retried'] = true;
                try {
                  final response = await api.dio.fetch(opts);
                  return handler.resolve(response);
                } on DioException catch (retryErr) {
                  return handler.next(retryErr);
                }
              }
            }
          }
          return handler.next(e);
        },
      ),
    );
    dio.interceptors.add(CookieManager(api._cookieJar));
    api.dio = dio;
    return api;
  }

  Future<bool> _tryRefresh() async {
    _refreshing = true;
    try {
      final res = await dio.post('/api/auth/refresh');
      return res.statusCode == 200;
    } catch (_) {
      return false;
    } finally {
      _refreshing = false;
    }
  }

  /// Extract a human-readable message from a FastAPI error response
  /// (`{"detail": "..."}` or `{"detail": [{"msg": ...}]}`).
  static String errorMessage(Object error) {
    if (error is DioException) {
      final data = error.response?.data;
      if (data is Map) {
        final detail = data['detail'];
        if (detail is String) return detail;
        if (detail is List && detail.isNotEmpty) {
          final first = detail.first;
          if (first is Map && first['msg'] is String) {
            return first['msg'] as String;
          }
        }
      }
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.connectionError:
          return 'Cannot reach the server. Check your connection.';
        case DioExceptionType.receiveTimeout:
        case DioExceptionType.sendTimeout:
          return 'The server took too long. Try again.';
        default:
          return 'Something went wrong. Please try again.';
      }
    }
    return 'Something went wrong. Please try again.';
  }

  void clearSession() => _cookieJar.deleteAll();
}

Future<String> defaultCookieDir() async {
  final dir = await getApplicationSupportDirectory();
  return dir.path;
}
