import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../app_state.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  Color _severityColor(String severity) {
    switch (severity) {
      case 'critical':
        return Colors.redAccent;
      case 'warning':
        return Colors.orangeAccent;
      default:
        return Colors.blueAccent;
    }
  }

  @override
  Widget build(BuildContext context) {
    final alerts = context.watch<AppState>().alerts;
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1F),
      appBar: AppBar(backgroundColor: const Color(0xFF11162B), title: const Text('Alerts')),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: alerts.length,
        itemBuilder: (context, i) {
          final a = alerts[i];
          return Card(
            color: const Color(0xFF151B33),
            margin: const EdgeInsets.only(bottom: 10),
            child: ListTile(
              leading: CircleAvatar(radius: 6, backgroundColor: _severityColor(a.severity)),
              title: Text(a.title, style: const TextStyle(color: Colors.white, fontSize: 14)),
              subtitle: Text(a.message, style: const TextStyle(color: Colors.white54, fontSize: 12)),
            ),
          );
        },
      ),
    );
  }
}
