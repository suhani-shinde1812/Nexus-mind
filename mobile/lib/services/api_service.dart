/// Nexus Mind Mobile - API client.
/// Same backend contract as the web app's src/js/api.js -- talks to the
/// FastAPI service over HTTP, storing JWTs in SharedPreferences.
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../models.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  ApiService({required this.baseUrl});

  /// e.g. https://api.nexusmind.ai or http://10.0.2.2:8000 for the Android emulator
  final String baseUrl;

  String? _accessToken;
  String? _refreshToken;

  static const _kAccess = 'nexus_access_token';
  static const _kRefresh = 'nexus_refresh_token';

  bool get isAuthenticated => _accessToken != null;

  Future<void> loadTokensFromStorage() async {
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString(_kAccess);
    _refreshToken = prefs.getString(_kRefresh);
  }

  Future<void> _saveTokens(AuthTokens tokens) async {
    _accessToken = tokens.accessToken;
    _refreshToken = tokens.refreshToken;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_kAccess, tokens.accessToken);
    await prefs.setString(_kRefresh, tokens.refreshToken);
  }

  Future<void> logout() async {
    _accessToken = null;
    _refreshToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_kAccess);
    await prefs.remove(_kRefresh);
  }

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Map<String, String> _headers({bool auth = true, bool form = false}) => {
        if (!form) 'Content-Type': 'application/json',
        if (auth && _accessToken != null) 'Authorization': 'Bearer $_accessToken',
      };

  Future<dynamic> _request(
    String path, {
    String method = 'GET',
    Object? body,
    bool auth = true,
    bool form = false,
  }) async {
    Future<http.Response> send() {
      final uri = _uri(path);
      final headers = _headers(auth: auth, form: form);
      final encodedBody = form ? body as String? : (body != null ? jsonEncode(body) : null);
      switch (method) {
        case 'POST':
          return http.post(uri, headers: headers, body: encodedBody);
        case 'PATCH':
          return http.patch(uri, headers: headers, body: encodedBody);
        default:
          return http.get(uri, headers: headers);
      }
    }

    var res = await send();

    if (res.statusCode == 401 && auth && _refreshToken != null && path != '/api/auth/refresh') {
      final refreshed = await _tryRefresh();
      if (refreshed) res = await send();
    }

    if (res.statusCode >= 400) {
      String detail = 'Request failed: ${res.statusCode}';
      try {
        detail = jsonDecode(res.body)['detail'] ?? detail;
      } catch (_) {}
      throw ApiException(detail);
    }
    if (res.body.isEmpty) return null;
    return jsonDecode(res.body);
  }

  Future<bool> _tryRefresh() async {
    try {
      final data = await _request(
        '/api/auth/refresh',
        method: 'POST',
        body: {'refresh_token': _refreshToken},
        auth: false,
      );
      await _saveTokens(AuthTokens.fromJson(data));
      return true;
    } catch (_) {
      await logout();
      return false;
    }
  }

  // ---- Auth ----
  Future<void> login(String email, String password) async {
    final data = await _request(
      '/api/auth/login',
      method: 'POST',
      auth: false,
      form: true,
      body: 'username=${Uri.encodeComponent(email)}&password=${Uri.encodeComponent(password)}',
    );
    await _saveTokens(AuthTokens.fromJson(data));
  }

  Future<NexusUser> me() async => NexusUser.fromJson(await _request('/api/auth/me'));

  // ---- Bootstrap ----
  Future<Map<String, dynamic>> bootstrap() async => await _request('/api/bootstrap');

  // ---- Tasks ----
  Future<List<NexusTask>> listTasks() async {
    final data = await _request('/api/tasks') as List;
    return data.map((e) => NexusTask.fromJson(e)).toList();
  }

  Future<NexusTask> updateTaskStatus(String taskId, String status) async {
    final data = await _request('/api/tasks/$taskId/status', method: 'PATCH', body: {'status': status});
    return NexusTask.fromJson(data);
  }

  Future<List<NexusAlert>> listAlerts() async {
    final data = await _request('/api/alerts') as List;
    return data.map((e) => NexusAlert.fromJson(e)).toList();
  }

  // ---- Push ----
  Future<void> registerPushToken(String token) async {
    await _request(
      '/api/users/me/push-token?token=${Uri.encodeComponent(token)}&platform=mobile',
      method: 'POST',
    );
  }

  String get wsUrl {
    final wsBase = baseUrl.replaceFirst('http', 'ws');
    return '$wsBase/ws?token=${Uri.encodeComponent(_accessToken ?? '')}';
  }
}
