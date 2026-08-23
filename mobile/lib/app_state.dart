/// Nexus Mind Mobile - lightweight app-wide state (Provider ChangeNotifier).
/// Scoped-down mirror of the web app's state.js: hydrates from
/// GET /api/bootstrap, applies optimistic local updates, and merges live
/// WebSocket events -- same architecture, same backend contract.
import 'package:flutter/foundation.dart';

import 'models.dart';
import 'services/api_service.dart';
import 'services/realtime_service.dart';

class AppState extends ChangeNotifier {
  AppState({required this.api, required this.realtime}) {
    realtime.events.listen(_handleEvent);
  }

  final ApiService api;
  final RealtimeService realtime;

  NexusUser? currentUser;
  List<NexusTask> tasks = [];
  List<NexusAlert> alerts = [];
  bool loading = false;
  String? error;

  bool get isAuthenticated => api.isAuthenticated;

  Future<void> login(String email, String password) async {
    await api.login(email, password);
    await bootstrap();
  }

  Future<void> logout() async {
    await api.logout();
    realtime.disconnect();
    currentUser = null;
    tasks = [];
    alerts = [];
    notifyListeners();
  }

  Future<void> bootstrap() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      final data = await api.bootstrap();
      currentUser = NexusUser.fromJson(data['currentUser']);
      tasks = (data['tasks'] as List).map((e) => NexusTask.fromJson(e)).toList();
      alerts = (data['aiAlerts'] as List).map((e) => NexusAlert.fromJson(e)).toList();
      realtime.connect();
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> updateTaskStatus(String taskId, String status) async {
    final idx = tasks.indexWhere((t) => t.id == taskId);
    final previous = idx >= 0 ? tasks[idx].status : null;
    if (idx >= 0) {
      tasks[idx].status = status;
      notifyListeners();
    }
    try {
      await api.updateTaskStatus(taskId, status);
    } catch (e) {
      // Revert optimistic update on failure.
      if (idx >= 0 && previous != null) {
        tasks[idx].status = previous;
        notifyListeners();
      }
      rethrow;
    }
  }

  void _handleEvent(Map<String, dynamic> msg) {
    final type = msg['type'];
    final payload = msg['payload'] as Map<String, dynamic>?;
    if (payload == null) return;

    switch (type) {
      case 'task_created':
      case 'task_updated':
        final task = NexusTask.fromJson(payload);
        final idx = tasks.indexWhere((t) => t.id == task.id);
        if (idx >= 0) {
          tasks[idx] = task;
        } else {
          tasks.add(task);
        }
        notifyListeners();
        break;
      case 'alert_created':
        final alert = NexusAlert.fromJson(payload);
        if (!alerts.any((a) => a.id == alert.id)) {
          alerts.insert(0, alert);
          notifyListeners();
        }
        break;
    }
  }
}
