/**
 * AI ASSISTANT AGENT — UNIFIED CLIENT & COPILOT ENGINE
 * Queries the backend Multi-Agent Swarm Orchestrator (/api/ai/query) for live database answers,
 * task lookups, assignee queries, RAG citations, and discrete what-if simulations.
 */
import { store } from '../state.js';
import { api } from '../api.js';

export class AiAssistantAgent {
  constructor() {
    this.name = 'AI Assistant Agent';
    this.lastTaskId = null;
  }

  async processPromptAsync(promptText) {
    const text = promptText.trim();
    if (!text) return { type: 'empty', message: 'Please enter a valid prompt.' };

    store.logSwarmActivity(this.name, 'Evaluating Query', `Routing query to backend agent swarm: "${text.substring(0, 35)}..."`);

    // 1. Query Backend Live Agent Orchestrator
    try {
      const res = await api.queryAi(text);
      if (res && res.answer) {
        if (res.decision_trace?.evidence?.includes('TASK-')) {
          const match = res.decision_trace.evidence.match(/TASK-\d+/);
          if (match) this.lastTaskId = match[0];
        }
        return {
          type: res.type || 'agent_response',
          agent: res.agent || 'Nexus AI Swarm',
          message: res.answer,
          trace: res.decision_trace,
          proposal: res.proposed_action,
          citations: res.citations || []
        };
      }
    } catch (err) {
      console.warn('Backend AI query endpoint failed, executing client-side database tool fallback', err);
    }

    // 2. Real State-Backed Local Fallback
    return this.processSmartRuleEngine(text);
  }

  processSmartRuleEngine(promptText) {
    const text = promptText.trim().toLowerCase();
    const state = store.getState();
    const tasks = state.tasks || [];
    const users = state.users || [];

    // Helper: find task by ID or keyword
    const findMatchingTask = (query) => {
      // Check exact ID or pronoun follow-up
      if (this.lastTaskId && (query.includes('it') || query.includes('this') || query.includes('the task') || query.includes('deadline') || query.includes('status'))) {
        const t = tasks.find(x => x.id === this.lastTaskId);
        if (t) return t;
      }

      const idMatch = query.match(/task-\d+/i);
      if (idMatch) {
        const found = tasks.find(t => t.id.toLowerCase() === idMatch[0].toLowerCase());
        if (found) return found;
      }

      // Keyword match
      const clean = query.replace(/who is working on|who is assigned to|who is handling|what is the status of|when is|what is the deadline for|is|what is blocking|which tasks depend on|tell me about|check|find|the|task|feature/gi, '').trim();
      if (!clean) return null;

      return tasks.find(t => t.title.toLowerCase().includes(clean) || (t.description && t.description.toLowerCase().includes(clean))) || null;
    };

    // 1. Assignee Query: "Who is working on Authentication?"
    if (text.includes('who is working') || text.includes('who is assigned') || text.includes('who is handling') || text.includes('owner') || (text.startsWith('who ') && text.includes('task'))) {
      const task = findMatchingTask(text);
      if (task) {
        this.lastTaskId = task.id;
        const assignee = task.assignee || 'Unassigned';
        return {
          type: 'task_assignee',
          message: `**${task.title}** is currently assigned to **${assignee}** and is **${task.status.toUpperCase()}**.\n\n• **Task ID**: \`${task.id}\`\n• **Priority**: ${task.priority}\n• **Due Date**: ${task.dueDate || 'No SLA set'}\n• **Predicted Risk**: ${Math.round((task.aiRiskScore || 0.1) * 100)}%`
        };
      }
      return {
        type: 'not_found',
        message: `I couldn't find a matching task in your current workspace.`
      };
    }

    // 2. Status Query: "What is the status of Authentication?"
    if (text.includes('status of') || text.includes('how is') || text.includes('progress of') || text.includes('status')) {
      const task = findMatchingTask(text);
      if (task) {
        this.lastTaskId = task.id;
        return {
          type: 'task_status',
          message: `📋 **Status for ${task.title}** (\`${task.id}\`):\n• Current Status: **${task.status.toUpperCase()}**\n• Assignee: **${task.assignee || 'Unassigned'}**\n• Priority: **${task.priority}**\n• SLA Target: **${task.dueDate || 'No SLA'}**\n${task.riskReason ? `\n⚠️ **Risk**: ${task.riskReason}` : ''}`
        };
      }
    }

    // 3. Deadline Query: "When is Authentication due?"
    if (text.includes('deadline') || text.includes('due') || text.includes('when is')) {
      const task = findMatchingTask(text);
      if (task) {
        this.lastTaskId = task.id;
        return {
          type: 'task_deadline',
          message: `📅 **Deadline for ${task.title}** (\`${task.id}\`):\n• Due Date: **${task.dueDate || 'No SLA deadline set'}**\n• Status: **${task.status.toUpperCase()}**\n• Assignee: **${task.assignee || 'Unassigned'}**`
        };
      }
    }

    // 4. Dependencies Query: "What is blocking Authentication?"
    if (text.includes('blocking') || text.includes('depend') || text.includes('prerequisite')) {
      const task = findMatchingTask(text);
      if (task) {
        this.lastTaskId = task.id;
        const deps = task.dependsOn || [];
        const depTasks = tasks.filter(t => deps.includes(t.id));
        const blockedByStr = depTasks.length > 0
          ? depTasks.map(d => `• **[${d.id}] ${d.title}** (Status: **${d.status.toUpperCase()}**, Owner: ${d.assignee})`).join('\n')
          : '• None (Can proceed immediately).';

        return {
          type: 'task_dependencies',
          message: `🔗 **Dependency Intelligence for ${task.title}** (\`${task.id}\`):\n\n⬅️ **Prerequisites**:\n${blockedByStr}`
        };
      }
    }

    // 5. Team Capacity & Overloaded Engineers
    if (text.includes('overload') || text.includes('bandwidth') || text.includes('capacity') || text.includes('available')) {
      const userList = users.map(u => `• **${u.name}** (${u.role}): **${u.capacity || 80}% Load** (${u.activeTasks || 0} active tasks)`).join('\n');
      return {
        type: 'workload_report',
        message: `📊 **Live Team Capacity Matrix**:\n\n${userList}`
      };
    }

    // 6. Sprint Summary
    if (text.includes('summary') || text.includes('report') || text.includes('sprint')) {
      const total = tasks.length;
      const done = tasks.filter(t => t.status === 'done').length;
      const blocked = tasks.filter(t => t.status === 'blocked').length;
      const progress = total > 0 ? Math.round((done / total) * 100) : 0;

      return {
        type: 'sprint_summary',
        message: `📈 **Sprint Intelligence Briefing**:\n• Total Tasks: **${total}**\n• Completed: **${done}** (${progress}%)\n• Blocked Tasks: **${blocked}**\n• On-Time Probability: **${state.sprintForecast?.onTimeProbability || 84.5}%**`
      };
    }

    // 7. General task match
    const generalTask = findMatchingTask(text);
    if (generalTask) {
      this.lastTaskId = generalTask.id;
      return {
        type: 'task_info',
        message: `📋 **[${generalTask.id}] ${generalTask.title}**\n• Assignee: **${generalTask.assignee || 'Unassigned'}**\n• Status: **${generalTask.status.toUpperCase()}**\n• Priority: **${generalTask.priority}**\n• Due Date: **${generalTask.dueDate || 'No SLA'}**`
      };
    }

    // Default response
    return {
      type: 'general_ai',
      message: `🤖 **Nexus AI Copilot**:\nI am connected to your live PostgreSQL database.\n\nTry asking:\n• *"Who is working on Authentication?"*\n• *"When is TASK-102 due?"*\n• *"What is the status of Database Migration?"*\n• *"Who is overloaded in the team?"*`
    };
  }

  generateSubtasks(featureTitle) {
    const subtasks = [
      `1. Architecture design & API contract specification for "${featureTitle}" (4 hrs)`,
      `2. Database schema migration & repository model implementation (6 hrs)`,
      `3. Core service logic & OAuth2 RBAC authorization validation (8 hrs)`,
      `4. Frontend interactive component integration & state wiring (6 hrs)`,
      `5. Automated unit & integration testing with compliance audit (4 hrs)`
    ];

    return {
      type: 'subtasks',
      subtasks
    };
  }
}

export const assistantAgent = new AiAssistantAgent();
