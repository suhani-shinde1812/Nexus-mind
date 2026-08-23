import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../app_state.dart';
import '../models.dart';
import 'login_screen.dart';
import 'notifications_screen.dart';
import 'task_detail_screen.dart';

class TaskListScreen extends StatefulWidget {
  const TaskListScreen({super.key});

  @override
  State<TaskListScreen> createState() => _TaskListScreenState();
}

class _TaskListScreenState extends State<TaskListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => context.read<AppState>().bootstrap());
  }

  Color _riskColor(double score) {
    if (score >= 0.7) return Colors.redAccent;
    if (score >= 0.4) return Colors.orangeAccent;
    return Colors.greenAccent;
  }

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF11162B),
        title: Text(appState.currentUser != null ? 'Hi, ${appState.currentUser!.name.split(' ').first}' : 'Nexus Mind'),
        actions: [
          IconButton(
            icon: Badge(
              label: Text('${appState.alerts.where((a) => !a.read).length}'),
              isLabelVisible: appState.alerts.any((a) => !a.read),
              child: const Icon(Icons.notifications_outlined),
            ),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const NotificationsScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await appState.logout();
              if (context.mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                  (route) => false,
                );
              }
            },
          ),
        ],
      ),
      body: appState.loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: appState.bootstrap,
              child: ListView.builder(
                padding: const EdgeInsets.all(12),
                itemCount: appState.tasks.length,
                itemBuilder: (context, i) {
                  final NexusTask task = appState.tasks[i];
                  return Card(
                    color: const Color(0xFF151B33),
                    margin: const EdgeInsets.only(bottom: 10),
                    child: ListTile(
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => TaskDetailScreen(taskId: task.id)),
                      ),
                      title: Text(task.title, style: const TextStyle(color: Colors.white, fontSize: 14)),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          '${task.assignee ?? "Unassigned"} · ${task.status} · due ${task.dueDate}',
                          style: const TextStyle(color: Colors.white54, fontSize: 12),
                        ),
                      ),
                      trailing: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CircleAvatar(
                            radius: 6,
                            backgroundColor: _riskColor(task.aiRiskScore),
                          ),
                          const SizedBox(height: 4),
                          Text('${(task.aiRiskScore * 100).round()}%',
                              style: const TextStyle(color: Colors.white38, fontSize: 10)),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
    );
  }
}
