import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'application/providers.dart';
import 'core/theme/app_theme.dart';
import 'presentation/screens/ai_copilot/nexus_ai_copilot_screen.dart';
import 'presentation/screens/auth/login_screen.dart';
import 'presentation/screens/dashboard/main_dashboard_screen.dart';
import 'presentation/screens/engineering/github_screen.dart';
import 'presentation/screens/graph/interactive_graph_screen.dart';
import 'presentation/screens/knowledge/knowledge_center_screen.dart';
import 'presentation/screens/meetings/meetings_screen.dart';
import 'presentation/screens/security/security_center_screen.dart';
import 'presentation/screens/settings/architecture_explorer_screen.dart';
import 'presentation/screens/tasks/kanban_screen.dart';
import 'presentation/widgets/responsive_scaffold.dart';


void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: NexusMindEnterpriseApp()));
}

class NexusMindEnterpriseApp extends ConsumerWidget {
  const NexusMindEnterpriseApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return MaterialApp(
      title: 'Nexus Mind Enterprise',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: authState.user == null ? const LoginScreen() : const EnterpriseShell(),
    );
  }
}

class EnterpriseShell extends StatefulWidget {
  const EnterpriseShell({super.key});

  @override
  State<EnterpriseShell> createState() => _EnterpriseShellState();
}

class _EnterpriseShellState extends State<EnterpriseShell> {
  int _currentIndex = 0;

  final List<String> _titles = [
    'Operations Dashboard',
    'Live Task Graph & Critical Path',
    'Drag & Drop Kanban Board',
    'Autonomous AI Swarm Copilot',
    'Cybersecurity Center & Threat Radar',
    'RAG Knowledge Base & Citations',
    'Engineering Intelligence & CI/CD',
    'Video Bridge & Standups',
    'Architecture Explorer',
  ];

  @override
  Widget build(BuildContext context) {
    final screens = [
      MainDashboardScreen(onNavigate: (index) => setState(() => _currentIndex = index)),
      const InteractiveGraphScreen(),
      const KanbanScreen(),
      const NexusAiCopilotScreen(),
      const SecurityCenterScreen(),
      const KnowledgeCenterScreen(),
      const GitHubScreen(),
      const MeetingsScreen(),
      const ArchitectureExplorerScreen(),
    ];

    return ResponsiveScaffold(
      selectedIndex: _currentIndex,
      onDestinationSelected: (index) => setState(() => _currentIndex = index),
      title: _titles[_currentIndex],
      body: screens[_currentIndex],
    );
  }
}
