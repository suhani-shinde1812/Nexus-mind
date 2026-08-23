import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';
import '../../../domain/entities/models.dart';

class KanbanScreen extends ConsumerWidget {
  const KanbanScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workspace = ref.watch(workspaceProvider);
    final tasks = workspace.tasks;

    final columns = [
      {'status': 'backlog', 'label': 'Backlog', 'color': AppColors.textMuted},
      {'status': 'ready', 'label': 'Ready', 'color': AppColors.secondary},
      {'status': 'in_progress', 'label': 'In Progress', 'color': AppColors.primary},
      {'status': 'blocked', 'label': 'Blocked', 'color': AppColors.danger},
      {'status': 'done', 'label': 'Done', 'color': AppColors.success},
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.all(16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: columns.map((col) {
          final status = col['status'] as String;
          final label = col['label'] as String;
          final color = col['color'] as Color;
          final colTasks = tasks.where((t) => t.status == status).toList();

          return Container(
            width: 280,
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
                        const SizedBox(width: 8),
                        Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(color: AppColors.surfaceElevated, borderRadius: BorderRadius.circular(10)),
                      child: Text('${colTasks.length}', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
                const Divider(color: AppColors.border, height: 20),
                if (colTasks.isEmpty)
                  Container(
                    height: 100,
                    alignment: Alignment.center,
                    child: Text('No tasks in $label', style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                  )
                else
                  ...colTasks.map((task) => _buildKanbanCard(context, ref, task)),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildKanbanCard(BuildContext context, WidgetRef ref, TaskModel task) {
    final isCritical = task.aiRiskScore >= 0.7;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surfaceElevated,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isCritical ? AppColors.danger.withOpacity(0.6) : AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(task.id, style: const TextStyle(color: AppColors.primary, fontSize: 11, fontWeight: FontWeight.bold)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                decoration: BoxDecoration(
                  color: (isCritical ? AppColors.danger : AppColors.success).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text('${(task.aiRiskScore * 100).toInt()}% Risk', style: TextStyle(fontSize: 9, color: isCritical ? AppColors.danger : AppColors.success, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(task.title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(task.assignee ?? 'Unassigned', style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
              PopupMenuButton<String>(
                icon: const Icon(Icons.more_horiz, size: 14),
                onSelected: (newStatus) {
                  ref.read(workspaceProvider.notifier).updateTaskStatus(task.id, newStatus);
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 'in_progress', child: Text('Move to In Progress')),
                  const PopupMenuItem(value: 'blocked', child: Text('Move to Blocked')),
                  const PopupMenuItem(value: 'done', child: Text('Move to Done')),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}
