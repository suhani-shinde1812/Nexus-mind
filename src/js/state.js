/**
 * NEXUS MIND - STATE MANAGEMENT ENGINE
 * Reactive state store for tasks, graph dependencies, users, and AI alerts.
 */

const STORAGE_KEY = 'NEXUS_MIND_STATE_V3';

const DEFAULT_STATE = {
  theme: 'dark', // 'dark' | 'light'
  currentRole: 'team_lead',
  currentUser: {
    id: 'u2',
    name: 'Sarah Jenkins',
    role: 'Team Lead',
    avatar: 'SJ',
    email: 'sarah.jenkins@nexusmind.ai'
  },
  users: [
    { id: 'u1', name: 'Alex Vance', role: 'Frontend Lead', avatar: 'AV', capacity: 80, activeTasks: 3 },
    { id: 'u2', name: 'Sarah Jenkins', role: 'Team Lead', avatar: 'SJ', capacity: 60, activeTasks: 2 },
    { id: 'u3', name: 'Devon Reed', role: 'Backend Engineer', avatar: 'DR', capacity: 110, activeTasks: 5 }, // Overloaded
    { id: 'u4', name: 'Priya Sharma', role: 'AI/ML Engineer', avatar: 'PS', capacity: 40, activeTasks: 1 },
    { id: 'u5', name: 'Marcus Chen', role: 'Project Manager', avatar: 'MC', capacity: 50, activeTasks: 2 }
  ],
  projects: [
    { id: 'p1', name: 'Sprint Alpha - Cloud Migration', lead: 'Sarah Jenkins', deadline: '2026-08-15', progress: 65 },
    { id: 'p2', name: 'Mobile App v2.0', lead: 'Alex Vance', deadline: '2026-09-01', progress: 40 },
    { id: 'p3', name: 'Security & Compliance', lead: 'Elena Rostova', deadline: '2026-08-01', progress: 90 }
  ],
  tasks: [
    {
      id: 'TASK-101',
      title: 'Cloud Infrastructure Provisioning (Terraform)',
      project: 'Sprint Alpha - Cloud Migration',
      assignee: 'Devon Reed',
      status: 'done',
      priority: 'High',
      dependsOn: [],
      x: 120,
      y: 180,
      dueDate: '2026-07-20',
      aiRiskScore: 0.1,
      riskReason: null
    },
    {
      id: 'TASK-102',
      title: 'PostgreSQL Database Schema & Migration Script',
      project: 'Sprint Alpha - Cloud Migration',
      assignee: 'Devon Reed',
      status: 'in_progress',
      priority: 'Critical',
      dependsOn: ['TASK-101'],
      x: 300,
      y: 140,
      dueDate: '2026-07-28',
      aiRiskScore: 0.85,
      riskReason: 'Devon Reed is at 110% capacity & SLA deadline approaching.'
    },
    {
      id: 'TASK-103',
      title: 'OAuth2 Authentication API Gateway',
      project: 'Security & Compliance',
      assignee: 'Alex Vance',
      status: 'in_progress',
      priority: 'High',
      dependsOn: ['TASK-102'],
      x: 480,
      y: 140,
      dueDate: '2026-07-30',
      aiRiskScore: 0.75,
      riskReason: 'Prerequisite TASK-102 is at high risk of slipping.'
    },
    {
      id: 'TASK-104',
      title: 'React Dashboard UI & Role Authorization Views',
      project: 'Mobile App v2.0',
      assignee: 'Alex Vance',
      status: 'blocked',
      priority: 'High',
      dependsOn: ['TASK-103'],
      x: 660,
      y: 200,
      dueDate: '2026-08-05',
      aiRiskScore: 0.92,
      riskReason: 'BLOCKED by TASK-103 which is delayed downstream.'
    },
    {
      id: 'TASK-105',
      title: 'AI Assistant Vector Search Integration (Milvus)',
      project: 'Sprint Alpha - Cloud Migration',
      assignee: 'Priya Sharma',
      status: 'in_progress',
      priority: 'Medium',
      dependsOn: ['TASK-101'],
      x: 300,
      y: 320,
      dueDate: '2026-08-02',
      aiRiskScore: 0.2,
      riskReason: null
    },
    {
      id: 'TASK-106',
      title: 'Real-Time Notification Websocket Cluster',
      project: 'Mobile App v2.0',
      assignee: 'Devon Reed',
      status: 'blocked',
      priority: 'Medium',
      dependsOn: ['TASK-102', 'TASK-105'],
      x: 480,
      y: 320,
      dueDate: '2026-08-08',
      aiRiskScore: 0.8,
      riskReason: 'Assignee Devon Reed has 5 assigned tasks simultaneously.'
    },
    {
      id: 'TASK-107',
      title: 'Redis Caching Layer & Rate Limiter Middleware',
      project: 'Security & Compliance',
      assignee: 'Devon Reed',
      status: 'in_progress',
      priority: 'High',
      dependsOn: ['TASK-103'],
      x: 660,
      y: 340,
      dueDate: '2026-08-10',
      aiRiskScore: 0.65,
      riskReason: 'Depends on TASK-103 API Gateway.'
    },
    {
      id: 'TASK-108',
      title: 'End-to-End System SLA Monitoring Dashboard',
      project: 'Sprint Alpha - Cloud Migration',
      assignee: 'Sarah Jenkins',
      status: 'in_progress',
      priority: 'Critical',
      dependsOn: ['TASK-104', 'TASK-107'],
      x: 840,
      y: 260,
      dueDate: '2026-08-14',
      aiRiskScore: 0.4,
      riskReason: 'Final release milestone node.'
    }
  ],
  policies: [
    { 
      title: 'Remote Work Policy', 
      category: 'HR & Operations', 
      tags: ['work', 'policy', 'remote'], 
      summary: 'Flexible hybrid schedule requires mandatory daily standup updates and core working hours (10 AM - 4 PM IST).' 
    },
    { 
      title: 'SLA Escalation Guideline', 
      category: 'Engineering & QA', 
      tags: ['sla', 'critical', 'bugs'], 
      summary: 'P0 Critical Bugs must be acknowledged within 30 minutes and resolved within 24 hours with AI root-cause diagnostic reports.' 
    },
    { 
      title: 'Security Secret Storage Policy', 
      category: 'Infra & Security', 
      tags: ['oauth', 'credentials', 'vault'], 
      summary: 'All production secrets and API credentials must be stored in HashiCorp Vault. Storing raw tokens in repo is strictly prohibited.' 
    }
  ],
  aiAlerts: [
    {
      id: 'alt-1',
      severity: 'critical',
      title: 'Critical Path Hazard: Devon Reed',
      message: 'Devon Reed is assigned 5 concurrent tasks (110% capacity load). TASK-102 is blocking 3 downstream milestones.',
      timestamp: 'Just now',
      taskId: 'TASK-102'
    },
    {
      id: 'alt-2',
      severity: 'warning',
      title: 'Dependency SLA Delay',
      message: 'TASK-104 (React Dashboard UI) is currently BLOCKED by delayed OAuth2 API Gateway.',
      timestamp: '10 mins ago',
      taskId: 'TASK-104'
    },
    {
      id: 'alt-3',
      severity: 'info',
      title: 'AI Workload Rebalance Recommendation',
      message: 'Reassigning TASK-106 to Priya Sharma will reduce Devon Reed capacity load to 75% and unblock Sprint Alpha.',
      timestamp: '25 mins ago',
      taskId: 'TASK-106'
    }
  ],
  systemStats: {
    cpuLoad: '28%',
    memoryUsage: '3.4 / 8.0 GB',
    activeConnections: 142,
    graphNodeCount: 8,
    graphEdgeCount: 7,
    aiInferenceLatency: '184ms'
  }
};

class StateStore {
  constructor() {
    this.listeners = [];
    this.loadState();
  }

  loadState() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        this.state = JSON.parse(saved);
      } else {
        this.state = JSON.parse(JSON.stringify(DEFAULT_STATE));
        this.saveState();
      }
    } catch (e) {
      this.state = JSON.parse(JSON.stringify(DEFAULT_STATE));
    }
  }

  saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
      this.notify();
    } catch (e) {
      console.error('Failed to save state', e);
    }
  }

  getState() {
    return this.state;
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(fn => fn(this.state));
  }

  toggleTheme() {
    this.state.theme = this.state.theme === 'dark' ? 'light' : 'dark';
    this.saveState();
    return this.state.theme;
  }

  setRole(role) {
    this.state.currentRole = role;
    const roleUserMap = {
      employee: { id: 'u1', name: 'Alex Vance', role: 'Frontend Lead', avatar: 'AV', email: 'alex.vance@nexusmind.ai' },
      team_lead: { id: 'u2', name: 'Sarah Jenkins', role: 'Team Lead', avatar: 'SJ', email: 'sarah.jenkins@nexusmind.ai' },
      project_manager: { id: 'u5', name: 'Marcus Chen', role: 'Project Manager', avatar: 'MC', email: 'marcus.chen@nexusmind.ai' },
      admin: { id: 'u6', name: 'Elena Rostova', role: 'Administrator', avatar: 'ER', email: 'elena.rostova@nexusmind.ai' }
    };
    this.state.currentUser = roleUserMap[role] || roleUserMap.team_lead;
    this.saveState();
  }

  addTask(taskData) {
    const newId = `TASK-${100 + this.state.tasks.length + 1}`;
    const newTask = {
      id: newId,
      title: taskData.title,
      project: taskData.project || 'Sprint Alpha - Cloud Migration',
      assignee: taskData.assignee || 'Sarah Jenkins',
      status: taskData.status || 'in_progress',
      priority: taskData.priority || 'Medium',
      dependsOn: taskData.dependsOn ? [taskData.dependsOn] : [],
      x: 400 + (Math.random() * 120 - 60),
      y: 250 + (Math.random() * 120 - 60),
      dueDate: taskData.dueDate || '2026-08-10',
      aiRiskScore: 0.1,
      riskReason: null
    };

    this.state.tasks.push(newTask);
    this.state.systemStats.graphNodeCount = this.state.tasks.length;
    this.state.systemStats.graphEdgeCount += newTask.dependsOn.length;
    this.saveState();
    return newTask;
  }

  updateTaskStatus(taskId, status) {
    const task = this.state.tasks.find(t => t.id === taskId);
    if (task) {
      task.status = status;
      if (status === 'done') {
        task.aiRiskScore = 0.05;
        task.riskReason = null;
        this.state.tasks.forEach(t => {
          if (t.dependsOn.includes(taskId) && t.status === 'blocked') {
            t.status = 'in_progress';
            t.aiRiskScore = 0.2;
            t.riskReason = 'Unblocked by prerequisite completion!';
          }
        });
      }
      this.saveState();
    }
  }

  autoRebalanceWorkload() {
    const devonTasks = this.state.tasks.filter(t => t.assignee === 'Devon Reed' && t.status !== 'done');
    if (devonTasks.length > 0) {
      const taskToShift = devonTasks[devonTasks.length - 1];
      taskToShift.assignee = 'Priya Sharma';
      taskToShift.riskReason = 'Reassigned by AI Workload Rebalancer to optimize team velocity.';
      taskToShift.aiRiskScore = 0.25;

      const devon = this.state.users.find(u => u.name === 'Devon Reed');
      const priya = this.state.users.find(u => u.name === 'Priya Sharma');
      if (devon) { devon.capacity = 75; devon.activeTasks -= 1; }
      if (priya) { priya.capacity = 70; priya.activeTasks += 1; }

      this.addAlert({
        severity: 'info',
        title: '⚡ AI Workload Rebalanced!',
        message: `Successfully reassigned ${taskToShift.id} to Priya Sharma. Devon Reed capacity load reduced to 75%.`
      });

      this.saveState();
      return true;
    }
    return false;
  }

  addAlert(alertData) {
    const newAlert = {
      id: `alt-${Date.now()}`,
      severity: alertData.severity || 'warning',
      title: alertData.title,
      message: alertData.message,
      timestamp: 'Just now',
      taskId: alertData.taskId || null
    };
    this.state.aiAlerts.unshift(newAlert);
    this.saveState();
  }
}

export const store = new StateStore();
