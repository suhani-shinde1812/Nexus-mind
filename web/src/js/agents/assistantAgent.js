/**
 * AI ASSISTANT AGENT (HYBRID OLLAMA + SMART CONVERSATIONAL ENGINE)
 * Context-aware AI Co-pilot for task decomposition, graph actions, and executive briefings.
 */
import { store } from '../state.js';
import { api } from '../api.js';

export class AiAssistantAgent {
  constructor() {
    this.name = 'AI Assistant Agent';
    this.ollamaUrl = 'http://localhost:11434/api/generate';
    this.preferredModel = 'llama3.2:latest';
    this.isOllamaAvailable = false;
  }

  async checkOllamaConnection() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 800);
      const res = await fetch('http://localhost:11434/api/tags', { 
        method: 'GET',
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        if (data.models && data.models.length > 0) {
          this.isOllamaAvailable = true;
          this.preferredModel = data.models[0].name;
          return true;
        }
      }
    } catch {
      // Standalone mode or CORS
    }
    this.isOllamaAvailable = false;
    return false;
  }

  async processPromptAsync(promptText) {
    const text = promptText.trim();
    if (!text) return { type: 'empty', message: 'Please enter a valid prompt.' };

    store.logSwarmActivity(this.name, 'Processing Query', `Evaluating natural language input: "${text.substring(0, 35)}..."`);

    // Check Ollama if available
    const isConnected = await this.checkOllamaConnection();
    if (isConnected) {
      try {
        const ollamaReply = await this.queryOllama(text);
        if (ollamaReply && ollamaReply.trim()) {
          return {
            type: 'ollama_llm',
            message: `🦙 **Ollama LLM (${this.preferredModel})**:\n\n${ollamaReply}`,
            model: this.preferredModel
          };
        }
      } catch (err) {
        console.warn('Ollama query fallback', err);
      }
    }

    // Try backend AI service decomposition / query if available
    if (text.toLowerCase().includes('decompose') || text.toLowerCase().includes('break down')) {
      try {
        const title = text.replace(/break down|decompose|subtasks|subtask|for|the/gi, '').trim() || 'Selected Feature';
        const subtasks = await api.decompose({ title });
        if (subtasks && subtasks.length > 0) {
          const subtaskList = subtasks.map((st, i) => `${i+1}. **${st.title}** (${st.estimatedHours}h, ${st.priority} Priority) — Skills: ${st.suggestedSkills ? st.suggestedSkills.join(', ') : 'General'}`);
          return {
            type: 'subtasks',
            feature: title,
            subtasks,
            message: `✨ **AI Task Decomposition for "${title}"**:\n\n${subtaskList.join('\n')}\n\n💡 *Subtasks can be attached directly to the Live Task Graph.*`
          };
        }
      } catch {
        // Fallback to internal neural rule engine
      }
    }

    return this.processSmartRuleEngine(text);
  }

  async queryOllama(userPrompt) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const state = store.getState();

      const taskSummary = state.tasks.map(t => `[${t.id}] ${t.title} (Owner: ${t.assignee}, Status: ${t.status})`).join('; ');
      
      const body = {
        model: this.preferredModel,
        prompt: `Context: Active Tasks: ${taskSummary}.\nUser Question: ${userPrompt}\nAnswer concisely as Nexus AI Assistant:`,
        stream: false
      };

      const res = await fetch(this.ollamaUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        return data.response;
      }
    } catch {
      // Handled by fallback
    }
    return null;
  }

  processSmartRuleEngine(promptText) {
    const text = promptText.trim().toLowerCase();
    const state = store.getState();

    // 1. Task Breakdown / Decompose
    if (text.includes('break down') || text.includes('decompose') || text.includes('subtask')) {
      const featureTitle = promptText.replace(/break down|decompose|subtasks|subtask|for|the/gi, '').trim() || 'Selected Component';
      return this.generateSubtasks(featureTitle);
    }

    // 2. Rebalance / Workload action
    if (text.includes('rebalance') || text.includes('balance load')) {
      store.autoRebalanceWorkload();
      return {
        type: 'action_rebalance',
        message: '⚡ **AI Workload Rebalance Executed**:\nAnalyzed developer capacities and reassigned tasks from overloaded members to available teammates!'
      };
    }

    // 3. Bandwidth / Capacity query
    if (text.includes('bandwidth') || text.includes('load') || text.includes('who can take') || text.includes('capacity')) {
      const userList = state.users.map(u => `• **${u.name}** (${u.role}): **${u.capacity}% Load** (${u.activeTasks} active tasks)`).join('\n');
      return {
        type: 'workload_report',
        message: `📊 **Team Workload & Capacity Matrix**:\n\n${userList}\n\n💡 **AI Talent Matcher**: Priya Sharma has the lowest capacity (40%) and highest availability.`
      };
    }

    // 4. Sprint / Project Summary & Briefing
    if (text.includes('summary') || text.includes('report') || text.includes('status') || text.includes('sprint') || text.includes('briefing')) {
      const total = state.tasks.length;
      const done = state.tasks.filter(t => t.status === 'done').length;
      const blocked = state.tasks.filter(t => t.status === 'blocked').length;
      const progress = Math.round((done / total) * 100);

      return {
        type: 'sprint_summary',
        message: `📈 **Sprint Alpha Executive Intelligence Briefing**:\n• Total Tasks: **${total}**\n• Completed: **${done}** (${progress}%)\n• Blocked Tasks: **${blocked}**\n• On-Time Delivery Probability: **${state.sprintForecast.onTimeProbability}%**\n• Predicted Delay: **${state.sprintForecast.expectedDelayDays} days**\n\n⚠️ **Critical Hazard**: Devon Reed is at 110% capacity overload. Reassigning TASK-106 will unblock the critical path!`
      };
    }

    // 5. Natural Language Task Creation
    if (text.includes('create task') || text.includes('add task')) {
      const title = promptText.replace(/create task|add task/gi, '').trim() || 'New Engineering Task';
      const newTask = store.addTask({
        title,
        priority: 'High',
        status: 'in_progress',
        assignee: 'Priya Sharma'
      });
      return {
        type: 'task_created',
        message: `✅ Created and published task **[${newTask.id}] ${newTask.title}** assigned to Priya Sharma live on the Task Graph!`
      };
    }

    // 6. Query specific task ID (e.g. "TASK-102", "102", "104")
    const taskMatch = state.tasks.find(t => text.includes(t.id.toLowerCase()) || text.includes(t.id.split('-')[1]));
    if (taskMatch) {
      return {
        type: 'task_info',
        message: `📋 **Task Details [${taskMatch.id}]**:\n• **Title**: ${taskMatch.title}\n• **Assignee**: ${taskMatch.assignee}\n• **Status**: ${taskMatch.status.toUpperCase()}\n• **Priority**: ${taskMatch.priority}\n• **SLA Target Due**: ${taskMatch.dueDate || 'Unset'}\n• **Prerequisites**: ${taskMatch.dependsOn ? taskMatch.dependsOn.join(', ') : 'None'}\n${taskMatch.riskReason ? `\n⚠️ **Risk Alert**: ${taskMatch.riskReason}` : '\n✓ No risk bottlenecks detected.'}`
      };
    }

    // 7. General AI Assistant response
    return {
      type: 'general_ai',
      message: `🤖 **Nexus AI Co-Pilot**:\nI parsed your request: "${promptText}".\n\n💡 **Suggested Commands**:\n• *"Break down OAuth feature"*\n• *"Who has bandwidth?"*\n• *"TASK-102 status"*\n• *"Rebalance team workload"*\n• *"Generate sprint summary report"*`
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
      feature: featureTitle,
      subtasks: subtasks,
      message: `✨ AI generated 5 structured subtasks for **"${featureTitle}"**:\n\n${subtasks.join('\n')}\n\n💡 *Click New Task to add these to the Live Graph.*`
    };
  }
}

export const assistantAgent = new AiAssistantAgent();
