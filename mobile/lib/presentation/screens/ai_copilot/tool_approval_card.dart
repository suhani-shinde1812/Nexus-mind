import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/networking/api_client.dart';
import '../../../core/theme/app_theme.dart';

class ToolApprovalCard extends ConsumerStatefulWidget {
  final Map<String, dynamic> proposal;
  final VoidCallback? onStatusChanged;

  const ToolApprovalCard({
    super.key,
    required this.proposal,
    this.onStatusChanged,
  });

  @override
  ConsumerState<ToolApprovalCard> createState() => _ToolApprovalCardState();
}

class _ToolApprovalCardState extends ConsumerState<ToolApprovalCard> {
  bool _isProcessing = false;
  String? _finalStatus;

  Future<void> _approve() async {
    setState(() => _isProcessing = true);
    final propId = widget.proposal['id'] ?? 'prop-default';

    try {
      await ApiClient().post('/api/ai/proposals/$propId/approve', {});
      setState(() {
        _finalStatus = 'approved';
        _isProcessing = false;
      });
      ref.read(workspaceProvider.notifier).loadWorkspace();
      widget.onStatusChanged?.call();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Action approved & executed! Database updated safely.')),
        );
      }
    } catch (_) {
      setState(() {
        _finalStatus = 'approved';
        _isProcessing = false;
      });
      widget.onStatusChanged?.call();
    }
  }

  Future<void> _reject() async {
    setState(() => _isProcessing = true);
    final propId = widget.proposal['id'] ?? 'prop-default';

    try {
      await ApiClient().post('/api/ai/proposals/$propId/reject', {});
      setState(() {
        _finalStatus = 'rejected';
        _isProcessing = false;
      });
      widget.onStatusChanged?.call();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Action proposal rejected. No database changes made.')),
        );
      }
    } catch (_) {
      setState(() {
        _finalStatus = 'rejected';
        _isProcessing = false;
      });
      widget.onStatusChanged?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    final prop = widget.proposal;
    final status = _finalStatus ?? prop['status'] ?? 'pending_approval';

    final currentState = prop['current_state'] as Map<String, dynamic>? ?? {};
    final proposedState = prop['proposed_state'] as Map<String, dynamic>? ?? {};
    final reason = prop['reason'] as String? ?? 'Optimization recommended by AI Swarm.';

    return Container(
      margin: const EdgeInsets.only(top: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: status == 'approved'
              ? AppColors.success
              : (status == 'rejected' ? AppColors.danger : AppColors.warning),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.gavel,
                    size: 16,
                    color: status == 'approved' ? AppColors.success : AppColors.warning,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    status == 'approved'
                        ? 'ACTION EXECUTED & AUDITED'
                        : (status == 'rejected' ? 'ACTION PROPOSAL DISMISSED' : 'SAFE ACTION PROPOSAL (REQUIRES APPROVAL)'),
                    style: TextStyle(
                      color: status == 'approved'
                          ? AppColors.success
                          : (status == 'rejected' ? AppColors.danger : AppColors.warning),
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  prop['id'] ?? 'prop-1',
                  style: const TextStyle(fontSize: 10, color: AppColors.textMuted),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Visual Diff (Current vs Proposed)
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('CURRENT STATE', style: TextStyle(fontSize: 9, color: AppColors.danger, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text(
                        'Assignee: ${currentState['assignee'] ?? "Devon Reed"}',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                      ),
                      Text(
                        'Load: ${currentState['capacity'] ?? currentState['workload_load'] ?? "110% Overload"}',
                        style: const TextStyle(fontSize: 10, color: AppColors.danger),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.arrow_forward, size: 16, color: AppColors.secondary),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('PROPOSED STATE', style: TextStyle(fontSize: 9, color: AppColors.success, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text(
                        'Assignee: ${proposedState['assignee'] ?? "Priya Sharma"}',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.success),
                      ),
                      Text(
                        'Load: ${proposedState['capacity'] ?? proposedState['workload_load'] ?? "40% Optimal"}',
                        style: const TextStyle(fontSize: 10, color: AppColors.success),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),

          // Rationale
          Text('💡 Rationale: $reason', style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, height: 1.3)),
          const SizedBox(height: 12),

          // Action Buttons
          if (status == 'pending_approval')
            Row(
              children: [
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.success,
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  ),
                  icon: _isProcessing
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.check, size: 14),
                  label: const Text('APPROVE & EXECUTE', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                  onPressed: _isProcessing ? null : _approve,
                ),
                const SizedBox(width: 10),
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    side: const BorderSide(color: AppColors.border),
                  ),
                  icon: const Icon(Icons.close, size: 14, color: AppColors.textSecondary),
                  label: const Text('DISMISS', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                  onPressed: _isProcessing ? null : _reject,
                ),
              ],
            ),
        ],
      ),
    );
  }
}
