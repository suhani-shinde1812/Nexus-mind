import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';

class MeetingsScreen extends ConsumerWidget {
  const MeetingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workspace = ref.watch(workspaceProvider);
    final meetings = workspace.meetings;

    return Scaffold(
      backgroundColor: Colors.transparent,
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.secondary,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('Schedule Meeting', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: () => _showScheduleMeetingSheet(context, ref, workspace),
      ),
      body: meetings.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.videocam_outlined, size: 48, color: AppColors.textMuted),
                  const SizedBox(height: 12),
                  const Text('No meetings scheduled yet', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  const Text('Tap "+ Schedule Meeting" to create a standup room.', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 80),
              itemCount: meetings.length,
              itemBuilder: (context, index) {
                final m = meetings[index];
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
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
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.15), borderRadius: BorderRadius.circular(6)),
                            child: Text(m.project, style: const TextStyle(color: AppColors.primary, fontSize: 11, fontWeight: FontWeight.bold)),
                          ),
                          Row(
                            children: [
                              const Icon(Icons.access_time, size: 14, color: AppColors.textSecondary),
                              const SizedBox(width: 4),
                              Text('${m.date} at ${m.time} (${m.duration}m)', style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(m.title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                      if (m.agenda.isNotEmpty) ...[
                        const SizedBox(height: 6),
                        Text(m.agenda, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                      ],
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Organizer: ${m.organizer}', style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(backgroundColor: AppColors.secondary, padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8)),
                            icon: const Icon(Icons.videocam, size: 16),
                            label: const Text('Join Room', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Connected to Jitsi Room: ${m.link}')));
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }

  void _showScheduleMeetingSheet(BuildContext context, WidgetRef ref, WorkspaceState workspace) {
    final titleCtrl = TextEditingController();
    final agendaCtrl = TextEditingController();
    String project = workspace.projects.isNotEmpty ? workspace.projects.first.name : 'Sprint Alpha - Cloud Migration';
    String duration = '30';
    DateTime selectedDate = DateTime.now().add(const Duration(days: 1));
    TimeOfDay selectedTime = const TimeOfDay(hour: 10, minute: 0);

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
                        const Text('📅 Schedule Team Meeting', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: titleCtrl,
                      decoration: const InputDecoration(labelText: 'Meeting Title', hintText: 'e.g. Blocker Review & Standup', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 10),
                    if (workspace.projects.isNotEmpty)
                      DropdownButtonFormField<String>(
                        value: project,
                        decoration: const InputDecoration(labelText: 'Project', border: OutlineInputBorder()),
                        items: workspace.projects.map((p) => DropdownMenuItem(value: p.name, child: Text(p.name))).toList(),
                        onChanged: (val) { if (val != null) setSheetState(() => project = val); },
                      ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            icon: const Icon(Icons.calendar_today, size: 16),
                            label: Text('${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}', style: const TextStyle(fontSize: 12)),
                            onPressed: () async {
                              final picked = await showDatePicker(context: ctx, initialDate: selectedDate, firstDate: DateTime.now(), lastDate: DateTime(2028));
                              if (picked != null) setSheetState(() => selectedDate = picked);
                            },
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            icon: const Icon(Icons.access_time, size: 16),
                            label: Text(selectedTime.format(ctx), style: const TextStyle(fontSize: 12)),
                            onPressed: () async {
                              final picked = await showTimePicker(context: ctx, initialTime: selectedTime);
                              if (picked != null) setSheetState(() => selectedTime = picked);
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      value: duration,
                      decoration: const InputDecoration(labelText: 'Duration', border: OutlineInputBorder()),
                      items: const [
                        DropdownMenuItem(value: '15', child: Text('15 minutes')),
                        DropdownMenuItem(value: '30', child: Text('30 minutes')),
                        DropdownMenuItem(value: '45', child: Text('45 minutes')),
                        DropdownMenuItem(value: '60', child: Text('60 minutes')),
                      ],
                      onChanged: (val) { if (val != null) setSheetState(() => duration = val); },
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: agendaCtrl,
                      maxLines: 2,
                      decoration: const InputDecoration(labelText: 'Agenda / Goals', hintText: 'What will this meeting cover?', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: AppColors.secondary, padding: const EdgeInsets.symmetric(vertical: 14)),
                      onPressed: () {
                        final title = titleCtrl.text.trim();
                        if (title.isEmpty) {
                          ScaffoldMessenger.of(ctx).showSnackBar(const SnackBar(content: Text('Please enter a meeting title')));
                          return;
                        }
                        final dateStr = '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}';
                        final timeStr = '${selectedTime.hour.toString().padLeft(2, '0')}:${selectedTime.minute.toString().padLeft(2, '0')}';

                        ref.read(workspaceProvider.notifier).createMeeting({
                          'title': title,
                          'project': project,
                          'date': dateStr,
                          'time': timeStr,
                          'duration': duration,
                          'agenda': agendaCtrl.text.trim(),
                          'attendees': ['Team Lead', 'Engineering Team'],
                        });
                        Navigator.pop(ctx);
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Meeting "$title" scheduled!')));
                      },
                      child: const Text('Schedule Meeting & Generate Jitsi Room', style: TextStyle(fontWeight: FontWeight.bold)),
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
