import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';
import '../../../domain/entities/models.dart';

class InteractiveGraphScreen extends ConsumerStatefulWidget {
  const InteractiveGraphScreen({super.key});

  @override
  ConsumerState<InteractiveGraphScreen> createState() => _InteractiveGraphScreenState();
}

class _InteractiveGraphScreenState extends ConsumerState<InteractiveGraphScreen> {
  TaskModel? _selectedTask;

  @override
  Widget build(BuildContext context) {
    final workspace = ref.watch(workspaceProvider);
    final tasks = workspace.tasks;

    return Stack(
      children: [
        // Interactive Graph Canvas
        InteractiveViewer(
          boundaryMargin: const EdgeInsets.all(500),
          minScale: 0.3,
          maxScale: 2.5,
          child: SizedBox(
            width: 1600,
            height: 1200,
            child: CustomPaint(
              painter: GraphVectorPainter(tasks: tasks, selectedTaskId: _selectedTask?.id),
              child: Stack(
                children: tasks.map((task) {
                  final isSelected = _selectedTask?.id == task.id;
                  final isCritical = task.aiRiskScore >= 0.7 || task.status == 'blocked';

                  Color borderColor = AppColors.border;
                  if (task.status == 'done') borderColor = AppColors.success;
                  if (task.status == 'in_progress') borderColor = AppColors.primary;
                  if (isCritical) borderColor = AppColors.danger;

                  return Positioned(
                    left: task.x,
                    top: task.y,
                    child: GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedTask = task;
                        });
                      },
                      child: Container(
                        width: 180,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.surfaceElevated,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: isSelected ? AppColors.secondary : borderColor,
                            width: isSelected ? 2.5 : 1.5,
                          ),
                          boxShadow: [
                            if (isCritical)
                              BoxShadow(
                                color: AppColors.danger.withOpacity(0.3),
                                blurRadius: 16,
                                spreadRadius: 2,
                              ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  task.id,
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.primary,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: (task.aiRiskScore >= 0.7 ? AppColors.danger : AppColors.success).withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    '${(task.aiRiskScore * 100).toInt()}% Risk',
                                    style: TextStyle(
                                      fontSize: 9,
                                      fontWeight: FontWeight.bold,
                                      color: task.aiRiskScore >= 0.7 ? AppColors.danger : AppColors.success,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              task.title,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  task.assignee ?? 'Unassigned',
                                  style: const TextStyle(fontSize: 10, color: AppColors.textSecondary),
                                ),
                                Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: borderColor,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ),

        // Node Inspector Overlay Drawer
        if (_selectedTask != null)
          Positioned(
            right: 16,
            top: 16,
            bottom: 16,
            width: 340,
            child: Card(
              color: AppColors.surface,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(_selectedTask!.id, style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 16)),
                        IconButton(
                          icon: const Icon(Icons.close, size: 18),
                          onPressed: () => setState(() => _selectedTask = null),
                        ),
                      ],
                    ),
                    const Divider(color: AppColors.border),
                    Text(_selectedTask!.title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Text(_selectedTask!.description, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        const Text('Status: ', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text(_selectedTask!.status.toUpperCase(), style: const TextStyle(color: AppColors.secondary)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Text('Assignee: ', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text(_selectedTask!.assignee ?? 'None'),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Text('AI Predictive Risk: ', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text('${(_selectedTask!.aiRiskScore * 100).toInt()}%', style: TextStyle(color: _selectedTask!.aiRiskScore >= 0.7 ? AppColors.danger : AppColors.success, fontWeight: FontWeight.bold)),
                      ],
                    ),
                    if (_selectedTask!.riskReason != null) ...[
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(color: AppColors.danger.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
                        child: Text('⚠️ ${_selectedTask!.riskReason}', style: const TextStyle(fontSize: 11, color: AppColors.danger)),
                      ),
                    ],
                    const Spacer(),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                        icon: const Icon(Icons.check, size: 16),
                        label: const Text('Mark Complete'),
                        onPressed: () {
                          ref.read(workspaceProvider.notifier).updateTaskStatus(_selectedTask!.id, 'done');
                          setState(() => _selectedTask = null);
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class GraphVectorPainter extends CustomPainter {
  final List<TaskModel> tasks;
  final String? selectedTaskId;

  GraphVectorPainter({required this.tasks, this.selectedTaskId});

  @override
  void paint(Canvas canvas, Size size) {
    final taskMap = {for (var t in tasks) t.id: t};

    for (final task in tasks) {
      for (final depId in task.dependsOn) {
        final parent = taskMap[depId];
        if (parent != null) {
          final isHighlighted = selectedTaskId == task.id || selectedTaskId == parent.id;
          final paint = Paint()
            ..color = isHighlighted ? AppColors.secondary : AppColors.border
            ..strokeWidth = isHighlighted ? 2.5 : 1.5
            ..style = PaintingStyle.stroke;

          final start = Offset(parent.x + 180, parent.y + 45);
          final end = Offset(task.x, task.y + 45);

          final path = Path()
            ..moveTo(start.dx, start.dy)
            ..cubicTo(
              start.dx + 50,
              start.dy,
              end.dx - 50,
              end.dy,
              end.dx,
              end.dy,
            );

          canvas.drawPath(path, paint);
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
