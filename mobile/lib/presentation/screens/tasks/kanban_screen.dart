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
      {'status': 'in_progress', 'label': 'In Progress', 'color': AppColors.primary},
      {'status': 'blocked', 'label': 'Blocked', 'color': AppColors.danger},
      {'status': 'done', 'label': 'Done', 'color': AppColors.success},
    ];

    return Scaffold(
      backgroundColor: Colors.transparent,
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('New Task', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: () => _showCreateTaskSheet(context, ref, workspace),
      ),
      body: SingleChildScrollView(
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
              width: 290,
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
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
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
        borderRadius: BorderRadius.circular(10),
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
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: (isCritical ? AppColors.danger : AppColors.success).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text('${(task.aiRiskScore * 100).toInt()}% Risk', style: TextStyle(fontSize: 9, color: isCritical ? AppColors.danger : AppColors.success, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(task.title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
          if (task.description.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(task.description, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary), maxLines: 2, overflow: TextOverflow.ellipsis),
          ],
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.person_outline, size: 12, color: AppColors.textMuted),
                  const SizedBox(width: 4),
                  Text(task.assignee ?? 'Unassigned', style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                ],
              ),
              PopupMenuButton<String>(
                icon: const Icon(Icons.more_horiz, size: 16),
                onSelected: (newStatus) {
                  ref.read(workspaceProvider.notifier).updateTaskStatus(task.id, newStatus);
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 'backlog', child: Text('Move to Backlog')),
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

  void _showCreateTaskSheet(BuildContext context, WidgetRef ref, WorkspaceState workspace) {
    final titleCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    final currentUser = ref.read(authProvider).user;
    final availableUsers = [
      if (currentUser != null) currentUser,
      ...workspace.users.where((u) => u.email != currentUser?.email),
    ];
    String priority = 'Medium';
    String status = 'in_progress';
    String? assignee = availableUsers.isNotEmpty ? availableUsers.first.name : 'Unassigned';
    String project = workspace.projects.isNotEmpty ? workspace.projects.first.name : 'Sprint Alpha - Cloud Migration';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return Padding(
              padding: EdgeInsets.only(
                left: 20, right: 20, top: 20,
                bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('⚡ Create New Task', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: titleCtrl,
                      decoration: const InputDecoration(labelText: 'Task Title', hintText: 'e.g. Build GraphQL Gateway', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: descCtrl,
                      maxLines: 2,
                      decoration: const InputDecoration(labelText: 'Description', hintText: 'Acceptance criteria and scope...', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            value: priority,
                            decoration: const InputDecoration(labelText: 'Priority', border: OutlineInputBorder()),
                            items: const [
                              DropdownMenuItem(value: 'Low', child: Text('Low')),
                              DropdownMenuItem(value: 'Medium', child: Text('Medium')),
                              DropdownMenuItem(value: 'High', child: Text('High')),
                              DropdownMenuItem(value: 'Critical', child: Text('Critical')),
                            ],
                            onChanged: (val) { if (val != null) setSheetState(() => priority = val); },
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            value: status,
                            decoration: const InputDecoration(labelText: 'Status', border: OutlineInputBorder()),
                            items: const [
                              DropdownMenuItem(value: 'backlog', child: Text('Backlog')),
                              DropdownMenuItem(value: 'in_progress', child: Text('In Progress')),
                              DropdownMenuItem(value: 'blocked', child: Text('Blocked')),
                              DropdownMenuItem(value: 'done', child: Text('Done')),
                            ],
                            onChanged: (val) { if (val != null) setSheetState(() => status = val); },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    if (availableUsers.isNotEmpty)
                      DropdownButtonFormField<String>(
                        value: assignee,
                        decoration: const InputDecoration(labelText: 'Assignee', border: OutlineInputBorder()),
                        items: availableUsers.map((u) => DropdownMenuItem(value: u.name, child: Text('${u.name} (${u.role})'))).toList(),
                        onChanged: (val) { if (val != null) setSheetState(() => assignee = val); },
                      ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, padding: const EdgeInsets.symmetric(vertical: 14)),
                      onPressed: () {
                        final title = titleCtrl.text.trim();
                        if (title.isEmpty) {
                          ScaffoldMessenger.of(ctx).showSnackBar(const SnackBar(content: Text('Please enter a task title')));
                          return;
                        }
                        ref.read(workspaceProvider.notifier).createTask({
                          'title': title,
                          'description': descCtrl.text.trim(),
                          'priority': priority,
                          'status': status,
                          'assignee': assignee ?? 'Unassigned',
                          'project': project,
                          'due_date': '2026-08-30',
                        });
                        Navigator.pop(ctx);
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Task "$title" created & published!')));
                      },
                      child: const Text('Save & Publish to Workspace', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}
