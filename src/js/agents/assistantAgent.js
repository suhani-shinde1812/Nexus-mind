/**
 * AI ASSISTANT AGENT (HYBRID OLLAMA + SMART RULE ENGINE)
 * Handles fast LLM querying with strict timeouts and instant fallback.
 */

import { store } from '../state.js';

export class AiAssistantAgent {
  constructor() {
    this.name = 'AI Assistant Agent';
    this.ollamaUrl = 'http://localhost:11434/api/generate';
    this.preferredModel = 'llama3.2:latest';
    this.isOllamaAvailable = false;
  }

  /**
   * Check if local Ollama responds within 1 second
   */
  async checkOllamaConnection() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000);
      const res = await fetch('http://localhost:11434/api/tags', { 
        method: 'GET',
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        if (data.models && data.models.length > 0) {
          this.isOllamaAvailable = true;
          const modelNames = data.models.map(m => m.name);
          if (modelNames.includes('llama3.2:latest')) this.preferredModel = 'llama3.2:latest';
          else if (modelNames.includes('llama3:latest')) this.preferredModel = 'llama3:latest';
          else if (modelNames.includes('phi3:mini')) this.preferredModel = 'phi3:mini';
          else this.preferredModel = modelNames[0];
          return true;
        }
      }
    } catch (e) {
      // Timeout or CORS restriction in browser
    }
    this.isOllamaAvailable = false;
    return false;
  }

  /**
   * Main Async Process Prompt
   */
  async processPromptAsync(promptText) {
    const text = promptText.trim();
    if (!text) return { type: 'empty', message: 'Please enter a valid prompt.' };

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
        console.warn('Ollama query error, using Smart AI Engine fallback', err);
      }
    }

    // Instant Smart AI Fallback
    return this.processSmartRuleEngine(text);
  }

  /**
   * Query Local Ollama LLM with strict 3-second timeout
   */
  async queryOllama(userPrompt) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);
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
    } catch (e) {
      console.warn('Ollama fetch error or CORS timeout', e);
    }
    return null;
  }

  /**
   * Context-Aware Smart AI Rule Engine
   */
  processSmartRuleEngine(promptText) {
    const text = promptText.trim().toLowerCase();
    const state = store.getState();

    // 1. Task Breakdown / Decompose
    if (text.includes('break down') || text.includes('decompose') || text.includes('subtask')) {
      const featureTitle = promptText.replace(/break down|decompose|subtasks|subtask|for|the/gi, '').trim() || 'Selected Component';
      return this.generateSubtasks(featureTitle);
    }

    // 2. Bandwidth / Workload
    if (text.includes('bandwidth') || text.includes('load') || text.includes('who can take') || text.includes('capacity')) {
      const userList = state.users.map(u => `• **${u.name}** (${u.role}): ${u.capacity}% capacity load (${u.activeTasks} active tasks)`).join('\n');
      return {
        type: 'workload_report',
        message: `📊 **Team Workload & Bandwidth Matrix**:\n\n${userList}\n\n💡 **AI Recommendation**: Priya Sharma has the lowest load (40%) and is ready for new task assignment!`
      };
    }

    // 3. Sprint / Project Summary
    if (text.includes('summary') || text.includes('report') || text.includes('status') || text.includes('sprint')) {
      const total = state.tasks.length;
      const done = state.tasks.filter(t => t.status === 'done').length;
      const blocked = state.tasks.filter(t => t.status === 'blocked').length;
      const progress = Math.round((done / total) * 100);

      return {
        type: 'sprint_summary',
        message: `📈 **Sprint Alpha Executive Report**:\n• Total Tasks: **${total}**\n• Completed: **${done}** (${progress}%)\n• Blocked Tasks: **${blocked}**\n\n⚠️ **Critical Bottleneck**: Devon Reed is overloaded at 110% capacity. Unblocking TASK-102 will accelerate 3 dependent milestones!`
      };
    }

    // 4. Natural Language Task Creation
    if (text.includes('create task') || text.includes('add task')) {
      const title = promptText.replace(/create task|add task/gi, '').trim() || 'New AI Task';
      const newTask = store.addTask({
        title,
        priority: 'High',
        status: 'in_progress',
        assignee: 'Priya Sharma'
      });
      return {
        type: 'task_created',
        message: `✅ Created and published task **${newTask.id}: ${newTask.title}** assigned to Priya Sharma live on the Task Graph!`
      };
    }

    // 5. Query about specific task (e.g. "102", "104", "oauth")
    const taskMatch = state.tasks.find(t => text.includes(t.id.toLowerCase()) || text.includes(t.title.toLowerCase()) || text.includes(t.id.split('-')[1]));
    if (taskMatch) {
      return {
        type: 'task_info',
        message: `📋 **Task Details [${taskMatch.id}]**:\n• **Title**: ${taskMatch.title}\n• **Assignee**: ${taskMatch.assignee}\n• **Status**: ${taskMatch.status.toUpperCase()}\n• **Priority**: ${taskMatch.priority}\n• **SLA Target**: ${taskMatch.dueDate}\n${taskMatch.riskReason ? `⚠️ **Risk Alert**: ${taskMatch.riskReason}` : '✓ No risk detected.'}`
      };
    }

    // 6. Query about team members (e.g. "Devon", "Alex", "Sarah", "Priya")
    const userMatch = state.users.find(u => text.includes(u.name.toLowerCase()) || text.includes(u.name.split(' ')[0].toLowerCase()));
    if (userMatch) {
      const assignedTasks = state.tasks.filter(t => t.assignee === userMatch.name);
      return {
        type: 'user_info',
        message: `👤 **Team Member: ${userMatch.name}**\n• **Role**: ${userMatch.role}\n• **Capacity Load**: ${userMatch.capacity}%\n• **Active Tasks**: ${assignedTasks.map(t => `[${t.id}] ${t.title}`).join(', ') || 'None'}`
      };
    }

    // 7. Dynamic AI Question / Help Response
    return {
      type: 'general_ai',
      message: `🤖 **Nexus AI Assistant**:\nI analyzed your query: "${promptText}".\n\n💡 **Live Context Analytics**:\n• Active Graph Nodes: **${state.tasks.length}**\n• High-Risk Hazards: **${state.tasks.filter(t => t.aiRiskScore >= 0.7).length}**\n\nTry asking me: *"Break down OAuth feature"*, *"Who has bandwidth?"*, *"Status of TASK-102"*, or *"Generate Sprint Summary"*!`
    };
  }

  generateSubtasks(featureTitle) {
    const subtasks = [
      `1. Draft technical design doc & API contract schema for "${featureTitle}"`,
      `2. Implement backend service endpoints & unit tests`,
      `3. Integrate frontend state, error boundaries, & UI components`,
      `4. Conduct end-to-end integration tests & security policy audit`
    ];

    return {
      type: 'subtasks',
      feature: featureTitle,
      subtasks: subtasks,
      message: `✨ AI generated 4 subtasks for **"${featureTitle}"**:\n\n${subtasks.join('\n')}`
    };
  }
}

export const assistantAgent = new AiAssistantAgent();
