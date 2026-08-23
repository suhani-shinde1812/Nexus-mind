import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final TextEditingController _emailController = TextEditingController(text: 'sarah.jenkins@nexusmind.ai');
  final TextEditingController _passwordController = TextEditingController(text: 'nexus-demo-2026');
  final TextEditingController _mfaController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 440),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Logo & Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.2), borderRadius: BorderRadius.circular(8), border: Border.all(color: AppColors.primary)),
                      child: const Icon(Icons.hub, color: AppColors.primary, size: 24),
                    ),
                    const SizedBox(width: 12),
                    const Text('NEXUS MIND', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, letterSpacing: 1.5)),
                  ],
                ),
                const SizedBox(height: 6),
                const Text('Enterprise AI Engineering Operations Platform', textAlign: TextAlign.center, style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                const SizedBox(height: 24),

                if (authState.mfaRequired) ...[
                  const Text('Enter 6-Digit MFA TOTP Code', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _mfaController,
                    decoration: const InputDecoration(hintText: '123456', border: OutlineInputBorder()),
                    keyboardType: TextInputType.number,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, padding: const EdgeInsets.symmetric(vertical: 14)),
                    onPressed: () {},
                    child: const Text('Verify MFA'),
                  ),
                ] else ...[
                  TextField(
                    controller: _emailController,
                    decoration: const InputDecoration(labelText: 'Email Address', border: OutlineInputBorder()),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _passwordController,
                    decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                    obscureText: true,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, padding: const EdgeInsets.symmetric(vertical: 14)),
                    onPressed: () {
                      ref.read(authProvider.notifier).login(_emailController.text, _passwordController.text);
                    },
                    child: authState.isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text('Sign In to Platform'),
                  ),
                  const SizedBox(height: 24),
                  const Row(
                    children: [
                      Expanded(child: Divider(color: AppColors.border)),
                      Padding(padding: EdgeInsets.symmetric(horizontal: 8), child: Text('1-CLICK EXAMINER ACCESS', style: TextStyle(fontSize: 10, color: AppColors.textMuted, fontWeight: FontWeight.bold))),
                      Expanded(child: Divider(color: AppColors.border)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _demoButton('Sarah Jenkins', 'Team Lead Portal', AppColors.primary, () => ref.read(authProvider.notifier).loginDemo('team_lead')),
                  const SizedBox(height: 8),
                  _demoButton('Alex Vance', 'Frontend Lead / Employee Portal', AppColors.secondary, () => ref.read(authProvider.notifier).loginDemo('employee')),
                  const SizedBox(height: 8),
                  _demoButton('Marcus Chen', 'Project Manager Portal', AppColors.purple, () => ref.read(authProvider.notifier).loginDemo('project_manager')),
                  const SizedBox(height: 8),
                  _demoButton('Elena Rostova', 'Security Administrator Portal', AppColors.danger, () => ref.read(authProvider.notifier).loginDemo('admin')),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _demoButton(String name, String role, Color color, VoidCallback onTap) {
    return OutlinedButton(
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: color.withOpacity(0.5)),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 12),
        alignment: Alignment.centerLeft,
      ),
      onPressed: onTap,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(name, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: color)),
          Text(role, style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
        ],
      ),
    );
  }
}
