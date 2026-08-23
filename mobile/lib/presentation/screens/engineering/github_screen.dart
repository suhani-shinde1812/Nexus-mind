import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';

class GitHubScreen extends ConsumerWidget {
  const GitHubScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workspace = ref.watch(workspaceProvider);
    final eng = workspace.engineeringMetrics;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Metrics Matrix
          Row(
            children: [
              Expanded(
                child: _metricBox(
                  title: 'Avg PR Cycle Time',
                  value: '${eng?.avgPrCycleTimeHours ?? 5.35}h',
                  subtitle: 'Target < 8h SLA',
                  color: AppColors.primary,
                  icon: Icons.timer_outlined,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _metricBox(
                  title: 'CI/CD Pass Rate',
                  value: '${(eng?.ciSuccessRate ?? 100).toInt()}%',
                  subtitle: 'Continuous Pipeline',
                  color: AppColors.success,
                  icon: Icons.check_circle_outline,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _metricBox(
                  title: 'Commits (7 Days)',
                  value: '${eng?.commitsLast7d ?? 14}',
                  subtitle: 'Velocity on target',
                  color: AppColors.secondary,
                  icon: Icons.commit,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _metricBox(
                  title: 'Deploy Frequency',
                  value: eng?.deploymentFrequency ?? '4.2 / day',
                  subtitle: 'Automated CD triggers',
                  color: AppColors.purple,
                  icon: Icons.rocket_launch_outlined,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Integrated Repositories
          const Text('Connected Repositories & CI/CD Telemetry', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border),
            ),
            child: Row(
              children: [
                const Icon(Icons.folder_special, color: AppColors.secondary, size: 28),
                const SizedBox(width: 14),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('nexusmind-platform/core', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                      SizedBox(height: 4),
                      Text('Branch: main • Linked to 8 Task Graph nodes', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: AppColors.success.withOpacity(0.2), borderRadius: BorderRadius.circular(6)),
                  child: const Text('SYNCED', style: TextStyle(color: AppColors.success, fontSize: 10, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Recent Engineering Events Feed
          const Text('Recent Pull Requests & CI Pipeline Events', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          _feedItem('PR-418: feat(auth) Add RFC 6238 TOTP Multi-Factor Authentication', 'Alex Vance', 'Merged • 4.2h cycle', AppColors.purple),
          _feedItem('PR-422: feat(graph) SVG Force-directed live dependency vectors', 'Devon Reed', 'Merged • 6.5h cycle', AppColors.primary),
          _feedItem('BUILD-1092: Linux & Docker Container Test Pipeline', 'GitHub Actions', 'Passed • 78s duration', AppColors.success),
        ],
      ),
    );
  }

  Widget _metricBox({
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
              Text(title, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
              Icon(icon, color: color, size: 16),
            ],
          ),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(subtitle, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
        ],
      ),
    );
  }

  Widget _feedItem(String title, String author, String meta, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                Text('Author: $author • $meta', style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
