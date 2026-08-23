# Nexus Mind — Primary Flutter Application Architecture & Migration Plan

## 1. Vision & Architecture Paradigm
Elevate the Flutter codebase (`mobile/`) to become the **primary enterprise cross-platform client** for mobile, tablet, and desktop.

### Architectural Blueprint: Clean Architecture with Riverpod & GoRouter
```
mobile/lib/
  ├── core/
  │   ├── config/          # AppConfig, API endpoints, WebSocket URLs
  │   ├── networking/      # Dio client, Interceptors, JWT Token Refresh, Error handling
  │   ├── authentication/  # TokenStore, AuthGuard, MFA controller
  │   ├── routing/         # GoRouter definitions & route guards
  │   ├── theme/           # Material 3 Obsidian Dark & Clean Light Themes
  │   └── errors/          # Custom Failure classes & domain exceptions
  ├── data/
  │   ├── models/          # Freezed / JSON serializable DTOs
  │   ├── datasources/     # Remote (Dio + WebSockets) & Local (Drift/SharedPreferences)
  │   └── repositories/    # Repository implementations (Tasks, Projects, AI, Security, Meetings)
  ├── domain/
  │   ├── entities/        # Pure domain entities (TaskEntity, ProjectEntity, AiRiskEntity)
  │   └── repositories/    # Abstract repository interfaces
  ├── application/
  │   └── providers/       # Riverpod StateNotifier / AsyncNotifier providers
  └── presentation/
      ├── screens/
      │   ├── auth/        # LoginScreen, RegisterScreen, MfaScreen, DemoLoginScreen
      │   ├── dashboard/   # MainDashboardScreen (Health, KPIs, Quick Actions, Role Matrix)
      │   ├── projects/    # ProjectListScreen, ProjectDetailScreen, MilestoneScreen
      │   ├── tasks/       # TaskListScreen, KanbanScreen, TaskDetailScreen, TaskModal
      │   ├── graph/       # InteractiveGraphScreen (CustomPainter Force Graph)
      │   ├── ai_copilot/  # NexusAiCopilotScreen (Chat, Agent Stream, Tool Proposals)
      │   ├── knowledge/   # KnowledgeCenterScreen (Docs, Upload, RAG Search, Citations)
      │   ├── security/    # SecurityCenterScreen (Audit Logs, Sessions, Threat Radar)
      │   ├── analytics/   # AnalyticsScreen (FlChart Burndown, Capacity Heatmap)
      │   ├── meetings/    # MeetingsScreen (Schedule, Agenda, Video Bridge)
      │   ├── engineering/ # GitHubScreen (PRs, Commits, CI Status, Lead Times)
      │   └── settings/    # SettingsScreen, ProfileScreen, ArchitectureExplorerScreen
      └── widgets/
          ├── app_drawer.dart
          ├── responsive_scaffold.dart
          ├── task_card.dart
          ├── ai_hazard_pill.dart
          └── stat_card.dart
```

---

## 2. Key Screen & Module Deliverables
1. **Interactive Task Graph (`InteractiveGraphScreen`)**:
   - Implemented via Flutter `CustomPainter` with pan/zoom gestures (`InteractiveViewer`).
   - Visualizes tasks as nodes with status color borders and animated dashed vector dependency edges.
2. **5-Column Drag & Drop Kanban (`KanbanScreen`)**:
   - `DragTarget` and `Draggable` widgets for moving cards across Backlog, Ready, In Progress, Review, and Completed.
3. **Dedicated Nexus AI Copilot (`NexusAiCopilotScreen`)**:
   - Chat interface supporting multi-agent persona switching, structured subtask generation, What-If simulation queries, and actionable tool proposals.
4. **Security Center (`SecurityCenterScreen`)**:
   - Active session management, security risk gauge, chronological audit events, and suspicious login anomaly alerts.
5. **RAG Knowledge Hub (`KnowledgeCenterScreen`)**:
   - Document upload preview, semantic search bar, and citation source inspector.
