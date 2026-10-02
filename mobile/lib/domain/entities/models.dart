/// Enterprise domain models for Nexus Mind Mobile & Desktop client.

class UserModel {
  final String id;
  final String name;
  final String email;
  final String role;
  final String appRole;
  final String avatar;
  final int capacity;
  final int activeTasks;
  final List<String> skills;
  final bool mfaEnabled;

  UserModel({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    required this.appRole,
    required this.avatar,
    required this.capacity,
    required this.activeTasks,
    required this.skills,
    this.mfaEnabled = false,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      name: json['name'] ?? 'User',
      email: json['email'] ?? '',
      role: json['role'] ?? 'Member',
      appRole: json['app_role'] ?? json['appRole'] ?? 'employee',
      avatar: json['avatar'] ?? 'NM',
      capacity: json['capacity'] ?? 0,
      activeTasks: json['active_tasks'] ?? json['activeTasks'] ?? 0,
      skills: (json['skills'] as List?)?.map((e) => e.toString()).toList() ?? const <String>[],
      mfaEnabled: json['mfa_enabled'] ?? json['mfaEnabled'] ?? false,
    );
  }
}

class ProjectModel {
  final String id;
  final String name;
  final String lead;
  final String deadline;
  final int progress;

  ProjectModel({
    required this.id,
    required this.name,
    required this.lead,
    required this.deadline,
    required this.progress,
  });

  factory ProjectModel.fromJson(Map<String, dynamic> json) {
    return ProjectModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      lead: json['lead'] ?? '',
      deadline: json['deadline'] ?? '',
      progress: json['progress'] ?? 0,
    );
  }
}

class TaskModel {
  final String id;
  final String title;
  final String description;
  final String? project;
  final String? assignee;
  final String status;
  final String priority;
  final List<String> dependsOn;
  final double x;
  final double y;
  final String dueDate;
  final double aiRiskScore;
  final String? riskReason;

  TaskModel({
    required this.id,
    required this.title,
    required this.description,
    this.project,
    this.assignee,
    required this.status,
    required this.priority,
    required this.dependsOn,
    required this.x,
    required this.y,
    required this.dueDate,
    required this.aiRiskScore,
    this.riskReason,
  });

  factory TaskModel.fromJson(Map<String, dynamic> json) {
    return TaskModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      project: json['project'],
      assignee: json['assignee'],
      status: json['status'] ?? 'in_progress',
      priority: json['priority'] ?? 'Medium',
      dependsOn: (json['dependsOn'] as List? ?? json['depends_on'] as List?)?.map((e) => e.toString()).toList() ?? const <String>[],
      x: (json['x'] as num?)?.toDouble() ?? 400.0,
      y: (json['y'] as num?)?.toDouble() ?? 250.0,
      dueDate: json['dueDate'] ?? json['due_date'] ?? '',
      aiRiskScore: (json['aiRiskScore'] as num? ?? json['ai_risk_score'] as num?)?.toDouble() ?? 0.1,
      riskReason: json['riskReason'] ?? json['risk_reason'],
    );
  }
}

class TaskCommentModel {
  final String id;
  final String taskId;
  final String authorId;
  final String authorName;
  final String authorAvatar;
  final String content;
  final String createdAt;

  TaskCommentModel({
    required this.id,
    required this.taskId,
    required this.authorId,
    required this.authorName,
    required this.authorAvatar,
    required this.content,
    required this.createdAt,
  });

  factory TaskCommentModel.fromJson(Map<String, dynamic> json) {
    return TaskCommentModel(
      id: json['id'] ?? '',
      taskId: json['task_id'] ?? json['taskId'] ?? '',
      authorId: json['author_id'] ?? json['authorId'] ?? '',
      authorName: json['author_name'] ?? json['authorName'] ?? 'Teammate',
      authorAvatar: json['author_avatar'] ?? json['authorAvatar'] ?? 'AV',
      content: json['content'] ?? '',
      createdAt: json['created_at'] ?? json['createdAt'] ?? '',
    );
  }
}

class ThreatRadarModel {
  final int threatScore;
  final String threatLevel;
  final int activeThreatsCount;
  final int failedLogins24h;

  ThreatRadarModel({
    required this.threatScore,
    required this.threatLevel,
    required this.activeThreatsCount,
    required this.failedLogins24h,
  });

  factory ThreatRadarModel.fromJson(Map<String, dynamic> json) {
    return ThreatRadarModel(
      threatScore: json['threat_score'] ?? json['threatScore'] ?? 15,
      threatLevel: json['threat_level'] ?? json['threatLevel'] ?? 'SECURE',
      activeThreatsCount: json['active_threats_count'] ?? json['activeThreatsCount'] ?? 0,
      failedLogins24h: json['failed_logins_24h'] ?? json['failedLogins24h'] ?? 0,
    );
  }
}

class EngineeringMetricsModel {
  final int repoCount;
  final int openPrsCount;
  final double avgPrCycleTimeHours;
  final int commitsLast7d;
  final double ciSuccessRate;
  final String deploymentFrequency;

  EngineeringMetricsModel({
    required this.repoCount,
    required this.openPrsCount,
    required this.avgPrCycleTimeHours,
    required this.commitsLast7d,
    required this.ciSuccessRate,
    required this.deploymentFrequency,
  });

  factory EngineeringMetricsModel.fromJson(Map<String, dynamic> json) {
    return EngineeringMetricsModel(
      repoCount: json['repo_count'] ?? json['repoCount'] ?? 1,
      openPrsCount: json['open_prs_count'] ?? json['openPrsCount'] ?? 0,
      avgPrCycleTimeHours: (json['avg_pr_cycle_time_hours'] as num? ?? json['avgPrCycleTimeHours'] as num?)?.toDouble() ?? 5.3,
      commitsLast7d: json['commits_last_7d'] ?? json['commitsLast7d'] ?? 14,
      ciSuccessRate: (json['ci_success_rate'] as num? ?? json['ciSuccessRate'] as num?)?.toDouble() ?? 98.0,
      deploymentFrequency: json['deployment_frequency'] ?? json['deploymentFrequency'] ?? '4.2 / day',
    );
  }
}

class DocumentModel {
  final String id;
  final String title;
  final String filename;
  final String fileType;
  final int fileSizeBytes;
  final String summary;
  final int chunkCount;

  DocumentModel({
    required this.id,
    required this.title,
    required this.filename,
    required this.fileType,
    required this.fileSizeBytes,
    required this.summary,
    required this.chunkCount,
  });

  factory DocumentModel.fromJson(Map<String, dynamic> json) {
    return DocumentModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      filename: json['filename'] ?? '',
      fileType: json['file_type'] ?? json['fileType'] ?? 'md',
      fileSizeBytes: json['file_size_bytes'] ?? json['fileSizeBytes'] ?? 0,
      summary: json['summary'] ?? '',
      chunkCount: json['chunk_count'] ?? json['chunkCount'] ?? 1,
    );
  }
}

class CitationModel {
  final String documentTitle;
  final String section;
  final int page;
  final String snippet;
  final double score;

  CitationModel({
    required this.documentTitle,
    required this.section,
    required this.page,
    required this.snippet,
    required this.score,
  });

  factory CitationModel.fromJson(Map<String, dynamic> json) {
    return CitationModel(
      documentTitle: json['document_title'] ?? json['documentTitle'] ?? 'Engineering Spec',
      section: json['section'] ?? 'Section',
      page: json['page'] ?? 1,
      snippet: json['snippet'] ?? '',
      score: (json['score'] as num?)?.toDouble() ?? 0.8,
    );
  }
}

class MeetingModel {
  final String id;
  final String title;
  final String project;
  final String date;
  final String time;
  final String duration;
  final List<String> attendees;
  final String agenda;
  final String organizer;
  final String status;
  final String link;

  MeetingModel({
    required this.id,
    required this.title,
    required this.project,
    required this.date,
    required this.time,
    required this.duration,
    required this.attendees,
    required this.agenda,
    required this.organizer,
    required this.status,
    required this.link,
  });

  factory MeetingModel.fromJson(Map<String, dynamic> json) {
    return MeetingModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      project: json['project'] ?? 'General',
      date: json['date'] ?? '',
      time: json['time'] ?? '',
      duration: json['duration'] ?? '30',
      attendees: (json['attendees'] as List?)?.map((e) => e.toString()).toList() ?? const <String>[],
      agenda: json['agenda'] ?? '',
      organizer: json['organizer'] ?? 'Team Lead',
      status: json['status'] ?? 'scheduled',
      link: json['link'] ?? '',
    );
  }
}
