import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../application/providers.dart';
import '../../core/theme/app_theme.dart';

class ResponsiveScaffold extends ConsumerStatefulWidget {
  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;
  final Widget body;
  final String title;

  const ResponsiveScaffold({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
    required this.body,
    required this.title,
  });

  @override
  ConsumerState<ResponsiveScaffold> createState() => _ResponsiveScaffoldState();
}

class _ResponsiveScaffoldState extends ConsumerState<ResponsiveScaffold> {
  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width >= 900;
    final authState = ref.watch(authProvider);
    final user = authState.user;

    final destinations = [
      const NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Dashboard'),
      const NavigationDestination(icon: Icon(Icons.hub_outlined), selectedIcon: Icon(Icons.hub), label: 'Graph'),
      const NavigationDestination(icon: Icon(Icons.view_kanban_outlined), selectedIcon: Icon(Icons.view_kanban), label: 'Kanban'),
      const NavigationDestination(icon: Icon(Icons.psychology_outlined), selectedIcon: Icon(Icons.psychology), label: 'AI Copilot'),
      const NavigationDestination(icon: Icon(Icons.security_outlined), selectedIcon: Icon(Icons.security), label: 'Security'),
      const NavigationDestination(icon: Icon(Icons.menu_book_outlined), selectedIcon: Icon(Icons.menu_book), label: 'Knowledge'),
      const NavigationDestination(icon: Icon(Icons.code_outlined), selectedIcon: Icon(Icons.code), label: 'Engineering'),
      const NavigationDestination(icon: Icon(Icons.videocam_outlined), selectedIcon: Icon(Icons.videocam), label: 'Meetings'),
      const NavigationDestination(icon: Icon(Icons.account_tree_outlined), selectedIcon: Icon(Icons.account_tree), label: 'Architecture'),
    ];

    final railDestinations = [
      const NavigationRailDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: Text('Dashboard')),
      const NavigationRailDestination(icon: Icon(Icons.hub_outlined), selectedIcon: Icon(Icons.hub), label: Text('Graph')),
      const NavigationRailDestination(icon: Icon(Icons.view_kanban_outlined), selectedIcon: Icon(Icons.view_kanban), label: Text('Kanban')),
      const NavigationRailDestination(icon: Icon(Icons.psychology_outlined), selectedIcon: Icon(Icons.psychology), label: Text('AI Copilot')),
      const NavigationRailDestination(icon: Icon(Icons.security_outlined), selectedIcon: Icon(Icons.security), label: Text('Security')),
      const NavigationRailDestination(icon: Icon(Icons.menu_book_outlined), selectedIcon: Icon(Icons.menu_book), label: Text('Knowledge')),
      const NavigationRailDestination(icon: Icon(Icons.code_outlined), selectedIcon: Icon(Icons.code), label: Text('Engineering')),
      const NavigationRailDestination(icon: Icon(Icons.videocam_outlined), selectedIcon: Icon(Icons.videocam), label: Text('Meetings')),
      const NavigationRailDestination(icon: Icon(Icons.account_tree_outlined), selectedIcon: Icon(Icons.account_tree), label: Text('Architecture')),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.2),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: AppColors.primary),
              ),
              child: const Text('NEXUS MIND', style: TextStyle(color: AppColors.primary, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            ),
            const SizedBox(width: 12),
            Text(widget.title, style: const TextStyle(fontSize: 16)),
          ],
        ),
        actions: [
          if (user != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Chip(
                avatar: CircleAvatar(
                  backgroundColor: AppColors.primary,
                  child: Text(user.avatar, style: const TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.bold)),
                ),
                label: Text('${user.name} (${user.role})', style: const TextStyle(fontSize: 12)),
                backgroundColor: AppColors.surfaceElevated,
                side: const BorderSide(color: AppColors.border),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            tooltip: 'Sync Workspace',
            onPressed: () => ref.read(workspaceProvider.notifier).loadWorkspace(),
          ),
          IconButton(
            icon: const Icon(Icons.logout, size: 20, color: AppColors.danger),
            tooltip: 'Sign Out',
            onPressed: () => ref.read(authProvider.notifier).logout(),
          ),
        ],
      ),
      body: Row(
        children: [
          if (isDesktop)
            NavigationRail(
              selectedIndex: widget.selectedIndex,
              onDestinationSelected: widget.onDestinationSelected,
              labelType: NavigationRailLabelType.all,
              destinations: railDestinations,
            ),
          Expanded(child: widget.body),
        ],
      ),
      bottomNavigationBar: isDesktop
          ? null
          : BottomNavigationBar(
              currentIndex: widget.selectedIndex > 3 ? 0 : widget.selectedIndex,
              onTap: widget.onDestinationSelected,
              items: const [
                BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: 'Dashboard'),
                BottomNavigationBarItem(icon: Icon(Icons.hub), label: 'Graph'),
                BottomNavigationBarItem(icon: Icon(Icons.view_kanban), label: 'Kanban'),
                BottomNavigationBarItem(icon: Icon(Icons.psychology), label: 'Copilot'),
              ],
            ),
    );
  }
}
