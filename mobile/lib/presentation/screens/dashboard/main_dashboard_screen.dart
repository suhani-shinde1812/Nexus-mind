import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';

class MainDashboardScreen extends ConsumerWidget {
  final ValueChanged<int> onNavigate;

  const MainDashboardScreen({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final workspace = ref.watch(workspaceProvider);
    final user = authState.user;
    final tasks = workspace.tasks;
    final projects = workspace.projects;

    final completedTasks = tasks.where((t) => t.status == 'done').length;
    final highRiskTasks = tasks.where((t) => t.aiRiskScore >= 0.7).length;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome & Role Switcher
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.primary.withOpacity(0.3), AppColors.surface],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.primary.withOpacity(0.5)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Welcome back, ${user?.name ?? "Engineer"}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text('Role Portal: ${user?.role ?? "Team Member"}', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                      ],
                    ),
                    PopupMenuButton<String>(
                      tooltip: 'Switch Examiner Role',
                      icon: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(6), border: Border.all(color: AppColors.border)),
                        child: const Row(
                          children: [
                            Text('Switch Persona', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                            Icon(Icons.arrow_drop_down, size: 16),
                          ],
                        ),
                      ),
                      onSelected: (role) => ref.read(authProvider.notifier).loginDemo(role),
                      itemBuilder: (context) => [
                        const PopupMenuItem(value: 'employee', child: Text('Alex Vance (Frontend Lead / Employee)')),
                        const PopupMenuItem(value: 'team_lead', child: Text('Sarah Jenkins (Team Lead)')),
                        const PopupMenuItem(value: 'project_manager', child: Text('Marcus Chen (Project Manager)')),
                        const PopupMenuItem(value: 'admin', child: Text('Elena Rostova (Administrator)')),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Primary KPIs Matrix
          Row(
            children: [
              Expanded(
                child: _kpiCard(
                  title: 'Sprint SLA On-Time',
                  value: '84.5%',
                  subtitle: 'Monte Carlo 500 Runs',
                  color: AppColors.success,
                  icon: Icons.speed,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _kpiCard(
                  title: 'Critical Path Hazards',
                  value: '$highRiskTasks Tasks',
                  subtitle: '2 Bottlenecks',
                  color: AppColors.danger,
                  icon: Icons.warning_amber,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _kpiCard(
                  title: 'Tasks Completed',
                  value: '$completedTasks / ${tasks.length}',
                  subtitle: '${((completedTasks / (tasks.isEmpty ? 1 : tasks.length)) * 100).toInt()}% Progress',
                  color: AppColors.secondary,
                  icon: Icons.check_circle_outline,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _kpiCard(
                  title: 'Threat Radar',
                  value: '${workspace.threatRadar?.threatScore ?? 24} / 100',
                  subtitle: workspace.threatRadar?.threatLevel ?? 'SECURE',
                  color: AppColors.purple,
                  icon: Icons.security,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Quick Navigation Hub
          const Text('Operations & Intelligence Matrix', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          GridView.count(
            crossAxisCount: MediaQuery.of(context).size.width > 600 ? 4 : 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              _navTile('Live Task Graph', 'CustomPainter dependency vectors', Icons.hub, AppColors.primary, () => onNavigate(1)),
              _navTile('Kanban Board', '5-column drag-and-drop', Icons.view_kanban, AppColors.secondary, () => onNavigate(2)),
              _navTile('AI Swarm Copilot', 'What-If discrete simulations', Icons.psychology, AppColors.purple, () => onNavigate(3)),
              _navTile('Security Center', 'Audit logs & Threat Radar', Icons.security, AppColors.danger, () => onNavigate(4)),
            ],
          ),
          const SizedBox(height: 24),

          // Active Projects List
          const Text('Active Engineering Milestones', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ...projects.map((p) => Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(p.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        Text('${p.progress}%', style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    LinearProgressIndicator(
                      value: p.progress / 100.0,
                      backgroundColor: AppColors.surfaceElevated,
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Lead: ${p.lead}', style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                        Text('Deadline: ${p.deadline}', style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                      ],
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  Widget _kpiCard({
    required String title,
    required String value,
    required String subtitle,
    required Color color,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
              Icon(icon, color: color, size: 16),
            ],
          ),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(subtitle, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
        ],
      ),
    );
  }

  Widget _navTile(String title, String subtitle, IconData icon, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(icon, color: color, size: 24),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 9, color: AppColors.textSecondary), maxLines: 1, overflow: TextOverflow.ellipsis),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
