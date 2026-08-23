import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../app_state.dart';

class TaskDetailScreen extends StatelessWidget {
  const TaskDetailScreen({super.key, required this.taskId});
  final String taskId;

  static const _statuses = ['in_progress', 'blocked', 'done'];

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();
    final task = appState.tasks.firstWhere((t) => t.id == taskId);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1F),
      appBar: AppBar(backgroundColor: const Color(0xFF11162B), title: Text(task.id)),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(task.title, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _row('Project', task.project ?? '—'),
            _row('Assignee', task.assignee ?? 'Unassigned'),
            _row('Priority', task.priority),
            _row('Due', task.dueDate),
            _row('AI risk', '${(task.aiRiskScore * 100).round()}%'),
            if (task.riskReason != null) ...[
              const SizedBox(height: 8),
              Text(task.riskReason!, style: const TextStyle(color: Colors.orangeAccent, fontSize: 12)),
            ],
            const SizedBox(height: 24),
            const Text('Status', style: TextStyle(color: Colors.white54, fontSize: 12)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _statuses.map((s) {
                final selected = task.status == s;
                return ChoiceChip(
                  label: Text(s),
                  selected: selected,
                  onSelected: (_) => context.read<AppState>().updateTaskStatus(task.id, s),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _row(String label, String value) => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Row(
          children: [
            SizedBox(width: 80, child: Text(label, style: const TextStyle(color: Colors.white38, fontSize: 12))),
            Expanded(child: Text(value, style: const TextStyle(color: Colors.white70, fontSize: 13))),
          ],
        ),
      );
}
