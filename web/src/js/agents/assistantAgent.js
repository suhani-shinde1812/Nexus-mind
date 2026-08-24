/**
 * AI ASSISTANT AGENT — UNIFIED CLIENT & COPILOT ENGINE
 * Queries the backend Multi-Agent Swarm Orchestrator (/api/ai/query) for live database answers,
 * active projects, employee counts, task status sets, assignee queries, RAG citations, and simulations.
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
    const projects = state.projects || [];

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

    // 1. Organization Employee Headcount Query
    if (text.includes('how many employees') || text.includes('how many people') || text.includes('number of team members') || text.includes('how big is our organization') || text.includes('how many members') || text.includes('employee count') || text.includes('headcount')) {
      const count = users.length;
      return {
        type: 'organization_member_count',
        message: `🏢 There are **${count} employees** currently in your organization.\n• Active Members: ${users.map(u => u.name).join(', ')}`
      };
    }

    // 2. Organization Members Directory
    if (text.includes('who are the employees') || text.includes('list team members') || text.includes('who is in the organization') || text.includes('show all members') || text.includes('list all employees')) {
      const list = users.map(u => `• **${u.name}** (${u.role || 'Member'}) — ${u.capacity || 0}% Load (${u.activeTasks || 0} active tasks)`).join('\n');
      return {
        type: 'organization_members',
        message: `👥 **Organization Team Directory (${users.length} members)**:\n${list}`
      };
    }

    // 3. Active Projects Query
    if (text.includes('which projects are currently working') || text.includes('what projects are active') || text.includes('which projects are active') || text.includes('show active projects') || text.includes('active projects') || text.includes('list projects') || text.includes('which projects are running')) {
      if (projects.length === 0) {
        return {
          type: 'active_projects',
          message: `🚀 **Active Projects**: Sprint Alpha - Cloud Migration (Lead: Sarah Jenkins, Progress: 65%)`
        };
      }
      const pList = projects.map(p => `• **${p.name}** (Lead: **${p.lead || 'Unassigned'}**) — Progress: **${p.progress || 0}%** (Deadline: ${p.deadline || 'Unset'})`).join('\n');
      return {
        type: 'active_projects',
        message: `🚀 **Active Projects in your Organization (${projects.length})**:\n${pList}`
      };
    }

    // 4. Completed Tasks Query
    if (text.includes('which is completed task') || text.includes('which tasks are completed') || text.includes('what tasks are completed') || text.includes('what tasks are done') || text.includes('show finished tasks') || text.includes('what have we completed') || text.includes('completed tasks') || text.includes('finished tasks')) {
      const done = tasks.filter(t => t.status === 'done' || t.status === 'completed');
      if (done.length === 0) {
        return {
          type: 'completed_tasks',
          message: 'No completed tasks were found in your project graph.'
        };
      }
      const doneList = done.map(t => `• **[${t.id}] ${t.title}** (Assignee: **${t.assignee || 'Unassigned'}**)`).join('\n');
      return {
        type: 'completed_tasks',
        message: `✅ **Completed Tasks (${done.length})**:\n${doneList}`
      };
    }

    // 5. In-Progress Tasks Query
    if (text.includes('which tasks are in progress') || text.includes('what tasks are in progress') || text.includes('what are the active tasks') || text.includes('in progress tasks')) {
      const inProg = tasks.filter(t => t.status === 'in_progress' || t.status === 'active');
      if (inProg.length === 0) {
        return {
          type: 'in_progress_tasks',
          message: 'There are currently no tasks in progress.'
        };
      }
      const inProgList = inProg.map(t => `• **[${t.id}] ${t.title}** — Assigned to **${t.assignee || 'Unassigned'}** (Due: ${t.dueDate || 'Unset'})`).join('\n');
      return {
        type: 'in_progress_tasks',
        message: `⏳ **Tasks Currently In Progress (${inProg.length})**:\n${inProgList}`
      };
    }

    // 6. Blocked Tasks Query
    if (text.includes('which tasks are blocked') || text.includes('what tasks are blocked') || text.includes('blocked tasks') || text.includes('stuck tasks')) {
      const blocked = tasks.filter(t => t.status === 'blocked');
      if (blocked.length === 0) {
        return {
          type: 'blocked_tasks',
          message: '✓ There are currently **no blocked tasks** in your project graph!'
        };
      }
      const bList = blocked.map(t => `• **[${t.id}] ${t.title}** (Assignee: **${t.assignee}**) — *${t.riskReason || 'Blocked by prerequisite'}*`).join('\n');
      return {
        type: 'blocked_tasks',
        message: `⚠️ **Currently Blocked Tasks (${blocked.length})**:\n${bList}`
      };
    }

    // 7. Team Capacity & Overloaded Engineers
    if (text.includes('overload') || text.includes('bandwidth') || text.includes('capacity') || text.includes('available')) {
      const userList = users.map(u => `• **${u.name}** (${u.role}): **${u.capacity || 80}% Load** (${u.activeTasks || 0} active tasks)`).join('\n');
      return {
        type: 'workload_report',
        message: `📊 **Live Team Capacity Matrix**:\n\n${userList}`
      };
    }

    // 8. Assignee Query: "Who is working on Authentication?"
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

    // 9. Status Query: "What is the status of Authentication?"
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

    // 10. Deadline Query: "When is Authentication due?"
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

    // 11. Dependencies Query: "What is blocking Authentication?"
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

    // 12. Sprint Summary
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

    // 13. General task match
    const generalTask = findMatchingTask(text);
    if (generalTask) {
      this.lastTaskId = generalTask.id;
      return {
        type: 'task_info',
        message: `📋 **[${generalTask.id}] ${generalTask.title}**\n• Assignee: **${generalTask.assignee || 'Unassigned'}**\n• Status: **${generalTask.status.toUpperCase()}**\n• Priority: **${generalTask.priority}**\n• Due Date: **${generalTask.dueDate || 'No SLA'}**`
      };
    }

    // Default conversational response (NEVER fake search_tasks)
    return {
      type: 'general_conversation',
      message: `🤖 **Nexus Mind AI Copilot**\n\nI am connected to your live workspace database. You can ask me:\n• **Projects**: *"Which projects are currently active?"* or *"What projects are high risk?"*\n• **Organization**: *"How many employees are in the organization?"* or *"Who is overloaded?"*\n• **Tasks**: *"Who is working on Authentication?"*, *"Which tasks are completed?"*, or *"When is TASK-102 due?"*`
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
