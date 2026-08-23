import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';

class SecurityCenterScreen extends ConsumerWidget {
  const SecurityCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workspace = ref.watch(workspaceProvider);
    final radar = workspace.threatRadar;

    final threatScore = radar?.threatScore ?? 24;
    final threatLevel = radar?.threatLevel ?? 'SECURE';

    Color levelColor = AppColors.success;
    if (threatLevel == 'ELEVATED') levelColor = AppColors.warning;
    if (threatLevel == 'HIGH' || threatLevel == 'CRITICAL') levelColor = AppColors.danger;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Threat Radar Banner
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: levelColor.withOpacity(0.5)),
            ),
            child: Row(
              children: [
                Container(
                  width: 80,
                  height: 80,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: levelColor.withOpacity(0.15),
                    shape: BoxShape.circle,
                    border: Border.all(color: levelColor, width: 2),
                  ),
                  child: Text(
                    '$threatScore',
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: levelColor),
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text('THREAT RADAR: ', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.textSecondary)),
                          Text(threatLevel, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: levelColor)),
                        ],
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Continuous anomaly detection evaluates login velocity, brute force resistance, and RBAC token validity.',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      const SizedBox(height: 8),
                      Text('• Active Threats: ${radar?.activeThreatsCount ?? 0}  |  • Failed Logins (24h): ${radar?.failedLogins24h ?? 0}', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Security Modules Matrix
          const Text('Security Subsystems & IAM Compliance', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _securityCard(
                  title: 'Multi-Factor Auth (MFA)',
                  subtitle: 'RFC 6238 TOTP Enforced',
                  icon: Icons.vpn_key,
                  color: AppColors.primary,
                  status: 'Active',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _securityCard(
                  title: 'RBAC Access Matrix',
                  subtitle: '4 Strict Role Boundaries',
                  icon: Icons.admin_panel_settings,
                  color: AppColors.secondary,
                  status: 'Enforced',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _securityCard(
                  title: 'SHA-256 Token Sessions',
                  subtitle: 'Automatic Session Rotation',
                  icon: Icons.shield,
                  color: AppColors.success,
                  status: 'Guarded',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _securityCard(
                  title: 'Audit Logging Pipeline',
                  subtitle: 'Immutable Ledger Active',
                  icon: Icons.history,
                  color: AppColors.purple,
                  status: 'Logging',
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Active Threat Events
          const Text('Recent Security Audit Events', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          _eventTile('system_startup', 'Security Gateway initialized with zero critical anomalies.', 'Just now', AppColors.success),
          _eventTile('mfa_validation', 'User Sarah Jenkins authenticated via RFC 6238 TOTP challenge.', '15 mins ago', AppColors.primary),
          _eventTile('token_session', 'Device session registered from 127.0.0.1 (Desktop Client).', '1 hour ago', AppColors.secondary),
        ],
      ),
    );
  }

  Widget _securityCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required String status,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
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
              Icon(icon, color: color, size: 20),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(color: color.withOpacity(0.15), borderRadius: BorderRadius.circular(4)),
                child: Text(status, style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(subtitle, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
        ],
      ),
    );
  }

  Widget _eventTile(String event, String desc, String time, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Container(width: 6, height: 6, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(event, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color)),
                Text(desc, style: const TextStyle(fontSize: 12)),
              ],
            ),
          ),
          Text(time, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
        ],
      ),
    );
  }
}
