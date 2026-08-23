import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class ArchitectureExplorerScreen extends StatelessWidget {
  const ArchitectureExplorerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.secondary.withOpacity(0.2), AppColors.surface],
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.secondary.withOpacity(0.5)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Nexus Mind Enterprise Architecture Explorer', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                SizedBox(height: 6),
                Text(
                  'End-to-End System Topology: Cross-Platform Flutter Client, FastAPI Async Engine, PostgreSQL / pgvector Hybrid RAG, Multi-Agent Swarm, Scikit-Learn ML Risk & What-If CPM Simulator.',
                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Architectural Layers
          _archLayer(
            title: '1. Presentation Layer (Cross-Platform)',
            subtitle: 'Flutter (Riverpod + Material 3) & React/Vite SPA with live SVG/CustomPainter Force Graph',
            icon: Icons.devices,
            color: AppColors.primary,
            technologies: ['Flutter SDK 3.x', 'Riverpod 2.5', 'Dio 5.7', 'CustomPainter', 'Material 3 Dark'],
          ),
          _archLayer(
            title: '2. Application Gateway & Security IAM',
            subtitle: 'FastAPI REST + Asynchronous WebSockets, JWT + RFC 6238 TOTP MFA, Fernet Secret Encryption',
            icon: Icons.security,
            color: AppColors.danger,
            technologies: ['FastAPI 0.115', 'Fernet AES-CBC', 'PyOTP', 'SHA-256 Hashing', 'RBAC Matrix'],
          ),
          _archLayer(
            title: '3. Autonomous Multi-Agent Swarm',
            subtitle: '5 Specialized AI Agents with Human-in-the-Loop Safe Action Proposal Protocol & Decision Traces',
            icon: Icons.psychology,
            color: AppColors.purple,
            technologies: ['PM Agent', 'Dev Agent', 'Security Agent', 'Knowledge Agent', 'Analytics Agent'],
          ),
          _archLayer(
            title: '4. Grounded RAG Knowledge & Vector Engine',
            subtitle: 'PDF/Markdown Parsing, Continuous Dense Semantic Embeddings, Hybrid BM25 Search & Grounded Citations',
            icon: Icons.menu_book,
            color: AppColors.secondary,
            technologies: ['PyPDF', 'Dense Vector Embeddings (dim=256)', 'BM25 Keyword Fusion', 'Reranker'],
          ),
          _archLayer(
            title: '5. Machine Learning & CPM Project Simulator',
            subtitle: 'RandomForestClassifier with Tree Feature Importances (XAI) & Critical Path Method (CPM) DAG Scheduler',
            icon: Icons.analytics,
            color: AppColors.success,
            technologies: ['Scikit-Learn 1.4', 'Random Forest', 'XAI Attribution', 'CPM Topological Engine'],
          ),
          _archLayer(
            title: '6. Persistence & Real-Time Transport',
            subtitle: 'PostgreSQL + pgvector, SQLite fallback engine, Redis Pub/Sub asynchronous broadcast manager',
            icon: Icons.storage,
            color: AppColors.warning,
            technologies: ['PostgreSQL 16', 'SQLAlchemy 2.0', 'Redis 5.0', 'WebSockets', 'Alembic 1.13'],
          ),
        ],
      ),
    );
  }

  Widget _archLayer({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required List<String> technologies,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
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
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 2),
                    Text(subtitle, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: technologies
                .map(
                  (t) => Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Text(t, style: const TextStyle(fontSize: 10, color: AppColors.textPrimary)),
                  ),
                )
                .toList(),
          ),
        ],
      ),
    );
  }
}
