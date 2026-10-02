import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../application/providers.dart';
import '../../../core/theme/app_theme.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Sign In controllers
  final TextEditingController _loginEmail = TextEditingController();
  final TextEditingController _loginPassword = TextEditingController();

  // Create Account controllers
  final TextEditingController _regName = TextEditingController();
  final TextEditingController _regEmail = TextEditingController();
  final TextEditingController _regPassword = TextEditingController();
  final TextEditingController _regSkills = TextEditingController(text: 'Python, Flutter, API');
  String _selectedRole = 'employee';

  final TextEditingController _mfaController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _loginEmail.dispose();
    _loginPassword.dispose();
    _regName.dispose();
    _regEmail.dispose();
    _regPassword.dispose();
    _regSkills.dispose();
    _mfaController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 460),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.border),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.4),
                  blurRadius: 30,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header Logo
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AppColors.primary.withOpacity(0.5)),
                      ),
                      child: const Icon(Icons.hub, color: AppColors.primary, size: 26),
                    ),
                    const SizedBox(width: 12),
                    RichText(
                      text: const TextSpan(
                        children: [
                          TextSpan(text: 'NEXUS', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Colors.white, letterSpacing: 1.5)),
                          TextSpan(text: 'MIND', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: AppColors.primary, letterSpacing: 1.5)),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  'Unified AI Workspace & Live Task Graph Platform',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                ),
                const SizedBox(height: 20),

                // Error Message Banner
                if (authState.error != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.danger.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.danger.withOpacity(0.5)),
                    ),
                    child: Text(
                      authState.error!,
                      style: const TextStyle(color: AppColors.danger, fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                  ),

                // Tabs: Sign In / Create Account
                Container(
                  decoration: BoxDecoration(
                    color: Colors.black26,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: TabBar(
                    controller: _tabController,
                    indicatorSize: TabBarIndicatorSize.tab,
                    indicator: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.25),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.primary.withOpacity(0.5)),
                    ),
                    labelColor: AppColors.primary,
                    unselectedLabelColor: AppColors.textSecondary,
                    labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    tabs: const [
                      Tab(text: 'Sign In'),
                      Tab(text: 'Create Account'),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Tab Content
                SizedBox(
                  height: 380,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      // TAB 1: SIGN IN
                      _buildSignInForm(context, authState),

                      // TAB 2: CREATE ACCOUNT
                      _buildRegisterForm(context, authState),
                    ],
                  ),
                ),

                // Collapsible 1-Click Demo
                const SizedBox(height: 12),
                Theme(
                  data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                  child: ExpansionTile(
                    tilePadding: EdgeInsets.zero,
                    title: const Text('⚡ Quick Demo Personas (Examiner Access)', style: TextStyle(fontSize: 11, color: AppColors.textMuted, fontWeight: FontWeight.bold)),
                    children: [
                      _demoButton('Sarah Jenkins', 'Team Lead (Sprint Alpha)', AppColors.primary, () => ref.read(authProvider.notifier).loginDemo('team_lead')),
                      const SizedBox(height: 6),
                      _demoButton('Alex Vance', 'Frontend Lead (Mobile App)', AppColors.secondary, () => ref.read(authProvider.notifier).loginDemo('employee')),
                      const SizedBox(height: 6),
                      _demoButton('Marcus Chen', 'Project Manager', AppColors.purple, () => ref.read(authProvider.notifier).loginDemo('project_manager')),
                      const SizedBox(height: 6),
                      _demoButton('Elena Rostova', 'Security Administrator', AppColors.danger, () => ref.read(authProvider.notifier).loginDemo('admin')),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSignInForm(BuildContext context, AuthState authState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _loginEmail,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Email Address',
            hintText: 'name@company.com',
            prefixIcon: Icon(Icons.email_outlined, size: 18),
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: _loginPassword,
          obscureText: true,
          decoration: const InputDecoration(
            labelText: 'Password',
            hintText: 'Enter your password',
            prefixIcon: Icon(Icons.lock_outline, size: 18),
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            padding: const EdgeInsets.symmetric(vertical: 14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          onPressed: authState.isLoading
              ? null
              : () {
                  final email = _loginEmail.text.trim();
                  final pwd = _loginPassword.text;
                  if (email.isEmpty || pwd.isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter email and password')));
                    return;
                  }
                  ref.read(authProvider.notifier).login(email, pwd);
                },
          child: authState.isLoading
              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
              : const Text('Sign In to Workspace', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        ),
      ],
    );
  }

  Widget _buildRegisterForm(BuildContext context, AuthState authState) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _regName,
            decoration: const InputDecoration(
              labelText: 'Full Name',
              hintText: 'e.g. Jordan Miller',
              prefixIcon: Icon(Icons.person_outline, size: 18),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _regEmail,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              labelText: 'Email Address',
              hintText: 'jordan@nexusmind.ai',
              prefixIcon: Icon(Icons.email_outlined, size: 18),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _regPassword,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Password (min 8 chars)',
              hintText: 'Create strong password',
              prefixIcon: Icon(Icons.lock_outline, size: 18),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(
            value: _selectedRole,
            decoration: const InputDecoration(
              labelText: 'Role',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.badge_outlined, size: 18),
            ),
            items: const [
              DropdownMenuItem(value: 'employee', child: Text('👨‍💻 Software Engineer')),
              DropdownMenuItem(value: 'team_lead', child: Text('👩‍💼 Team Lead')),
              DropdownMenuItem(value: 'project_manager', child: Text('📊 Project Manager')),
              DropdownMenuItem(value: 'admin', child: Text('🛡️ System Administrator')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _selectedRole = val);
            },
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _regSkills,
            decoration: const InputDecoration(
              labelText: 'Skills (comma separated)',
              hintText: 'Flutter, Python, React',
              prefixIcon: Icon(Icons.auto_awesome_outlined, size: 18),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.secondary,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: authState.isLoading
                ? null
                : () async {
                    final name = _regName.text.trim();
                    final email = _regEmail.text.trim();
                    final pwd = _regPassword.text;
                    if (name.isEmpty || email.isEmpty || pwd.length < 8) {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter valid details (password min 8 characters)')));
                      return;
                    }
                    final skills = _regSkills.text.split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
                    try {
                      await ref.read(authProvider.notifier).register({
                        'name': name,
                        'email': email,
                        'password': pwd,
                        'role': _selectedRole == 'employee' ? 'Software Engineer' : (_selectedRole == 'team_lead' ? 'Team Lead' : (_selectedRole == 'project_manager' ? 'Project Manager' : 'Administrator')),
                        'app_role': _selectedRole,
                        'skills': skills,
                      });
                    } catch (e) {
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Registration error: $e')));
                      }
                    }
                  },
            child: authState.isLoading
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text('Create Account & Enter', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
          ),
        ],
      ),
    );
  }

  Widget _demoButton(String name, String role, Color color, VoidCallback onTap) {
    return OutlinedButton(
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: color.withOpacity(0.4)),
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
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
