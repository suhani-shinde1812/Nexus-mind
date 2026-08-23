/// Nexus Mind Mobile - data models.
/// Mirrors the JSON shape returned by the FastAPI backend
/// (see backend/app/serializers.py / schemas.py).

class AuthTokens {
  final String accessToken;
  final String refreshToken;
  AuthTokens({required this.accessToken, required this.refreshToken});

  factory AuthTokens.fromJson(Map<String, dynamic> j) => AuthTokens(
        accessToken: j['access_token'],
        refreshToken: j['refresh_token'],
      );

  Map<String, dynamic> toJson() => {
        'access_token': accessToken,
        'refresh_token': refreshToken,
      };
}

class NexusUser {
  final String id;
  final String name;
  final String email;
  final String role;
  final String appRole;
  final String avatar;
  final int capacity;
  final int activeTasks;
  final List<String> skills;

  NexusUser({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    required this.appRole,
    required this.avatar,
    required this.capacity,
    required this.activeTasks,
    required this.skills,
  });

  factory NexusUser.fromJson(Map<String, dynamic> j) => NexusUser(
        id: j['id'],
        name: j['name'],
        email: j['email'],
        role: j['role'] ?? '',
        appRole: j['app_role'] ?? 'employee',
        avatar: j['avatar'] ?? '',
        capacity: j['capacity'] ?? 0,
        activeTasks: j['active_tasks'] ?? 0,
        skills: List<String>.from(j['skills'] ?? const []),
      );
}

class NexusTask {
  final String id;
  final String title;
  final String? project;
  final String? assignee;
  String status;
  final String priority;
  final List<String> dependsOn;
  final String dueDate;
  double aiRiskScore;
  String? riskReason;

  NexusTask({
    required this.id,
    required this.title,
    required this.project,
    required this.assignee,
    required this.status,
    required this.priority,
    required this.dependsOn,
    required this.dueDate,
    required this.aiRiskScore,
    required this.riskReason,
  });

  factory NexusTask.fromJson(Map<String, dynamic> j) => NexusTask(
        id: j['id'],
        title: j['title'],
        project: j['project'],
        assignee: j['assignee'],
        status: j['status'] ?? 'in_progress',
        priority: j['priority'] ?? 'Medium',
        dependsOn: List<String>.from(j['dependsOn'] ?? const []),
        dueDate: j['dueDate'] ?? '',
        aiRiskScore: (j['aiRiskScore'] ?? 0.1).toDouble(),
        riskReason: j['riskReason'],
      );
}

class NexusAlert {
  final String id;
  final String severity;
  final String title;
  final String message;
  final String? taskId;
  final bool read;
  final DateTime timestamp;

  NexusAlert({
    required this.id,
    required this.severity,
    required this.title,
    required this.message,
    required this.taskId,
    required this.read,
    required this.timestamp,
  });

  factory NexusAlert.fromJson(Map<String, dynamic> j) => NexusAlert(
        id: j['id'],
        severity: j['severity'] ?? 'info',
        title: j['title'] ?? '',
        message: j['message'] ?? '',
        taskId: j['taskId'],
        read: j['read'] ?? false,
        timestamp: DateTime.tryParse(j['timestamp'] ?? '') ?? DateTime.now(),
      );
}
