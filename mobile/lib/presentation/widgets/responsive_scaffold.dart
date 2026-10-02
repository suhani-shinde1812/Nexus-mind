import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../application/providers.dart';
import '../../core/theme/app_theme.dart';
import '../../domain/entities/models.dart';


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
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width >= 900;
    final authState = ref.watch(authProvider);
    final user = authState.user;

    final railDestinations = [
      const NavigationRailDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: Text('Dashboard')),
      const NavigationRailDestination(icon: Icon(Icons.hub_outlined), selectedIcon: Icon(Icons.hub), label: Text('Graph')),
      const NavigationRailDestination(icon: Icon(Icons.view_kanban_outlined), selectedIcon: Icon(Icons.view_kanban), label: Text('Tasks')),
      const NavigationRailDestination(icon: Icon(Icons.psychology_outlined), selectedIcon: Icon(Icons.psychology), label: Text('AI Copilot')),
      const NavigationRailDestination(icon: Icon(Icons.security_outlined), selectedIcon: Icon(Icons.security), label: Text('Security')),
      const NavigationRailDestination(icon: Icon(Icons.menu_book_outlined), selectedIcon: Icon(Icons.menu_book), label: Text('Knowledge')),
      const NavigationRailDestination(icon: Icon(Icons.code_outlined), selectedIcon: Icon(Icons.code), label: Text('Engineering')),
      const NavigationRailDestination(icon: Icon(Icons.videocam_outlined), selectedIcon: Icon(Icons.videocam), label: Text('Meetings')),
      const NavigationRailDestination(icon: Icon(Icons.account_tree_outlined), selectedIcon: Icon(Icons.account_tree), label: Text('Architecture')),
    ];

    return Scaffold(
      key: _scaffoldKey,
      drawer: _buildDrawer(context, user),
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.menu),
          tooltip: 'Open Workspace Menu',
          onPressed: () => _scaffoldKey.currentState?.openDrawer(),
        ),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.2),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: AppColors.primary),
              ),
              child: const Text('NEXUS MIND', style: TextStyle(color: AppColors.primary, fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                widget.title,
                style: const TextStyle(fontSize: 14, overflow: TextOverflow.ellipsis),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            tooltip: 'Sync Workspace',
            onPressed: () {
              ref.read(workspaceProvider.notifier).loadWorkspace();
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Workspace synced!'), duration: Duration(seconds: 1)));
            },
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
              type: BottomNavigationBarType.fixed,
              backgroundColor: AppColors.surface,
              selectedItemColor: AppColors.primary,
              unselectedItemColor: AppColors.textMuted,
              currentIndex: _getBottomNavIndex(widget.selectedIndex),
              onTap: (navIndex) {
                if (navIndex == 0) widget.onDestinationSelected(0); // Dashboard
                if (navIndex == 1) widget.onDestinationSelected(2); // Kanban / Tasks
                if (navIndex == 2) widget.onDestinationSelected(1); // Graph
                if (navIndex == 3) widget.onDestinationSelected(7); // Meetings
                if (navIndex == 4) widget.onDestinationSelected(3); // Copilot
              },
              items: const [
                BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), activeIcon: Icon(Icons.dashboard), label: 'Dashboard'),
                BottomNavigationBarItem(icon: Icon(Icons.view_kanban_outlined), activeIcon: Icon(Icons.view_kanban), label: 'Tasks'),
                BottomNavigationBarItem(icon: Icon(Icons.hub_outlined), activeIcon: Icon(Icons.hub), label: 'Graph'),
                BottomNavigationBarItem(icon: Icon(Icons.videocam_outlined), activeIcon: Icon(Icons.videocam), label: 'Meetings'),
                BottomNavigationBarItem(icon: Icon(Icons.psychology_outlined), activeIcon: Icon(Icons.psychology), label: 'Copilot'),
              ],
            ),
    );
  }

  int _getBottomNavIndex(int selectedIndex) {
    if (selectedIndex == 0) return 0; // Dashboard
    if (selectedIndex == 2) return 1; // Tasks
    if (selectedIndex == 1) return 2; // Graph
    if (selectedIndex == 7) return 3; // Meetings
    if (selectedIndex == 3) return 4; // Copilot
    return 0;
  }

  Widget _buildDrawer(BuildContext context, UserModel? user) {
    final drawerItems = [
      {'index': 0, 'icon': Icons.dashboard, 'label': 'Operations Dashboard'},
      {'index': 1, 'icon': Icons.hub, 'label': 'Live Task Graph'},
      {'index': 2, 'icon': Icons.view_kanban, 'label': 'Kanban Task Board'},
      {'index': 3, 'icon': Icons.psychology, 'label': 'Autonomous AI Copilot'},
      {'index': 7, 'icon': Icons.videocam, 'label': 'Meetings & Video Bridge'},
      {'index': 5, 'icon': Icons.menu_book, 'label': 'RAG Knowledge Center'},
      {'index': 4, 'icon': Icons.security, 'label': 'Cybersecurity Threat Radar'},
      {'index': 6, 'icon': Icons.code, 'label': 'Engineering Intelligence & CI/CD'},
      {'index': 8, 'icon': Icons.account_tree, 'label': 'Architecture Explorer'},
    ];

    return Drawer(
      backgroundColor: AppColors.background,
      child: Column(
        children: [
          UserAccountsDrawerHeader(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF0D1220), Color(0xFF1E293B)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            accountName: Text(user?.name ?? 'Workspace User', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            accountEmail: Text('${user?.email ?? "user@nexusmind.ai"} • ${user?.role ?? "Member"}', style: const TextStyle(color: AppColors.primary, fontSize: 12)),
            currentAccountPicture: CircleAvatar(
              backgroundColor: AppColors.primary,
              child: Text(user?.avatar ?? 'NM', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
            ),
          ),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                ...drawerItems.map((item) {
                  final idx = item['index'] as int;
                  final isSelected = widget.selectedIndex == idx;
                  return ListTile(
                    leading: Icon(item['icon'] as IconData, color: isSelected ? AppColors.primary : AppColors.textSecondary),
                    title: Text(item['label'] as String, style: TextStyle(color: isSelected ? AppColors.primary : AppColors.textPrimary, fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, fontSize: 13)),
                    selected: isSelected,
                    selectedTileColor: AppColors.primary.withOpacity(0.12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
                    onTap: () {
                      Navigator.pop(context);
                      widget.onDestinationSelected(idx);
                    },
                  );
                }),
                const Divider(color: AppColors.border, height: 24),
                ListTile(
                  leading: const Icon(Icons.logout, color: AppColors.danger),
                  title: const Text('Sign Out', style: TextStyle(color: AppColors.danger, fontWeight: FontWeight.bold, fontSize: 13)),
                  onTap: () {
                    Navigator.pop(context);
                    ref.read(authProvider.notifier).logout();
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
