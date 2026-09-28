/**
 * NEXUS MIND - ROLE PORTALS & WORKSPACE VIEWS
 * Multi-role tailored portals: Employee, Team Lead, Project Manager, Administrator
 * Interactive tabs: Dashboard, Tasks, War Room, Simulation, Analytics, Meetings, Knowledge Hub, Activity Trail.
 */
import { store } from '../state.js';
import { monitoringAgent } from '../agents/monitoringAgent.js';
import { warRoomAgent, AGENTS } from '../agents/warRoomAgent.js';
import { meetingIntelAgent } from '../agents/meetingIntelAgent.js';

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

    if (this.activeTab === 'simulation') {
      this.renderSimulationTab(state);
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
    const activeProjects = state.projects || [];
    const activeProjectsCount = activeProjects.length;
    const projectNames = activeProjectsCount > 0 ? activeProjects.map(p => p.name).join(', ') : 'No active projects';

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
          <span class="stat-card-trend warn">⚠️ Critical Path Delivery Risk</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">ACTIVE PROJECTS</span>
          <span class="stat-card-value">${activeProjectsCount}</span>
          <span class="stat-card-trend ${activeProjectsCount > 0 ? 'up' : ''}">${projectNames}</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">🚀 Sprint Planning & Delivery Trajectory</h3>
        ${activeProjectsCount > 0 ? activeProjects.map(p => `
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700;">
              <span>${p.name}</span>
              <span style="color: var(--cyan-primary);">${p.progress}% Completed</span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Lead: ${p.lead || 'Unassigned'} • Target Deadline: ${p.deadline || 'Unset'}</div>
            <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; margin-top: 8px; overflow: hidden;">
              <div style="width: ${p.progress}%; height: 100%; background: linear-gradient(90deg, var(--cyan-primary), var(--purple-primary));"></div>
            </div>
          </div>
        `).join('') : '<p class="text-muted" style="font-size: 0.825rem; padding: 12px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px;">No active projects in organization.</p>'}
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
  // 6. WAR ROOM — AUTONOMOUS AGENT PARALLEL EXECUTION VISUALIZER
  // --------------------------------------------------------------------------
  renderAgentsTab(state) {
    const agentIds = Object.keys(AGENTS);
    const agentStates = warRoomAgent.getAgentStates();
    const logs = state.agentSwarmLogs || [];

    this.container.innerHTML = `
      <div class="war-room">
        <!-- Header -->
        <div class="war-room-header">
          <div>
            <h3 class="war-room-title">🎖️ Nexus Agent War Room</h3>
            <p class="war-room-subtitle">4 specialist agents running in parallel · Real-time execution stream · Human-in-the-Loop consensus</p>
          </div>
          <div style="display:flex; gap:8px;">
            <button class="btn btn-gradient glow-cyan btn-xs" id="btnWarRoomAnalyse">▶ Run Full Analysis</button>
          </div>
        </div>

        <!-- 4-Agent Grid -->
        <div class="war-room-grid">
          ${agentIds.map(id => {
            const agent = AGENTS[id];
            const as = agentStates[id] || { status: 'idle', lastMessage: 'Awaiting command...', logLines: [] };
            const statusColors = { idle: '#475569', active: '#00F2FE', thinking: '#A855F7', done: '#22C55E', error: '#EF4444' };
            const color = statusColors[as.status] || '#475569';

            return `
              <div class="war-room-agent-card" id="war-agent-${id}" style="--agent-color:${agent.color};">
                <div class="war-agent-header">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div class="war-agent-avatar" style="background:${agent.color}22; border-color:${agent.color};">${agent.avatar}</div>
                    <div>
                      <div class="war-agent-name">${agent.name}</div>
                      <div class="war-agent-badge" style="color:${agent.color};">${agent.badge}</div>
                    </div>
                  </div>
                  <div class="war-agent-status" style="color:${color};">
                    ${as.status === 'thinking' || as.status === 'active' ? '<span class="war-pulse"></span>' : ''}
                    ${as.status.toUpperCase()}
                  </div>
                </div>
                <div class="war-agent-specialty">${agent.specialty}</div>
                <div class="war-agent-log" id="war-log-${id}">
                  ${as.logLines.length > 0
                    ? as.logLines.slice(-6).map(l => `<div class="war-log-line">${l.line}</div>`).join('')
                    : `<div class="war-log-line" style="color:#475569;">Awaiting command...</div>`
                  }
                </div>
                ${as.lastMessage ? `<div class="war-agent-footer" style="border-color:${agent.color}44;">${as.lastMessage}</div>` : ''}
              </div>
            `;
          }).join('')}
        </div>

        <!-- Swarm Reasoning Stream -->
        <div class="war-room-stream">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h4 style="font-size:0.85rem; color:var(--cyan-primary); font-weight:700;">⚡ Live Swarm Reasoning Stream</h4>
            <span style="font-size:0.7rem; color:var(--text-muted);">${logs.length} swarm operations</span>
          </div>
          <div class="war-stream-log" id="warStreamLog">
            ${logs.length > 0 ? logs.slice(-15).reverse().map(log => `
              <div class="war-stream-entry">
                <div style="display:flex; align-items:center; gap:6px;">
                  <span style="font-size:0.75rem; font-weight:700; color:#fff;">${log.agent}</span>
                  <span style="font-size:0.65rem; color:var(--cyan-primary);">[${log.action}]</span>
                  ${log.tool ? `<code style="font-size:0.62rem; background:rgba(0,242,254,0.1); color:var(--cyan-primary); padding:1px 3px; border-radius:2px;">tool: ${log.tool}</code>` : ''}
                </div>
                <div style="font-size:0.725rem; color:var(--text-secondary); margin-top:2px;">${log.message}</div>
                <span style="font-size:0.65rem; color:var(--text-muted);">${log.time}</span>
              </div>
            `).join('') : '<p style="font-size:0.75rem; color:var(--text-muted);">Click ▶ Run Full Analysis to launch all agents.</p>'}
          </div>
        </div>
      </div>
    `;

    // Bind run button
    const runBtn = this.container.querySelector('#btnWarRoomAnalyse');
    if (runBtn) {
      runBtn.addEventListener('click', async () => {
        runBtn.disabled = true;
        runBtn.textContent = '⏳ Agents Running...';

        // Subscribe to updates and re-render agent cards
        warRoomAgent.onUpdate((agentStates, _) => {
          Object.keys(agentStates).forEach(id => {
            const as = agentStates[id];
            const logEl = document.getElementById(`war-log-${id}`);
            if (logEl && as.logLines.length > 0) {
              logEl.innerHTML = as.logLines.slice(-6).map(l => `<div class="war-log-line">${l.line}</div>`).join('');
              logEl.scrollTop = logEl.scrollHeight;
            }
            const card = document.getElementById(`war-agent-${id}`);
            if (card) {
              const statusEl = card.querySelector('.war-agent-status');
              if (statusEl) {
                const statusColors = { idle: '#475569', active: '#00F2FE', thinking: '#A855F7', done: '#22C55E', error: '#EF4444' };
                const color = statusColors[as.status] || '#475569';
                statusEl.style.color = color;
                statusEl.innerHTML = `${as.status === 'thinking' || as.status === 'active' ? '<span class="war-pulse"></span>' : ''} ${as.status.toUpperCase()}`;
              }
              const footerEl = card.querySelector('.war-agent-footer');
              if (footerEl && as.lastMessage) footerEl.textContent = as.lastMessage;
            }
          });
        });

        await warRoomAgent.runFullAnalysis();
        store.addToast('War Room Complete', '4-agent analysis finished. Consensus reached.', 'success');
        runBtn.disabled = false;
        runBtn.textContent = '▶ Run Full Analysis';
        this.render();
      });
    }
  }

  // --------------------------------------------------------------------------
  // 6b. MONTE CARLO SIMULATION SANDBOX TAB
  // --------------------------------------------------------------------------
  renderSimulationTab(state) {
    this.container.innerHTML = '<div id="simSandboxMount" style="width:100%;"></div>';
    // Lazy-import to avoid circular deps
    import('../components/simulationSandbox.js').then(({ SimulationSandbox }) => {
      const sandbox = new SimulationSandbox('simSandboxMount');
      sandbox.render();
    });
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
  // 8. TEAM MEETINGS TAB — WITH MEETING INTELLIGENCE AGENT
  // --------------------------------------------------------------------------
  renderMeetingsTab(state) {
    const meetings = state.meetings || [];
    const upcoming = meetings.filter(m => m.status === 'scheduled');
    const actionItems = meetingIntelAgent.actionItems;
    const transcript = meetingIntelAgent.transcript;
    const isRecording = meetingIntelAgent.isRecording;

    this.container.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:16px;">
        <!-- Header -->
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <h3 style="font-size:1rem; font-weight:700; color:#fff;">🗓️ Team Video Meetings & AI Meeting Intelligence</h3>
          <button class="btn btn-primary btn-sm btn-open-meeting-modal">📅 Schedule Meeting</button>
        </div>

        <!-- Meeting Intel Panel -->
        <div class="meeting-intel-panel">
          <div class="meeting-intel-header">
            <div>
              <div style="font-size:0.9rem; font-weight:700; color:#fff;">🎙️ Meeting Intelligence Agent</div>
              <div style="font-size:0.75rem; color:var(--text-muted);">Live speech-to-text · NLP action item extraction · Auto-task insertion</div>
            </div>
            <div style="display:flex; gap:8px;">
              ${isRecording
                ? `<button class="btn btn-sm" style="background:#EF4444; color:#fff;" id="btnStopTranscription">⏹ Stop & Extract</button>`
                : `<button class="btn btn-sm" style="background:#22C55E; color:#fff;" id="btnStartTranscription">🎙 Start Live Transcription</button>
                   <button class="btn btn-ghost btn-sm" id="btnDemoTranscription">▶ Demo Mode</button>`
              }
            </div>
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px;">
            <!-- Transcript Feed -->
            <div>
              <div style="font-size:0.75rem; font-weight:700; color:var(--cyan-primary); margin-bottom:8px;">
                📝 Live Transcript ${isRecording ? '<span class="war-pulse" style="display:inline-block;"></span>' : ''}
              </div>
              <div class="meeting-transcript-feed" id="transcriptFeed">
                ${transcript.length > 0
                  ? transcript.slice(-12).map(t => `
                      <div class="transcript-line">
                        <span class="transcript-time">${t.time}</span>
                        <span class="transcript-text">${t.text}</span>
                      </div>`).join('')
                  : '<div style="font-size:0.75rem; color:#475569; padding:12px;">Transcript will appear here during the meeting...</div>'
                }
              </div>
            </div>

            <!-- Action Items -->
            <div>
              <div style="font-size:0.75rem; font-weight:700; color:#A855F7; margin-bottom:8px;">
                ✅ Extracted Action Items (${actionItems.length})
              </div>
              <div class="meeting-actions-feed" id="actionsFeed">
                ${actionItems.length > 0
                  ? actionItems.map(item => `
                      <div class="action-item-card ${item.inserted ? 'inserted' : ''}">
                        <div class="action-item-text">${item.text}</div>
                        <div class="action-item-meta">
                          ${item.assignee ? `<span class="action-assignee">👤 ${item.assignee}</span>` : '<span style="color:#475569;">👤 Unassigned</span>'}
                          <span style="color:#475569;">📅 ${item.deadline}</span>
                          <span style="color:#A855F7;">${Math.round(item.confidence * 100)}% confidence</span>
                        </div>
                        ${!item.inserted
                          ? `<button class="btn btn-xs btn-primary action-insert-btn" data-id="${item.id}">+ Add to Graph</button>`
                          : '<span style="font-size:0.7rem; color:#22C55E;">✓ Added to Live Graph</span>'
                        }
                      </div>`).join('')
                  : '<div style="font-size:0.75rem; color:#475569; padding:12px;">Action items extracted from speech will appear here...</div>'
                }
              </div>
              ${actionItems.filter(i => !i.inserted).length > 1 ? `
                <button class="btn btn-primary btn-sm" id="btnInsertAllActions" style="margin-top:8px; width:100%;">
                  + Insert All ${actionItems.filter(i => !i.inserted).length} Items to Graph
                </button>
              ` : ''}
            </div>
          </div>
        </div>

        <!-- Scheduled Meetings -->
        <div class="task-list-container">
          ${upcoming.map(m => `
            <div class="task-item-card" data-meeting-id="${m.id}" style="flex-direction:column; align-items:stretch; gap:10px;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <div class="task-title">📅 ${m.title}</div>
                  <div class="task-meta">
                    <span>${m.date} • ${m.time} (${m.duration} min)</span>
                    <span>Project: ${m.project}</span>
                  </div>
                </div>
                <span class="search-item-tag">Organizer: ${m.organizer}</span>
              </div>
              ${m.agenda ? `<p style="font-size:0.8rem; color:var(--text-secondary); line-height:1.4;">${m.agenda}</p>` : ''}
              <div style="display:flex; flex-wrap:wrap; gap:6px;">
                ${m.attendees.map(a => `<span style="font-size:0.7rem; background:rgba(255,255,255,0.06); padding:3px 9px; border-radius:10px; color:var(--text-secondary);">👤 ${a}</span>`).join('')}
              </div>
              <div style="display:flex; gap:8px; margin-top:4px;">
                <button class="btn btn-primary btn-xs btn-join-meeting" data-id="${m.id}">🎥 Join Live Video Room</button>
                <button class="btn btn-ghost btn-xs btn-cancel-meeting" data-id="${m.id}" style="color:#EF4444; border-color:#EF4444;">Cancel</button>
              </div>
            </div>
          `).join('')}
          ${upcoming.length === 0 ? '<p class="text-muted">No meetings currently scheduled.</p>' : ''}
        </div>
      </div>
    `;

    this._bindMeetingIntelEvents();
    this.attachMeetingsEvents();
  }

  _bindMeetingIntelEvents() {
    // Start transcription
    const startBtn = this.container.querySelector('#btnStartTranscription');
    if (startBtn) {
      startBtn.addEventListener('click', () => {
        if (!meetingIntelAgent.isSupported) {
          store.addToast('Not Supported', 'Web Speech API is not available in this browser. Try Chrome.', 'warning');
          return;
        }
        meetingIntelAgent.onTranscriptUpdate(() => this.renderMeetingsTab(store.getState()));
        meetingIntelAgent.onActionItemsUpdate(() => this.renderMeetingsTab(store.getState()));
        meetingIntelAgent.startTranscription('Team Meeting');
        this.renderMeetingsTab(store.getState());
        store.addToast('Transcription Started', 'Live speech-to-text is now active.', 'success');
      });
    }

    // Demo transcription
    const demoBtn = this.container.querySelector('#btnDemoTranscription');
    if (demoBtn) {
      demoBtn.addEventListener('click', () => {
        meetingIntelAgent.onTranscriptUpdate((t) => {
          const feed = document.getElementById('transcriptFeed');
          if (feed) {
            feed.innerHTML = t.slice(-12).map(entry => `
              <div class="transcript-line">
                <span class="transcript-time">${entry.time}</span>
                <span class="transcript-text">${entry.text}</span>
              </div>`).join('');
            feed.scrollTop = feed.scrollHeight;
          }
        });
        meetingIntelAgent.onActionItemsUpdate((items) => {
          const feed = document.getElementById('actionsFeed');
          if (feed) {
            feed.innerHTML = items.map(item => `
              <div class="action-item-card ${item.inserted ? 'inserted' : ''}">
                <div class="action-item-text">${item.text}</div>
                <div class="action-item-meta">
                  ${item.assignee ? `<span class="action-assignee">👤 ${item.assignee}</span>` : '<span style="color:#475569;">👤 Unassigned</span>'}
                  <span style="color:#475569;">📅 ${item.deadline}</span>
                  <span style="color:#A855F7;">${Math.round(item.confidence * 100)}% confidence</span>
                </div>
                ${!item.inserted
                  ? `<button class="btn btn-xs btn-primary action-insert-btn" data-id="${item.id}">+ Add to Graph</button>`
                  : '<span style="font-size:0.7rem; color:#22C55E;">✓ Added to Live Graph</span>'
                }
              </div>`).join('');
          }
        });
        meetingIntelAgent.simulateTranscription('Sprint Planning Demo');
        store.addToast('Demo Started', 'Simulating sprint planning meeting transcription...', 'info');
      });
    }

    // Stop transcription
    const stopBtn = this.container.querySelector('#btnStopTranscription');
    if (stopBtn) {
      stopBtn.addEventListener('click', () => {
        const summary = meetingIntelAgent.stopTranscription();
        store.addToast('Meeting Ended', `${summary.actionItems.length} action items extracted from ${summary.duration} meeting.`, 'success');
        this.renderMeetingsTab(store.getState());
      });
    }

    // Individual insert buttons
    this.container.querySelectorAll('.action-insert-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        await meetingIntelAgent.insertActionItemAsTask(id);
        this.renderMeetingsTab(store.getState());
      });
    });

    // Insert all
    const insertAllBtn = this.container.querySelector('#btnInsertAllActions');
    if (insertAllBtn) {
      insertAllBtn.addEventListener('click', async () => {
        await meetingIntelAgent.insertAllActionItems();
        this.renderMeetingsTab(store.getState());
      });
    }
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
    const externalBtn = document.getElementById('btnOpenExternalMeeting');
    const copyBtn = document.getElementById('btnCopyMeetingLink');
    const closeBtn = document.getElementById('btnCloseLiveMeeting');

    if (!modal || !container) return;

    if (window.nexusJitsiApi) {
      try { window.nexusJitsiApi.dispose(); } catch {}
      window.nexusJitsiApi = null;
    }

    container.innerHTML = '';

    // Deterministic room name identical for all participants:
    const cleanId = (meeting.id || 'room').toLowerCase().replace(/[^a-z0-9]/g, '-');
    const roomName = meeting.room_id || (meeting.link ? meeting.link.split('/').pop() : `nexusmind-${cleanId}`);
    const jitsiUrl = `https://meet.jit.si/${roomName}`;

    console.log(`[Jitsi] Connecting to room: ${roomName} (${jitsiUrl})`);

    if (title) title.textContent = `🎥 ${meeting.title}`;
    if (roomLabel) roomLabel.textContent = `${meeting.date} • ${meeting.time} | Room: ${roomName}`;
    if (externalBtn) {
      externalBtn.href = jitsiUrl;
      externalBtn.style.display = 'inline-flex';
    }
    if (copyBtn) {
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(jitsiUrl).then(() => {
          store.addToast('Link Copied', 'Jitsi video room link copied to clipboard!', 'info');
        });
      };
    }
    if (closeBtn) {
      closeBtn.onclick = () => {
        if (window.nexusJitsiApi) {
          try { window.nexusJitsiApi.dispose(); } catch {}
          window.nexusJitsiApi = null;
        }
        container.innerHTML = '';
        modal.classList.add('hidden');
      };
    }

    modal.classList.remove('hidden');

    const currentUser = store.getState().currentUser || {};
    const displayName = currentUser.name || 'Participant';
    const email = currentUser.email || '';

    if (typeof window.JitsiMeetExternalAPI === 'function') {
      try {
        window.nexusJitsiApi = new window.JitsiMeetExternalAPI('meet.jit.si', {
          roomName: roomName,
          parentNode: container,
          width: '100%',
          height: '100%',
          configOverwrite: {
            prejoinConfig: { enabled: false },
            startWithAudioMuted: false,
            startWithVideoMuted: false,
            enableWelcomePage: false,
            enableClosePage: false,
            disableDeepLinking: true
          },
          interfaceConfigOverwrite: {
            SHOW_JITSI_WATERMARK: false,
            SHOW_WATERMARK_FOR_GUESTS: false,
            TOOLBAR_BUTTONS: [
              'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
              'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
              'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
              'videoquality', 'filmstrip', 'invite', 'feedback', 'stats', 'shortcuts',
              'tileview', 'videobackgroundblur', 'download', 'help', 'mute-everyone', 'security'
            ]
          },
          userInfo: {
            displayName: displayName,
            email: email
          }
        });
      } catch (err) {
        console.warn('[Jitsi] External API initialization failed, falling back to secure iframe:', err);
        this._renderJitsiIframe(container, jitsiUrl);
      }
    } else {
      console.log('[Jitsi] External API not loaded, rendering secure WebRTC iframe');
      this._renderJitsiIframe(container, jitsiUrl);
    }
  }

  _renderJitsiIframe(container, jitsiUrl) {
    container.innerHTML = `
      <iframe
        src="${jitsiUrl}#config.prejoinConfig.enabled=false"
        allow="camera; microphone; fullscreen; display-capture; autoplay; clipboard-write; speaker"
        style="width: 100%; height: 100%; min-height: 520px; border: none; border-radius: 12px; background: #000;"
      ></iframe>
    `;
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