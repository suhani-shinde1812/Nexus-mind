import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/config/app_config.dart';
import '../core/networking/api_client.dart';
import '../domain/entities/models.dart';


// --------------------------------------------------------------------------
// Auth State & Controller
// --------------------------------------------------------------------------
class AuthState {
  final UserModel? user;
  final bool isLoading;
  final String? error;
  final bool mfaRequired;
  final String? tempToken;

  AuthState({this.user, this.isLoading = false, this.error, this.mfaRequired = false, this.tempToken});

  AuthState copyWith({
    UserModel? user,
    bool? isLoading,
    String? error,
    bool? mfaRequired,
    String? tempToken,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      mfaRequired: mfaRequired ?? this.mfaRequired,
      tempToken: tempToken ?? this.tempToken,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient _api = ApiClient();

  AuthNotifier() : super(AuthState());

  Future<void> register(Map<String, dynamic> data) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.post('/api/auth/register', data);
      if (res['access_token'] != null) {
        await _api.saveTokens(res['access_token'], res['refresh_token'] ?? '');
        final boot = await _api.get('/api/bootstrap');
        state = state.copyWith(
          user: UserModel.fromJson(boot['currentUser']),
          isLoading: false,
        );
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.postForm('/api/auth/login', {'username': email, 'password': password});
      if (res['mfa_required'] == true) {
        state = state.copyWith(isLoading: false, mfaRequired: true, tempToken: res['temp_token']);
        return;
      }
      await _api.saveTokens(res['access_token'], res['refresh_token']);
      final boot = await _api.get('/api/bootstrap');
      state = state.copyWith(
        user: UserModel.fromJson(boot['currentUser']),
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void loginDemo(String role) {
    UserModel user;
    if (role == 'admin') {
      user = UserModel(id: 'u6', name: 'Elena Rostova', email: 'elena.rostova@nexusmind.ai', role: 'Administrator', appRole: 'admin', avatar: 'ER', capacity: 30, activeTasks: 0, skills: ['Security', 'OAuth']);
    } else if (role == 'project_manager') {
      user = UserModel(id: 'u5', name: 'Marcus Chen', email: 'marcus.chen@nexusmind.ai', role: 'Project Manager', appRole: 'project_manager', avatar: 'MC', capacity: 50, activeTasks: 2, skills: ['Planning']);
    } else if (role == 'employee') {
      user = UserModel(id: 'u1', name: 'Alex Vance', email: 'alex.vance@nexusmind.ai', role: 'Frontend Lead', appRole: 'employee', avatar: 'AV', capacity: 80, activeTasks: 3, skills: ['Frontend', 'React']);
    } else {
      user = UserModel(id: 'u2', name: 'Sarah Jenkins', email: 'sarah.jenkins@nexusmind.ai', role: 'Team Lead', appRole: 'team_lead', avatar: 'SJ', capacity: 60, activeTasks: 2, skills: ['Management']);
    }
    state = state.copyWith(user: user, isLoading: false);
  }

  void logout() {
    _api.clearTokens();
    state = AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) => AuthNotifier());

// --------------------------------------------------------------------------
// Workspace State & Controller
// --------------------------------------------------------------------------
class WorkspaceState {
  final List<TaskModel> tasks;
  final List<ProjectModel> projects;
  final List<UserModel> users;
  final List<MeetingModel> meetings;
  final ThreatRadarModel? threatRadar;
  final EngineeringMetricsModel? engineeringMetrics;
  final bool isLoading;

  WorkspaceState({
    this.tasks = const [],
    this.projects = const [],
    this.users = const [],
    this.meetings = const [],
    this.threatRadar,
    this.engineeringMetrics,
    this.isLoading = false,
  });

  WorkspaceState copyWith({
    List<TaskModel>? tasks,
    List<ProjectModel>? projects,
    List<UserModel>? users,
    List<MeetingModel>? meetings,
    ThreatRadarModel? threatRadar,
    EngineeringMetricsModel? engineeringMetrics,
    bool? isLoading,
  }) {
    return WorkspaceState(
      tasks: tasks ?? this.tasks,
      projects: projects ?? this.projects,
      users: users ?? this.users,
      meetings: meetings ?? this.meetings,
      threatRadar: threatRadar ?? this.threatRadar,
      engineeringMetrics: engineeringMetrics ?? this.engineeringMetrics,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class WorkspaceNotifier extends StateNotifier<WorkspaceState> {
  final ApiClient _api = ApiClient();

  WorkspaceNotifier() : super(WorkspaceState()) {
    loadWorkspace();
  }

  Future<void> loadWorkspace() async {
    state = state.copyWith(isLoading: true);
    try {
      final res = await _api.get('/api/bootstrap');
      final tasks = (res['tasks'] as List?)?.map((e) => TaskModel.fromJson(e)).toList() ?? [];
      final projects = (res['projects'] as List?)?.map((e) => ProjectModel.fromJson(e)).toList() ?? [];
      final users = (res['users'] as List?)?.map((e) => UserModel.fromJson(e)).toList() ?? [];
      final meetings = (res['meetings'] as List?)?.map((e) => MeetingModel.fromJson(e)).toList() ?? [];
      final radar = res['securityThreat'] != null ? ThreatRadarModel.fromJson(res['securityThreat']) : null;
      final eng = res['engineeringMetrics'] != null ? EngineeringMetricsModel.fromJson(res['engineeringMetrics']) : null;

      state = state.copyWith(
        tasks: tasks,
        projects: projects,
        users: users,
        meetings: meetings,
        threatRadar: radar,
        engineeringMetrics: eng,
        isLoading: false,
      );
    } catch (_) {
      // Fallback demo state
      _loadFallbackState();
    }
  }

  void _loadFallbackState() {
    state = state.copyWith(
      tasks: [
        TaskModel(id: 'TASK-101', title: 'Cloud Infrastructure Provisioning (Terraform)', description: 'AWS VPC & ECS cluster setup', status: 'done', priority: 'High', dependsOn: [], x: 120, y: 180, dueDate: '2026-07-20', aiRiskScore: 0.1, assignee: 'Devon Reed'),
        TaskModel(id: 'TASK-102', title: 'PostgreSQL Database Schema & Migration Script', description: 'Partitioned relational schema', status: 'in_progress', priority: 'Critical', dependsOn: ['TASK-101'], x: 300, y: 140, dueDate: '2026-07-28', aiRiskScore: 0.85, assignee: 'Devon Reed', riskReason: 'Capacity overload 110%'),
        TaskModel(id: 'TASK-103', title: 'OAuth2 Authentication API Gateway', description: 'JWT refresh & MFA endpoints', status: 'in_progress', priority: 'High', dependsOn: ['TASK-102'], x: 480, y: 140, dueDate: '2026-07-30', aiRiskScore: 0.75, assignee: 'Alex Vance'),
        TaskModel(id: 'TASK-104', title: 'React Dashboard UI & Role Authorization Views', description: 'Enterprise UI matrix', status: 'blocked', priority: 'High', dependsOn: ['TASK-103'], x: 660, y: 200, dueDate: '2026-08-05', aiRiskScore: 0.92, assignee: 'Alex Vance', riskReason: 'Blocked by prerequisite TASK-103'),
      ],
      projects: [
        ProjectModel(id: 'p1', name: 'Sprint Alpha - Cloud Migration', lead: 'Sarah Jenkins', deadline: '2026-08-15', progress: 65),
        ProjectModel(id: 'p2', name: 'Mobile App v2.0', lead: 'Alex Vance', deadline: '2026-09-01', progress: 40),
      ],
      threatRadar: ThreatRadarModel(threatScore: 24, threatLevel: 'SECURE', activeThreatsCount: 0, failedLogins24h: 0),
      engineeringMetrics: EngineeringMetricsModel(repoCount: 1, openPrsCount: 0, avgPrCycleTimeHours: 5.35, commitsLast7d: 14, ciSuccessRate: 100.0, deploymentFrequency: '4.2 / day'),
      isLoading: false,
    );
  }

  Future<void> updateTaskStatus(String taskId, String newStatus) async {
    final updated = state.tasks.map((t) {
      if (t.id == taskId) {
        return TaskModel(
          id: t.id, title: t.title, description: t.description, project: t.project,
          assignee: t.assignee, status: newStatus, priority: t.priority,
          dependsOn: t.dependsOn, x: t.x, y: t.y, dueDate: t.dueDate,
          aiRiskScore: newStatus == 'done' ? 0.05 : t.aiRiskScore, riskReason: t.riskReason,
        );
      }
      return t;
    }).toList();
    state = state.copyWith(tasks: updated);
    _api.patch('/api/tasks/$taskId/status', {'status': newStatus}).catchError((_) => {});
  }

  Future<void> createTask(Map<String, dynamic> taskData) async {
    try {
      final res = await _api.post('/api/tasks', taskData);
      final newTask = TaskModel.fromJson(res);
      state = state.copyWith(tasks: [newTask, ...state.tasks]);
    } catch (_) {
      final localId = 'TASK-${100 + state.tasks.length + 1}';
      final localTask = TaskModel(
        id: localId,
        title: taskData['title'] ?? 'New Task',
        description: taskData['description'] ?? '',
        project: taskData['project'] ?? 'General',
        status: taskData['status'] ?? 'in_progress',
        priority: taskData['priority'] ?? 'Medium',
        assignee: taskData['assignee'],
        dueDate: taskData['due_date'] ?? '2026-08-30',
        aiRiskScore: 0.1,
      );
      state = state.copyWith(tasks: [localTask, ...state.tasks]);
    }
  }

  Future<void> createMeeting(Map<String, dynamic> meetingData) async {
    try {
      final res = await _api.post('/api/meetings', meetingData);
      final newMeeting = MeetingModel.fromJson(res);
      state = state.copyWith(meetings: [newMeeting, ...state.meetings]);
    } catch (_) {
      final localId = 'MTG-${1000 + state.meetings.length + 1}';
      final localM = MeetingModel(
        id: localId,
        title: meetingData['title'] ?? 'Team Sync',
        project: meetingData['project'] ?? 'General',
        date: meetingData['date'] ?? '2026-08-25',
        time: meetingData['time'] ?? '10:00',
        duration: meetingData['duration'] ?? '30',
        attendees: (meetingData['attendees'] as List?)?.map((e) => e.toString()).toList() ?? [],
        agenda: meetingData['agenda'] ?? '',
        organizer: meetingData['organizer'] ?? 'Organizer',
        status: 'scheduled',
        link: 'https://meet.jit.si/NexusMind-$localId',
      );
      state = state.copyWith(meetings: [localM, ...state.meetings]);
    }
  }
}

final workspaceProvider = StateNotifierProvider<WorkspaceNotifier, WorkspaceState>((ref) => WorkspaceNotifier());
