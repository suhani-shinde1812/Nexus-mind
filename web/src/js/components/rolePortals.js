/**
 * NEXUS MIND - ROLE PORTALS & WORKSPACE VIEWS
 * Multi-role tailored portals: Employee, Team Lead, Project Manager, Administrator
 * Interactive tabs: Dashboard, Tasks, Autonomous AI Swarm, Analytics, Meetings, Knowledge Hub, Activity Trail.
 */
import { store } from '../state.js';
import { monitoringAgent } from '../agents/monitoringAgent.js';

export class RolePortals {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.activeTab = 'overview';
  }

  setTab(tabName) {
    this.activeTab = tabName;
    this.render();
  }

  render() {
    if (!this.container) return;

    const state = store.getState();
    const role = state.currentRole;

    if (this.activeTab === 'agents') {
      this.renderAgentsTab(state);
      return;
    }

    if (this.activeTab === 'analytics') {
      this.renderAnalyticsTab(state);
      return;
    }

    if (this.activeTab === 'meetings') {
      this.renderMeetingsTab(state);
      return;
    }

    if (this.activeTab === 'knowledge') {
      this.renderKnowledgeTab(state);
      return;
    }

    if (this.activeTab === 'activity') {
      this.renderActivityTab(state);
      return;
    }

    if (this.activeTab === 'tasks') {
      this.renderTasksTab(state);
      return;
    }

    switch (role) {
      case 'employee':
        this.renderEmployeePortal(state);
        break;
      case 'team_lead':
        this.renderTeamLeadPortal(state);
        break;
      case 'project_manager':
        this.renderProjectManagerPortal(state);
        break;
      case 'admin':
        this.renderAdminPortal(state);
        break;
      default:
        this.renderTeamLeadPortal(state);
    }
  }

  // --------------------------------------------------------------------------
  // 1. EMPLOYEE PORTAL
  // --------------------------------------------------------------------------
  renderEmployeePortal(state) {
    const userTasks = state.tasks.filter(t => t.assignee === state.currentUser.name);
    const activeTasks = userTasks.filter(t => t.status !== 'done');
    const doneTasks = userTasks.filter(t => t.status === 'done');

    this.container.innerHTML = `
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">MY ACTIVE TASKS</span>
          <span class="stat-card-value">${activeTasks.length}</span>
          <span class="stat-card-trend up">⚡ High Priority Focus</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">COMPLETED THIS SPRINT</span>
          <span class="stat-card-value">${doneTasks.length}</span>
          <span class="stat-card-trend up">↑ Velocity On Target</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">CURRENT WORKLOAD</span>
          <span class="stat-card-value" style="color: ${state.currentUser.capacity > 90 ? '#EF4444' : 'var(--cyan-primary)'};">${state.currentUser.capacity}%</span>
          <span class="stat-card-trend">💡 ${state.currentUser.capacity > 90 ? 'High capacity load' : 'Optimal bandwidth'}</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff;">📌 My Tasks & Active Work Queue</h3>
          <span class="text-muted" style="font-size: 0.75rem;">Showing ${userTasks.length} assigned task(s)</span>
        </div>

        <div class="task-list-container">
          ${userTasks.length > 0 ? userTasks.map(task => `
            <div class="task-item-card" data-task-id="${task.id}">
              <div class="task-item-main">
                <span class="task-status-pill ${task.status}">${task.status.replace('_', ' ')}</span>
                <div>
                  <div class="task-title">[${task.id}] ${task.title}</div>
                  <div class="task-meta">
                    <span>Project: ${task.project || 'General'}</span>
                    <span>Due: ${task.dueDate || 'No Due Date'}</span>
                    ${task.dependsOn && task.dependsOn.length > 0 ? `<span style="color:var(--cyan-primary);">🔗 ${task.dependsOn.join(', ')}</span>` : ''}
                  </div>
                </div>
              </div>
              <div style="display: flex; gap: 8px;">
                <button class="btn btn-ghost btn-xs btn-inspect-task" data-id="${task.id}">🔍 View</button>
                <button class="btn btn-primary btn-xs btn-complete-task" data-id="${task.id}">
                  ${task.status === 'done' ? 'Completed ✓' : 'Mark Done'}
                </button>
              </div>
            </div>
          `).join('') : '<p class="text-muted">No tasks assigned to your queue.</p>'}
        </div>
      </div>

      <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
        <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--cyan-primary); margin-bottom: 8px;">📤 Submit Work & Daily Engineer Standup Log</h4>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
          <input type="text" id="dailyLogInput" placeholder="Log today's code changes or PR link (e.g. Completed OAuth2 JWT refresh logic)..." style="flex:1; background: rgba(0,0,0,0.3); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; color: #fff; font-size: 0.825rem;" />
          <button id="btnSubmitDailyLog" class="btn btn-primary btn-sm">Submit Log</button>
        </div>
        <div id="logSuccessMsg" style="font-size: 0.75rem; color: var(--status-done); display: none;">✓ Standup entry committed to Live Task Graph Activity Trail!</div>
      </div>
    `;

    this.attachEmployeeEvents();
  }

  attachEmployeeEvents() {
    this.container.querySelectorAll('.btn-complete-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        store.updateTaskStatus(id, 'done');
        this.render();
      });
    });

    this.container.querySelectorAll('.btn-inspect-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        store.setView('graph');
        window.dispatchEvent(new CustomEvent('nexus:inspect-node', { detail: { taskId: id } }));
      });
    });

    const submitBtn = this.container.querySelector('#btnSubmitDailyLog');
    if (submitBtn) {
      submitBtn.addEventListener('click', () => {
        const input = this.container.querySelector('#dailyLogInput');
        if (input && input.value.trim()) {
          store.addActivityLog('DAILY-LOG', 'standup_entry', null, input.value.trim());
          store.addToast('Standup Logged', 'Your daily update was recorded on the activity trail.', 'success');
          input.value = '';
          const msg = this.container.querySelector('#logSuccessMsg');
          if (msg) {
            msg.style.display = 'block';
            setTimeout(() => msg.style.display = 'none', 3500);
          }
        }
      });
    }
  }

  // --------------------------------------------------------------------------
  // 2. TEAM LEAD PORTAL
  // --------------------------------------------------------------------------
  renderTeamLeadPortal(state) {
    const tasks = state.tasks;
    const blockedCount = tasks.filter(t => t.status === 'blocked').length;
    const highRiskCount = tasks.filter(t => t.aiRiskScore >= 0.7 && t.status !== 'done').length;

    this.container.innerHTML = `
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">ACTIVE SPRINT TASKS</span>
          <span class="stat-card-value">${tasks.length}</span>
          <span class="stat-card-trend up">${Math.round((tasks.filter(t => t.status === 'done').length / tasks.length) * 100)}% Overall Completion</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">BLOCKED BOTTLENECKS</span>
          <span class="stat-card-value" style="color: var(--status-blocked);">${blockedCount}</span>
          <span class="stat-card-trend warn">⚠️ Requires Lead Unblocking</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">AI HIGH RISK HALOS</span>
          <span class="stat-card-value" style="color: var(--status-risk);">${highRiskCount}</span>
          <span class="stat-card-trend warn">🔴 Pulsing on Live Graph</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff;">👥 Team Member Capacity & Workload Balance</h3>
          <button class="btn btn-ghost btn-xs" id="btnLeadAutoRebalance">⚡ Run AI Rebalance</button>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px;">
          ${state.users.map(u => `
            <div style="background: var(--bg-card); border: 1px solid ${u.capacity > 95 ? '#EF4444' : 'var(--border-color)'}; border-radius: 8px; padding: 10px;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600;">
                <span>${u.name} (${u.role})</span>
                <span style="color: ${u.capacity > 95 ? '#EF4444' : 'var(--cyan-primary)'};">${u.capacity}% Load</span>
              </div>
              <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; margin-top: 6px; overflow: hidden;">
                <div style="width: ${Math.min(100, u.capacity)}%; height: 100%; background: ${u.capacity > 95 ? '#EF4444' : 'var(--cyan-primary)'};"></div>
              </div>
              <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px;">Active: ${u.activeTasks} task(s) • Skills: ${u.skills.slice(0, 3).join(', ')}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <div>
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">📋 Approvals & Hazard Review Queue</h3>
        <div class="task-list-container">
          ${tasks.filter(t => (t.status === 'blocked' || t.priority === 'Critical' || t.aiRiskScore >= 0.7) && t.status !== 'done').map(task => `
            <div class="task-item-card" data-task-id="${task.id}">
              <div class="task-item-main">
                <span class="task-status-pill ${task.status}">${task.status.replace('_', ' ')}</span>
                <div>
                  <div class="task-title">[${task.id}] ${task.title}</div>
                  <div class="task-meta">
                    <span>Owner: ${task.assignee}</span>
                    <span style="color:#EF4444;">${task.riskReason ? 'Risk: ' + task.riskReason : ''}</span>
                  </div>
                </div>
              </div>
              <div style="display: flex; gap: 6px;">
                <button class="btn btn-ghost btn-xs btn-inspect-task" data-id="${task.id}">🔍 Inspect</button>
                <button class="btn btn-primary btn-xs btn-unblock-task" data-id="${task.id}">Unblock Node</button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    this.attachTeamLeadEvents();
  }

  attachTeamLeadEvents() {
    this.container.querySelectorAll('.btn-unblock-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        store.updateTaskStatus(id, 'in_progress');
        this.render();
      });
    });

    this.container.querySelectorAll('.btn-inspect-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        store.setView('graph');
        window.dispatchEvent(new CustomEvent('nexus:inspect-node', { detail: { taskId: id } }));
      });
    });

    const rebalanceBtn = this.container.querySelector('#btnLeadAutoRebalance');
    if (rebalanceBtn) {
      rebalanceBtn.addEventListener('click', () => {
        store.autoRebalanceWorkload();
        this.render();
      });
    }
  }

  // --------------------------------------------------------------------------
  // 3. PROJECT MANAGER PORTAL
  // --------------------------------------------------------------------------
  renderProjectManagerPortal(state) {
    this.container.innerHTML = `
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">PROJECT HEALTH INDEX</span>
          <span class="stat-card-value" style="color: var(--cyan-primary);">86%</span>
          <span class="stat-card-trend up">↑ On-Time Delivery: ${state.sprintForecast.onTimeProbability}%</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">PREDICTED SLA DELAY</span>
          <span class="stat-card-value">${state.sprintForecast.expectedDelayDays} Days</span>
          <span class="stat-card-trend warn">⚠️ Critical Path on Sprint Alpha</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">ACTIVE PROJECTS</span>
          <span class="stat-card-value">${state.projects.length}</span>
          <span class="stat-card-trend up">Cloud, Mobile, Security</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">🚀 Sprint Planning & Delivery Trajectory</h3>
        ${state.projects.map(p => `
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700;">
              <span>${p.name}</span>
              <span style="color: var(--cyan-primary);">${p.progress}% Completed</span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Lead: ${p.lead} • Target Deadline: ${p.deadline}</div>
            <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; margin-top: 8px; overflow: hidden;">
              <div style="width: ${p.progress}%; height: 100%; background: linear-gradient(90deg, var(--cyan-primary), var(--purple-primary));"></div>
            </div>
          </div>
        `).join('')}
      </div>

      <div style="background: rgba(127,0,255,0.08); border: 1px solid var(--purple-primary); border-radius: 12px; padding: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <h4 style="font-size: 0.85rem; font-weight: 700; color: #fff;">🧠 AI Monte Carlo Delivery Forecast</h4>
          <button class="btn btn-ghost btn-xs" id="btnExportBriefing">Export Executive Report</button>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">
          The AI Multi-Agent Swarm computed <strong>${state.sprintForecast.simulationRuns} stochastic simulations</strong>. Current probability of hitting the Sprint Alpha release on schedule is <strong>${state.sprintForecast.onTimeProbability}%</strong> with an expected delay variance of <strong>${state.sprintForecast.expectedDelayDays} days</strong>.
        </p>
      </div>
    `;

    const exportBtn = this.container.querySelector('#btnExportBriefing');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => {
        const report = store.generateExecutiveSprintReport();
        const blob = new Blob([report], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `NexusMind-Sprint-Briefing-${new Date().toISOString().slice(0, 10)}.md`;
        a.click();
        store.addToast('Report Exported', 'Downloaded Sprint Executive Briefing in Markdown.', 'success');
      });
    }
  }

  // --------------------------------------------------------------------------
  // 4. ADMINISTRATOR PORTAL
  // --------------------------------------------------------------------------
  renderAdminPortal(state) {
    const stats = state.systemStats;

    this.container.innerHTML = `
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">GRAPH ENGINE NODES</span>
          <span class="stat-card-value">${stats.graphNodeCount} Nodes</span>
          <span class="stat-card-trend up">${stats.graphEdgeCount} Active Edges</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">AI INFERENCE LATENCY</span>
          <span class="stat-card-value" style="color: var(--cyan-primary);">${stats.aiInferenceLatency}</span>
          <span class="stat-card-trend up">⚡ Sub-second neural response</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">SYSTEM MEMORY LOAD</span>
          <span class="stat-card-value">${stats.memoryUsage}</span>
          <span class="stat-card-trend">CPU Load: ${stats.cpuLoad}</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">🛡️ Organization Roles & Security Matrix</h3>
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden;">
          <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem; color: var(--text-primary);">
            <thead>
              <tr style="background: rgba(255,255,255,0.05); text-align: left;">
                <th style="padding: 10px;">User</th>
                <th style="padding: 10px;">Role</th>
                <th style="padding: 10px;">Permissions</th>
                <th style="padding: 10px;">Status</th>
              </tr>
            </thead>
            <tbody>
              ${state.users.map(u => `
                <tr style="border-top: 1px solid var(--border-color);">
                  <td style="padding: 10px; font-weight: 600;">${u.name}</td>
                  <td style="padding: 10px; color: var(--cyan-primary);">${u.role}</td>
                  <td style="padding: 10px; color: var(--text-secondary);">Full Read/Write, Live Graph Access</td>
                  <td style="padding: 10px;"><span style="color: var(--status-done);">● Active</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  // --------------------------------------------------------------------------
  // 5. TASKS MATRIX TAB
  // --------------------------------------------------------------------------
  renderTasksTab(state) {
    this.container.innerHTML = `
      <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff;">📋 All Sprint Alpha Engineering Tasks</h3>
        <span class="text-muted" style="font-size: 0.75rem;">${state.tasks.length} total tasks</span>
      </div>

      <div class="task-list-container">
        ${state.tasks.map(task => `
          <div class="task-item-card" data-task-id="${task.id}">
            <div class="task-item-main">
              <span class="task-status-pill ${task.status}">${task.status.replace('_', ' ')}</span>
              <div>
                <div class="task-title">[${task.id}] ${task.title}</div>
                <div class="task-meta">
                  <span>👤 ${task.assignee}</span>
                  <span>Project: ${task.project || 'General'}</span>
                  <span>Due: ${task.dueDate || 'Unset'}</span>
                </div>
              </div>
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-ghost btn-xs btn-inspect-task" data-id="${task.id}">🔍 Inspect</button>
              <button class="btn btn-primary btn-xs btn-complete-task" data-id="${task.id}">
                ${task.status === 'done' ? 'Completed ✓' : 'Mark Done'}
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    this.container.querySelectorAll('.btn-inspect-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        store.setView('graph');
        window.dispatchEvent(new CustomEvent('nexus:inspect-node', { detail: { taskId: id } }));
      });
    });

    this.container.querySelectorAll('.btn-complete-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        store.updateTaskStatus(id, 'done');
        this.render();
      });
    });
  }

  // --------------------------------------------------------------------------
  // 6. AUTONOMOUS AI SWARM TAB
  // --------------------------------------------------------------------------
  renderAgentsTab(state) {
    const report = monitoringAgent.analyzeGraphRisks();

    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3 style="font-size: 1rem; color: #fff; font-weight: 700;">🤖 Autonomous AI Agent Swarm</h3>
          <button class="btn btn-gradient btn-xs glow-cyan" id="btnSwarmRescan">⚡ Trigger Swarm Scan</button>
        </div>

        <!-- 3 Core Agents Grid -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
          <!-- Agent 1 -->
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
              <span style="font-size: 1.3rem;">🤖</span>
              <span class="task-status-pill done">Active</span>
            </div>
            <h4 style="font-size: 0.85rem; color: #fff; font-weight: 700;">1. AI Monitoring Agent</h4>
            <p style="font-size: 0.725rem; color: var(--text-secondary); margin-top: 4px;">Topological sort, critical path calculation, and SLA risk halos.</p>
          </div>

          <!-- Agent 2 -->
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
              <span style="font-size: 1.3rem;">💡</span>
              <span class="task-status-pill in_progress">Co-Pilot</span>
            </div>
            <h4 style="font-size: 0.85rem; color: #fff; font-weight: 700;">2. AI Assistant Agent</h4>
            <p style="font-size: 0.725rem; color: var(--text-secondary); margin-top: 4px;">Generative subtask decomposition, sprint briefings, graph queries.</p>
          </div>

          <!-- Agent 3 -->
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
              <span style="font-size: 1.3rem;">⚖️</span>
              <span class="task-status-pill done">Optimizer</span>
            </div>
            <h4 style="font-size: 0.85rem; color: #fff; font-weight: 700;">3. Workload Rebalancer</h4>
            <p style="font-size: 0.725rem; color: var(--text-secondary); margin-top: 4px;">Skill vector cosine similarity & capacity load leveling.</p>
          </div>
        </div>

        <!-- Real-Time Agent Reasoning Stream -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px;">
          <h4 style="font-size: 0.85rem; color: var(--cyan-primary); font-weight: 700; margin-bottom: 12px;">⚡ Live Agent Swarm Reasoning Stream</h4>
          <div style="display: flex; flex-direction: column; gap: 8px; max-height: 220px; overflow-y: auto;">
            ${state.agentSwarmLogs.map(log => `
              <div style="display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 8px 12px;">
                <div>
                  <span style="font-size: 0.75rem; font-weight: 700; color: #fff;">${log.agent}</span>
                  <span style="font-size: 0.65rem; color: var(--cyan-primary); margin-left: 6px;">[${log.action}]</span>
                  <div style="font-size: 0.725rem; color: var(--text-secondary); margin-top: 2px;">${log.message}</div>
                </div>
                <span style="font-size: 0.65rem; color: var(--text-muted);">${log.time}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

    const rescanBtn = this.container.querySelector('#btnSwarmRescan');
    if (rescanBtn) {
      rescanBtn.addEventListener('click', () => {
        monitoringAgent.analyzeGraphRisks();
        store.addToast('AI Swarm Scan Complete', 'Evaluated all graph dependencies & SLA risk factors.', 'success');
        this.render();
      });
    }
  }

  // --------------------------------------------------------------------------
  // 7. EXECUTIVE ANALYTICS TAB
  // --------------------------------------------------------------------------
  renderAnalyticsTab(state) {
    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3 style="font-size: 1rem; color: #fff; font-weight: 700;">📊 Live Sprint Analytics & Risk Intelligence</h3>
          <span class="badge-pill in-progress">Sprint Delivery: ${state.sprintForecast.onTimeProbability}%</span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.85rem; color: #fff; margin-bottom: 12px;">Task Status Distribution</h4>
            <canvas id="taskStatusChart" style="max-height: 220px;"></canvas>
          </div>

          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.85rem; color: #fff; margin-bottom: 12px;">Engineer Capacity Load (%)</h4>
            <canvas id="capacityLoadChart" style="max-height: 220px;"></canvas>
          </div>
        </div>
      </div>
    `;

    setTimeout(() => {
      if (window.Chart) {
        const c1 = document.getElementById('taskStatusChart');
        if (c1) {
          new window.Chart(c1, {
            type: 'doughnut',
            data: {
              labels: ['Completed', 'In Progress', 'Blocked', 'High Risk'],
              datasets: [{
                data: [
                  state.tasks.filter(t => t.status === 'done').length,
                  state.tasks.filter(t => t.status === 'in_progress').length,
                  state.tasks.filter(t => t.status === 'blocked').length,
                  state.tasks.filter(t => t.aiRiskScore >= 0.7).length
                ],
                backgroundColor: ['#10B981', '#3B82F6', '#EF4444', '#F59E0B']
              }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#CBD5E1', font: { size: 10 } } } } }
          });
        }

        const c2 = document.getElementById('capacityLoadChart');
        if (c2) {
          new window.Chart(c2, {
            type: 'bar',
            data: {
              labels: state.users.map(u => u.name.split(' ')[0]),
              datasets: [{
                label: 'Workload %',
                data: state.users.map(u => u.capacity),
                backgroundColor: state.users.map(u => u.capacity > 95 ? '#EF4444' : '#00F2FE')
              }]
            },
            options: {
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                y: { beginAtZero: true, max: 130, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } },
                x: { ticks: { color: '#94A3B8' } }
              }
            }
          });
        }
      }
    }, 100);
  }

  // --------------------------------------------------------------------------
  // 8. TEAM MEETINGS TAB
  // --------------------------------------------------------------------------
  renderMeetingsTab(state) {
    const meetings = state.meetings || [];
    const upcoming = meetings.filter(m => m.status === 'scheduled');
    const cancelled = meetings.filter(m => m.status === 'cancelled');

    this.container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h3 style="font-size: 1rem; font-weight: 700; color: #fff;">🗓️ Team Video Meetings & Standups</h3>
        <button class="btn btn-primary btn-sm btn-open-meeting-modal">📅 Schedule Meeting</button>
      </div>

      <div class="task-list-container">
        ${upcoming.map(m => `
          <div class="task-item-card" data-meeting-id="${m.id}" style="flex-direction: column; align-items: stretch; gap: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <div class="task-title">📅 ${m.title}</div>
                <div class="task-meta">
                  <span>${m.date} • ${m.time} (${m.duration} min)</span>
                  <span>Project: ${m.project}</span>
                </div>
              </div>
              <span class="search-item-tag">Organizer: ${m.organizer}</span>
            </div>

            ${m.agenda ? `<p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">${m.agenda}</p>` : ''}

            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
              ${m.attendees.map(a => `<span style="font-size: 0.7rem; background: rgba(255,255,255,0.06); padding: 3px 9px; border-radius: 10px; color: var(--text-secondary);">👤 ${a}</span>`).join('')}
            </div>

            <div style="display: flex; gap: 8px; margin-top: 4px;">
              <button class="btn btn-primary btn-xs btn-join-meeting" data-id="${m.id}">🎥 Join Live Video Room</button>
              <button class="btn btn-ghost btn-xs btn-cancel-meeting" data-id="${m.id}" style="color:#EF4444; border-color:#EF4444;">Cancel</button>
            </div>
          </div>
        `).join('')}
        ${upcoming.length === 0 ? '<p class="text-muted">No meetings currently scheduled.</p>' : ''}
      </div>
    `;

    this.attachMeetingsEvents();
  }

  attachMeetingsEvents() {
    this.container.querySelectorAll('.btn-join-meeting').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        const meeting = store.getState().meetings.find(m => m.id === id);
        if (meeting) this.openLiveMeeting(meeting);
      });
    });

    this.container.querySelectorAll('.btn-cancel-meeting').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        if (confirm('Cancel this scheduled meeting?')) {
          store.cancelMeeting(id);
          this.render();
        }
      });
    });

    const openModalBtn = this.container.querySelector('.btn-open-meeting-modal');
    if (openModalBtn) {
      openModalBtn.addEventListener('click', () => {
        const modal = document.getElementById('meetingModal');
        if (modal) modal.classList.remove('hidden');
      });
    }
  }

  openLiveMeeting(meeting) {
    const modal = document.getElementById('liveMeetingModal');
    const container = document.getElementById('jitsiContainer');
    const title = document.getElementById('liveMeetingTitle');
    const roomLabel = document.getElementById('liveMeetingRoom');

    if (!modal || !container) return;

    if (window.nexusJitsiApi) {
      try { window.nexusJitsiApi.dispose(); } catch {}
      window.nexusJitsiApi = null;
    }

    container.innerHTML = '';
    const safeTitle = (meeting.title || 'TeamMeeting').replace(/[^a-zA-Z0-9]/g, '').substring(0, 25);
    const roomName = `NexusMind-${safeTitle}-${meeting.id}`;

    if (title) title.textContent = `🎥 ${meeting.title}`;
    if (roomLabel) roomLabel.textContent = `${meeting.date} • ${meeting.time}`;
    modal.classList.remove('hidden');

    if (typeof window.JitsiMeetExternalAPI === 'function') {
      window.nexusJitsiApi = new window.JitsiMeetExternalAPI('meet.jit.si', {
        roomName,
        parentNode: container,
        width: '100%',
        height: '100%',
        userInfo: { displayName: store.getState().currentUser.name }
      });
    }
  }

  // --------------------------------------------------------------------------
  // 9. KNOWLEDGE BASE & POLICY HUB TAB
  // --------------------------------------------------------------------------
  renderKnowledgeTab(state) {
    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3 style="font-size: 1rem; font-weight: 700; color: #fff;">📄 SOP & Compliance Knowledge Hub</h3>
          <span class="text-muted" style="font-size: 0.75rem;">${state.policies.length} standard policies indexed</span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 10px;">
          ${state.policies.map(p => `
            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <h4 style="font-size: 0.875rem; color: #fff; font-weight: 700;">${p.title}</h4>
                <span class="search-item-tag">${p.category}</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4; margin-bottom: 8px;">${p.summary}</p>
              <div style="display: flex; gap: 6px;">
                ${p.tags.map(t => `<span style="font-size: 0.65rem; background: rgba(0,242,254,0.1); color: var(--cyan-primary); padding: 2px 8px; border-radius: 10px;">#${t}</span>`).join('')}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  // --------------------------------------------------------------------------
  // 10. ACTIVITY & AUDIT TRAIL TAB
  // --------------------------------------------------------------------------
  renderActivityTab(state) {
    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3 style="font-size: 1rem; font-weight: 700; color: #fff;">📜 Live Workspace Activity Trail & Audit Log</h3>
          <span class="text-muted" style="font-size: 0.75rem;">${state.activityLogs.length} events logged</span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 8px;">
          ${state.activityLogs.map(l => `
            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 14px;">
              <div>
                <span style="font-weight: 700; font-size: 0.8rem; color: var(--cyan-primary);">${l.actor}</span>
                <span style="font-size: 0.75rem; color: #fff; margin-left: 8px;">${l.eventType.replace('_', ' ').toUpperCase()}</span>
                <span style="font-size: 0.725rem; color: var(--text-secondary); margin-left: 6px;">[${l.taskId}] ${l.fromValue ? l.fromValue + ' ➔ ' : ''}${l.toValue || ''}</span>
              </div>
              <span style="font-size: 0.7rem; color: var(--text-muted);">${l.timestamp}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
}