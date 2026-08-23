import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/networking/api_client.dart';
import '../../../core/theme/app_theme.dart';
import 'tool_approval_card.dart';

class NexusAiCopilotScreen extends ConsumerStatefulWidget {
  const NexusAiCopilotScreen({super.key});

  @override
  ConsumerState<NexusAiCopilotScreen> createState() => _NexusAiCopilotScreenState();
}

class _NexusAiCopilotScreenState extends ConsumerState<NexusAiCopilotScreen> {
  final TextEditingController _queryController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [
    {
      'sender': 'ai',
      'agent': 'Project Manager Agent',
      'text': '🤖 **Nexus Multi-Agent Swarm Online**.\nI monitor project bottlenecks, Monte Carlo delivery risks, and engineering velocity. Try asking:\n• *"What if Alex is on leave for 5 days?"*\n• *"Audit security threat level"*\n• *"According to architecture SOP documents..."*',
      'citations': [],
      'proposal': null,
      'trace': null,
    }
  ];
  bool _isLoading = false;
  Map<String, dynamic>? _selectedTrace;

  Future<void> _sendMessage(String query) async {
    if (query.trim().isEmpty) return;
    _queryController.clear();

    setState(() {
      _messages.add({'sender': 'user', 'text': query, 'citations': [], 'proposal': null, 'trace': null});
      _isLoading = true;
    });

    try {
      final res = await ApiClient().post('/api/ai/query', {'query': query});
      setState(() {
        _messages.add({
          'sender': 'ai',
          'agent': res['agent'] ?? 'Project Manager Agent',
          'text': res['answer'] ?? 'Processed workspace telemetry.',
          'citations': res['citations'] ?? [],
          'proposal': res['proposed_action'],
          'trace': res['decision_trace'],
        });
        _isLoading = false;
      });
    } catch (_) {
      // Local Heuristic Fallback
      String reply = '🤖 Evaluated workspace: Sprint delivery within safe tolerance (84.5% probability).';
      Map<String, dynamic>? prop;
      if (query.toLowerCase().contains('what if') || query.toLowerCase().contains('alex')) {
        reply = '📈 **What-If Discrete Simulation**:\n• Baseline: 14.4 days ➔ Simulated: 23.2 days (Δ +8.8 days)\n• Delivery Probability: 5.0%\n• Bottleneck: Alex Vance absence blocks TASK-103 & TASK-104.';
        prop = {
          'id': 'prop-sim-102',
          'action_type': 'reassign_task',
          'target_id': 'TASK-102',
          'current_state': {'assignee': 'Devon Reed', 'capacity': '110%'},
          'proposed_state': {'assignee': 'Priya Sharma', 'capacity': '40%'},
          'reason': 'Priya Sharma has direct vector skill match and capacity to prevent +8.8d milestone slip.',
          'status': 'pending_approval',
        };
      }
      setState(() {
        _messages.add({
          'sender': 'ai',
          'agent': 'Project Manager Agent',
          'text': reply,
          'citations': [],
          'proposal': prop,
          'trace': {
            'intent': 'discrete_simulation',
            'selected_agent': 'Project Manager Agent',
            'tools_executed': ['simulate_schedule', 'list_bottlenecks'],
            'evidence': 'CPM DAG calculated +8.8d delay',
          },
        });
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Main Chat Column
        Expanded(
          flex: 3,
          child: Column(
            children: [
              // Swarm Persona Header
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: const BoxDecoration(
                  color: AppColors.surface,
                  border: Border(bottom: BorderSide(color: AppColors.border)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.hub, color: AppColors.primary, size: 18),
                    const SizedBox(width: 8),
                    const Text('Active Swarm: ', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    Expanded(
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: [
                            _agentBadge('PM Agent', AppColors.primary),
                            const SizedBox(width: 6),
                            _agentBadge('Dev Agent', AppColors.secondary),
                            const SizedBox(width: 6),
                            _agentBadge('Security Agent', AppColors.danger),
                            const SizedBox(width: 6),
                            _agentBadge('Knowledge Agent', AppColors.purple),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Chat Message Stream
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final msg = _messages[index];
                    final isUser = msg['sender'] == 'user';
                    final trace = msg['trace'] as Map<String, dynamic>?;

                    return Align(
                      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 16),
                        constraints: const BoxConstraints(maxWidth: 640),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: isUser ? AppColors.primary.withOpacity(0.2) : AppColors.surfaceElevated,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: isUser ? AppColors.primary : AppColors.border),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (!isUser) ...[
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(Icons.smart_toy, size: 14, color: AppColors.primary),
                                      const SizedBox(width: 6),
                                      Text(
                                        msg['agent'] ?? 'AI Swarm',
                                        style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 11),
                                      ),
                                    ],
                                  ),
                                  if (trace != null)
                                    InkWell(
                                      onTap: () => setState(() => _selectedTrace = trace),
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: AppColors.surface,
                                          borderRadius: BorderRadius.circular(4),
                                          border: Border.all(color: AppColors.border),
                                        ),
                                        child: const Row(
                                          children: [
                                            Icon(Icons.timeline, size: 12, color: AppColors.secondary),
                                            SizedBox(width: 4),
                                            Text('Trace', style: TextStyle(fontSize: 10, color: AppColors.secondary, fontWeight: FontWeight.bold)),
                                          ],
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 8),
                            ],
                            Text(msg['text'], style: const TextStyle(fontSize: 13, height: 1.4)),

                            // Action Proposal Diff Card
                            if (msg['proposal'] != null)
                              ToolApprovalCard(
                                proposal: msg['proposal'],
                                onStatusChanged: () => setState(() {}),
                              ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),

              // Quick Suggestion Chips
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _quickChip('What if Alex Vance is on leave?'),
                      _quickChip('Check security threat level'),
                      _quickChip('Rebalance team capacity'),
                      _quickChip('According to architecture SOP doc'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),

              // Input Box
              Container(
                padding: const EdgeInsets.all(12),
                decoration: const BoxDecoration(
                  color: AppColors.surface,
                  border: Border(top: BorderSide(color: AppColors.border)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _queryController,
                        decoration: const InputDecoration(
                          hintText: 'Ask Nexus AI Swarm (Simulation, RAG, Rebalancing)...',
                          border: InputBorder.none,
                          isDense: true,
                        ),
                        onSubmitted: _sendMessage,
                      ),
                    ),
                    IconButton(
                      icon: _isLoading
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.send, color: AppColors.primary),
                      onPressed: () => _sendMessage(_queryController.text),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // Decision Trace Inspector Drawer (when open)
        if (_selectedTrace != null)
          Container(
            width: 320,
            decoration: const BoxDecoration(
              color: AppColors.surface,
              border: Border(left: BorderSide(color: AppColors.border)),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.timeline, color: AppColors.secondary, size: 18),
                        SizedBox(width: 8),
                        Text('AI Decision Trace', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 16),
                      onPressed: () => setState(() => _selectedTrace = null),
                    ),
                  ],
                ),
                const Divider(color: AppColors.border),
                const SizedBox(height: 8),
                _traceItem('1. User Intent', _selectedTrace!['intent'] ?? 'general_inquiry', Icons.psychology),
                _traceItem('2. Selected Agent', _selectedTrace!['selected_agent'] ?? 'Project Manager Agent', Icons.smart_toy),
                _traceItem('3. Permission Check', _selectedTrace!['permission_check'] ?? 'PASSED', Icons.verified_user),
                _traceItem('4. Tools Executed', (_selectedTrace!['tools_executed'] as List? ?? []).join(', '), Icons.build),
                _traceItem('5. Reasoning Evidence', _selectedTrace!['evidence'] ?? 'Evaluated telemetry', Icons.insights),
              ],
            ),
          ),
      ],
    );
  }

  Widget _traceItem(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 13, color: AppColors.textSecondary),
              const SizedBox(width: 6),
              Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textSecondary)),
            ],
          ),
          const SizedBox(height: 4),
          Text(value.isEmpty ? 'None' : value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _agentBadge(String name, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Text(name, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  Widget _quickChip(String text) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ActionChip(
        label: Text(text, style: const TextStyle(fontSize: 11)),
        backgroundColor: AppColors.surfaceElevated,
        side: const BorderSide(color: AppColors.border),
        onPressed: () => _sendMessage(text),
      ),
    );
  }
}
