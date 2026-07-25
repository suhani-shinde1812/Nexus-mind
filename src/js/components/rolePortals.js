/**
 * ROLE PORTALS COMPONENT
 * Renders tailored views for 4 User Roles: Employee, Team Lead, Project Manager, Administrator
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

    this.container.innerHTML = `
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">MY ACTIVE TASKS</span>
          <span class="stat-card-value">${userTasks.filter(t => t.status !== 'done').length}</span>
          <span class="stat-card-trend up">⚡ High Priority Focus</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">COMPLETED THIS SPRINT</span>
          <span class="stat-card-value">${userTasks.filter(t => t.status === 'done').length}</span>
          <span class="stat-card-trend up">↑ +2 this week</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">PERSONAL AI ASSIST</span>
          <span class="stat-card-value">Active</span>
          <span class="stat-card-trend">💡 Real-time suggestion ready</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">📌 My Tasks & Work Queue</h3>
        <div class="task-list-container">
          ${userTasks.length > 0 ? userTasks.map(task => `
            <div class="task-item-card" data-task-id="${task.id}">
              <div class="task-item-main">
                <span class="task-status-pill ${task.status}">${task.status.replace('_', ' ')}</span>
                <div>
                  <div class="task-title">[${task.id}] ${task.title}</div>
                  <div class="task-meta">
                    <span>Project: ${task.project}</span>
                    <span>Due: ${task.dueDate}</span>
                  </div>
                </div>
              </div>
              <button class="btn btn-ghost btn-xs btn-complete-task" data-id="${task.id}">
                ${task.status === 'done' ? 'Completed ✓' : 'Mark Done'}
              </button>
            </div>
          `).join('') : '<p class="text-muted">No assigned tasks found.</p>'}
        </div>
      </div>

      <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
        <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--cyan-primary); margin-bottom: 8px;">📤 Upload Work & Daily Progress Log</h4>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
          <input type="text" id="dailyLogInput" placeholder="Log today's progress or PR link (e.g. Completed OAuth2 token refresh logic)..." style="flex:1; background: rgba(0,0,0,0.3); border: 1px solid var(--border-color); border-radius: 6px; padding: 8px; color: #fff; font-size: 0.8rem;" />
          <button id="btnSubmitDailyLog" class="btn btn-primary btn-sm">Submit Log</button>
        </div>
        <div id="logSuccessMsg" style="font-size: 0.75rem; color: var(--status-done); display: none;">✓ Progress logged to Live Task Graph timeline!</div>
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

    const submitBtn = this.container.querySelector('#btnSubmitDailyLog');
    if (submitBtn) {
      submitBtn.addEventListener('click', () => {
        const msg = this.container.querySelector('#logSuccessMsg');
        if (msg) {
          msg.style.display = 'block';
          setTimeout(() => msg.style.display = 'none', 3000);
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
    const highRiskCount = tasks.filter(t => t.aiRiskScore >= 0.7).length;

    this.container.innerHTML = `
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">ACTIVE SPRINT TASKS</span>
          <span class="stat-card-value">${tasks.length}</span>
          <span class="stat-card-trend up">65% Overall Completion</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">BLOCKED BOTTLENECKS</span>
          <span class="stat-card-value" style="color: var(--status-blocked);">${blockedCount}</span>
          <span class="stat-card-trend warn">⚠️ Requires Lead Approval</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">AI HIGH RISK HALOS</span>
          <span class="stat-card-value" style="color: var(--status-risk);">${highRiskCount}</span>
          <span class="stat-card-trend warn">🔴 Pulsing on Live Graph</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">👥 Team Member Capacity & Workload Balance</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px;">
          ${state.users.map(u => `
            <div style="background: var(--bg-card); border: 1px solid ${u.capacity > 100 ? '#EF4444' : 'var(--border-color)'}; border-radius: 8px; padding: 10px;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600;">
                <span>${u.name} (${u.role})</span>
                <span style="color: ${u.capacity > 100 ? '#EF4444' : 'var(--cyan-primary)'};">${u.capacity}% Load</span>
              </div>
              <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; margin-top: 6px; overflow: hidden;">
                <div style="width: ${Math.min(100, u.capacity)}%; height: 100%; background: ${u.capacity > 100 ? '#EF4444' : 'var(--cyan-primary)'};"></div>
              </div>
              <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px;">Assigned Tasks: ${u.activeTasks}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <div>
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">📋 Approvals & Review Queue</h3>
        ${tasks.filter(t => t.status === 'blocked' || t.priority === 'Critical').map(task => `
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
            <button class="btn btn-primary btn-xs btn-unblock-task" data-id="${task.id}">Unblock & Reassign</button>
          </div>
        `).join('')}
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
  }

  // --------------------------------------------------------------------------
  // 3. PROJECT MANAGER PORTAL
  // --------------------------------------------------------------------------
  renderProjectManagerPortal(state) {
    this.container.innerHTML = `
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">PROJECT HEALTH INDEX</span>
          <span class="stat-card-value" style="color: var(--cyan-primary);">82%</span>
          <span class="stat-card-trend up">↑ +4% from last sprint</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">PREDICTED SLA DELAY</span>
          <span class="stat-card-value">2 Days</span>
          <span class="stat-card-trend warn">⚠️ Risk on Sprint Alpha</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">ACTIVE PROJECTS</span>
          <span class="stat-card-value">${state.projects.length}</span>
          <span class="stat-card-trend up">Cloud, Mobile, Security</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">🚀 Sprint Planning & Project Progress</h3>
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
        <h4 style="font-size: 0.85rem; font-weight: 700; color: #fff; margin-bottom: 6px;">🧠 AI Insights & Delivery Forecast</h4>
        <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">
          The AI Monitoring Agent predicts a 88% likelihood of completing Sprint Alpha ahead of schedule if <strong>TASK-102 (Database Migration)</strong> is unblocked by reassigning secondary subtasks from Devon Reed to Priya Sharma.
        </p>
      </div>
    `;
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
          <span class="stat-card-trend up">⚡ Sub-second response</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">SYSTEM MEMORY LOAD</span>
          <span class="stat-card-value">${stats.memoryUsage}</span>
          <span class="stat-card-trend">CPU Load: ${stats.cpuLoad}</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">🛡️ User & Role Permissions Matrix</h3>
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
  // AGENTS TAB & ANALYTICS TAB
  // --------------------------------------------------------------------------
  renderAgentsTab(state) {
    const report = monitoringAgent.analyzeGraphRisks();

    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <!-- Agent 1 Card -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-highlight); border-radius: 12px; padding: 16px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 1.5rem;">🤖</span>
              <div>
                <h3 style="font-size: 1rem; color: #fff;">1. AI Monitoring Agent</h3>
                <p style="font-size: 0.75rem; color: var(--text-secondary);">Deadline Tracking • Risk Detection • Anomaly Alerts</p>
              </div>
            </div>
            <span class="task-status-pill done">Active</span>
          </div>
          <p style="font-size: 0.825rem; color: var(--text-primary); margin-bottom: 10px;">${report.summary}</p>
          <div style="font-size: 0.75rem; color: var(--cyan-primary);">System Health Score: <strong>${report.systemHealthIndex}%</strong></div>
        </div>

        <!-- Agent 2 Card -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-highlight); border-radius: 12px; padding: 16px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 1.5rem;">💡</span>
              <div>
                <h3 style="font-size: 1rem; color: #fff;">2. AI Assistant Agent</h3>
                <p style="font-size: 0.75rem; color: var(--text-secondary);">Smart Suggestions • Auto Responses • Task Breakdown</p>
              </div>
            </div>
            <span class="task-status-pill done">Ready</span>
          </div>
          <p style="font-size: 0.825rem; color: var(--text-primary);">Ready to process natural language inputs from the prompt bar below or chat modal.</p>
        </div>

        <!-- Agent 3 Card -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-highlight); border-radius: 12px; padding: 16px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 1.5rem;">🔍</span>
              <div>
                <h3 style="font-size: 1rem; color: #fff;">3. AI Search Agent</h3>
                <p style="font-size: 0.75rem; color: var(--text-secondary);">Search Engine • Knowledge Base • Policy Index</p>
              </div>
            </div>
            <span class="task-status-pill done">Indexed</span>
          </div>
          <p style="font-size: 0.825rem; color: var(--text-primary);">Indexed ${state.tasks.length} tasks, ${state.policies.length} policies, and ${state.users.length} user skills.</p>
        </div>
      </div>
    `;
  }

  renderAnalyticsTab(state) {
    this.container.innerHTML = `
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px;">
        <h3 style="font-size: 1rem; color: #fff; margin-bottom: 16px;">📊 Live Sprint Analytics & Risk Matrix</h3>
        <canvas id="sprintAnalyticsChart" style="max-height: 260px; width: 100%;"></canvas>
      </div>
    `;

    setTimeout(() => {
      const canvas = document.getElementById('sprintAnalyticsChart');
      if (canvas && window.Chart) {
        new window.Chart(canvas, {
          type: 'bar',
          data: {
            labels: ['Done', 'In Progress', 'Blocked', 'High Risk'],
            datasets: [{
              label: 'Task Count',
              data: [
                state.tasks.filter(t => t.status === 'done').length,
                state.tasks.filter(t => t.status === 'in_progress').length,
                state.tasks.filter(t => t.status === 'blocked').length,
                state.tasks.filter(t => t.aiRiskScore >= 0.7).length
              ],
              backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
          }
        });
      }
    }, 100);
  }
}
