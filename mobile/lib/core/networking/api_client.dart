import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  late final Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  String? _accessToken;
  String? _refreshToken;

  bool get isAuthenticated => _accessToken != null;
  String? get token => _accessToken;

  ApiClient._internal() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    // Authentication & Auto-Refresh Interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          if (_accessToken != null) {
            options.headers['Authorization'] = 'Bearer $_accessToken';
          }
          return handler.next(options);
        },
        onError: (DioException error, handler) async {
          if (error.response?.statusCode == 401 && _refreshToken != null) {
            try {
              // Attempt token refresh
              final refreshDio = Dio(BaseOptions(baseUrl: AppConfig.baseUrl));
              final res = await refreshDio.post(
                '/api/auth/refresh',
                data: {'refresh_token': _refreshToken},
              );

              if (res.statusCode == 200 && res.data != null) {
                final newAccess = res.data['access_token'] as String;
                final newRefresh = res.data['refresh_token'] as String;
                await saveTokens(newAccess, newRefresh);

                // Retry original request
                final opts = Options(
                  method: error.requestOptions.method,
                  headers: {
                    ...error.requestOptions.headers,
                    'Authorization': 'Bearer $newAccess',
                  },
                );
                final retryRes = await _dio.request(
                  error.requestOptions.path,
                  options: opts,
                  data: error.requestOptions.data,
                  queryParameters: error.requestOptions.queryParameters,
                );
                return handler.resolve(retryRes);
              }
            } catch (_) {
              await clearTokens();
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<void> init() async {
    try {
      _accessToken = await _storage.read(key: 'access_token');
      _refreshToken = await _storage.read(key: 'refresh_token');
    } catch (_) {
      // Fallback
    }
  }

  Future<void> saveTokens(String access, String refresh) async {
    _accessToken = access;
    _refreshToken = refresh;
    try {
      await _storage.write(key: 'access_token', value: access);
      await _storage.write(key: 'refresh_token', value: refresh);
    } catch (_) {
      // Fallback
    }
  }

  Future<void> clearTokens() async {
    _accessToken = null;
    _refreshToken = null;
    try {
      await _storage.delete(key: 'access_token');
      await _storage.delete(key: 'refresh_token');
    } catch (_) {
      // Fallback
    }
  }

  Future<dynamic> get(String path) async {
    try {
      final res = await _dio.get(path);
      return res.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? e.message);
    }
  }

  Future<dynamic> post(String path, dynamic body) async {
    try {
      final res = await _dio.post(path, data: body);
      return res.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? e.message);
    }
  }

  Future<dynamic> postForm(String path, Map<String, dynamic> data) async {
    try {
      final formData = FormData.fromMap(data);
      final res = await _dio.post(path, data: formData);
      return res.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? e.message);
    }
  }


  Future<dynamic> put(String path, dynamic body) async {
    try {
      final res = await _dio.put(path, data: body);
      return res.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? e.message);
    }
  }

  Future<dynamic> patch(String path, dynamic body) async {
    try {
      final res = await _dio.patch(path, data: body);
      return res.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? e.message);
    }
  }

  Future<dynamic> delete(String path) async {
    try {
      final res = await _dio.delete(path);
      return res.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? e.message);
    }
  }
}
