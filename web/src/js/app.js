/**
 * NEXUS MIND - APPLICATION BOOTSTRAP & MAIN ORCHESTRATOR
 * Orchestrates Multi-View Matrix (Graph, Kanban, Gantt), Autonomous AI Swarm,
 * Role Portals, and Real-Time Collaboration.
 */
import { store } from './state.js';
import { api } from './api.js';
import { LiveTaskGraphEngine } from './graphEngine.js';
import { KanbanEngine } from './components/kanbanEngine.js';
import { GanttEngine } from './components/ganttEngine.js';
import { RolePortals } from './components/rolePortals.js';
import { monitoringAgent } from './agents/monitoringAgent.js';
import { assistantAgent } from './agents/assistantAgent.js';
import { searchAgent } from './agents/searchAgent.js';
import { mountLoginScreen } from './components/loginScreen.js';

class NexusApp {
  constructor() {
    this.graphEngine = null;
    this.kanbanEngine = null;
    this.ganttEngine = null;
    this.rolePortals = null;
  }

  init() {
    this.rolePortals = new RolePortals('portalTabContent');
    this.graphEngine = new LiveTaskGraphEngine('graphSvg', 'graphTooltip', 'nodeDetailDrawer');
    this.kanbanEngine = new KanbanEngine('kanbanContainer');
    this.ganttEngine = new GanttEngine('ganttContainer');

    this.rolePortals.render();
    this.renderCurrentView();
    this.graphEngine.startPhysicsLoop();

    this.bindThemeToggler();
    this.bindRoleSelector();
    this.bindTabNavigation();
    this.bindViewSwitcher();
    this.bindSearchEngine();
    this.bindAiPromptLauncher();
    this.bindTaskModal();
    this.bindGraphControls();
    this.bindAiRiskScan();
    this.bindNotificationsDrawer();
    this.bindAutoRebalancer();
    this.bindDocumentViewerModal();
    this.bindMeetingModal();
    this.bindFooterAgentPills();
    this.bindLogoutButton();

    store.subscribe(() => {
      this.rolePortals.render();
      this.renderCurrentView();
      this.updateNavbarUser();
      this.updateUnreadCount();
      this.renderToasts();
      this.syncThemeUI();
    });

    this.updateNavbarUser();
    this.updateUnreadCount();
    this.renderToasts();
    this.syncThemeUI();
    console.log('🚀 Nexus Mind Autonomous Platform Online!');
  }

  // --- Multi-View Matrix Rendering ---
  bindViewSwitcher() {
    const viewBtns = document.querySelectorAll('.view-tab-btn');
    viewBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = e.currentTarget.getAttribute('data-view');
        store.setView(view);
      });
    });
  }

  renderCurrentView() {
    const state = store.getState();
    const view = state.currentView || 'graph';

    const graphContainer = document.getElementById('graphCanvasContainer');
    const kanbanContainer = document.getElementById('kanbanContainer');
    const ganttContainer = document.getElementById('ganttContainer');
    const graphToolbar = document.getElementById('graphSpecificToolbar');
    const viewSubtitle = document.getElementById('viewSubtitle');

    // Update switcher active tab
    document.querySelectorAll('.view-tab-btn').forEach(btn => {
      if (btn.getAttribute('data-view') === view) btn.classList.add('active');
      else btn.classList.remove('active');
    });

    if (view === 'graph') {
      if (graphContainer) graphContainer.classList.remove('hidden');
      if (kanbanContainer) kanbanContainer.classList.add('hidden');
      if (ganttContainer) ganttContainer.classList.add('hidden');
      if (graphToolbar) graphToolbar.classList.remove('hidden');
      if (viewSubtitle) viewSubtitle.textContent = 'Single Source of Truth • Drag node port to link dependencies';
      this.graphEngine.render();
    } else if (view === 'kanban') {
      if (graphContainer) graphContainer.classList.add('hidden');
      if (kanbanContainer) kanbanContainer.classList.remove('hidden');
      if (ganttContainer) ganttContainer.classList.add('hidden');
      if (graphToolbar) graphToolbar.classList.add('hidden');
      if (viewSubtitle) viewSubtitle.textContent = 'Interactive Drag & Drop Board • Backlog to Completed';
      this.kanbanEngine.render();
    } else if (view === 'timeline') {
      if (graphContainer) graphContainer.classList.add('hidden');
      if (kanbanContainer) kanbanContainer.classList.add('hidden');
      if (ganttContainer) ganttContainer.classList.remove('hidden');
      if (graphToolbar) graphToolbar.classList.add('hidden');
      if (viewSubtitle) viewSubtitle.textContent = 'Critical Path Schedule & Milestone Durations';
      this.ganttEngine.render();
    }
  }

  // --- Toasts Rendering ---
  renderToasts() {
    const container = document.getElementById('nexusToastContainer');
    if (!container) return;

    const state = store.getState();
    container.innerHTML = state.toasts.map(t => `
      <div class="toast-item ${t.type}">
        <div style="font-weight:700; font-size:0.8rem; display:flex; justify-content:space-between; align-items:center;">
          <span>${t.type === 'success' ? '✅' : (t.type === 'warning' ? '⚠️' : '💡')} ${t.title}</span>
          <button class="btn-toast-close" data-id="${t.id}">&times;</button>
        </div>
        <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:3px;">${t.message}</div>
      </div>
    `).join('');

    container.querySelectorAll('.btn-toast-close').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        store.removeToast(id);
      });
    });
  }

  // --- Footer Agent Pills Shortcuts ---
  bindFooterAgentPills() {
    document.getElementById('agentMonitoringPill')?.addEventListener('click', () => {
      document.getElementById('btnRunAiScan')?.click();
    });

    document.getElementById('agentAssistantPill')?.addEventListener('click', () => {
      const chatModal = document.getElementById('aiChatModal');
      if (chatModal) chatModal.classList.remove('hidden');
      document.getElementById('chatInput')?.focus();
    });

    document.getElementById('agentSearchPill')?.addEventListener('click', () => {
      const searchInput = document.getElementById('globalSearchInput');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    });
  }

  // --- Theme Toggle Switch ---
  bindThemeToggler() {
    const btn = document.getElementById('btnToggleTheme');
    if (!btn) return;

    btn.addEventListener('click', () => {
      const newTheme = store.toggleTheme();
      this.syncThemeUI();
    });
  }

  syncThemeUI() {
    const state = store.getState();
    const theme = state.theme || 'dark';
    document.body.className = `theme-${theme}`;

    const icon = document.getElementById('themeToggleIcon');
    const text = document.getElementById('themeToggleText');
    if (icon && text) {
      icon.textContent = theme === 'dark' ? '🌙' : '☀️';
      text.textContent = theme === 'dark' ? 'Dark' : 'Light';
    }
  }

  updateNavbarUser() {
    const state = store.getState();
    const user = state.currentUser;
    if (!user) return;

    const navName = document.getElementById('navUserName');
    const navRole = document.getElementById('navUserRole');
    const navAvatar = document.getElementById('navUserAvatar');
    const portalTitle = document.getElementById('portalTitle');

    if (navName) navName.textContent = user.name;
    if (navRole) navRole.textContent = user.role;
    if (navAvatar) navAvatar.textContent = user.avatar;

    const titleMap = {
      employee: '👨‍💻 Employee Workspace Portal',
      team_lead: '👩‍💼 Team Lead Management Portal',
      project_manager: '📊 Project Manager Sprint Portal',
      admin: '🛡️ Administrator Organization Portal'
    };
    if (portalTitle) portalTitle.textContent = titleMap[state.currentRole] || 'Workspace Portal';
  }

  updateUnreadCount() {
    const state = store.getState();
    const badge = document.getElementById('unreadCount');
    if (badge) {
      badge.textContent = state.aiAlerts.length;
    }
  }

  bindRoleSelector() {
    const roleSelect = document.getElementById('roleSelect');
    if (!roleSelect) return;

    roleSelect.value = store.getState().currentRole;
    roleSelect.addEventListener('change', (e) => {
      store.setRole(e.target.value);
    });
  }

  bindTabNavigation() {
    const tabs = document.querySelectorAll('.portal-tabs .tab-btn');
    tabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        tabs.forEach(t => t.classList.remove('active'));
        const targetBtn = e.currentTarget;
        targetBtn.classList.add('active');
        const tabName = targetBtn.getAttribute('data-tab');
        this.rolePortals.setTab(tabName);
      });
    });
  }

  bindSearchEngine() {
    const searchInput = document.getElementById('globalSearchInput');
    const dropdown = document.getElementById('searchResultsDropdown');

    if (!searchInput || !dropdown) return;

    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });

    searchInput.addEventListener('input', (e) => {
      const query = e.target.value;
      if (!query.trim()) {
        dropdown.classList.add('hidden');
        return;
      }

      const results = searchAgent.search(query);
      if (results.length === 0) {
        dropdown.innerHTML = '<div style="padding:10px; font-size:0.8rem; color:var(--text-muted);">No matching items found.</div>';
      } else {
        dropdown.innerHTML = results.map(res => `
          <div class="search-item" data-id="${res.id}" data-type="${res.type}">
            <div>
              <div class="search-item-title">${res.title}</div>
              <div style="font-size:0.725rem; color:var(--text-secondary);">${res.subtitle}</div>
            </div>
            <span class="search-item-tag">${res.badge}</span>
          </div>
        `).join('');
      }

      dropdown.classList.remove('hidden');
    });

    dropdown.addEventListener('click', (e) => {
      const item = e.target.closest('.search-item');
      if (item) {
        const id = item.getAttribute('data-id');
        const type = item.getAttribute('data-type');
        dropdown.classList.add('hidden');

        if (type === 'Task') {
          const task = store.getState().tasks.find(t => t.id === id);
          if (task) {
            store.setView('graph');
            this.graphEngine.showNodeDrawer(task);
          }
        } else if (type === 'Policy') {
          const policy = store.getState().policies.find(p => p.title === id);
          if (policy) this.openDocModal(policy);
        } else if (type === 'Meeting') {
          const tabs = document.querySelectorAll('.portal-tabs .tab-btn');
          tabs.forEach(t => t.classList.remove('active'));
          const meetingsTabBtn = document.querySelector('.portal-tabs .tab-btn[data-tab="meetings"]');
          if (meetingsTabBtn) meetingsTabBtn.classList.add('active');
          this.rolePortals.setTab('meetings');
        }
      }
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });
  }

  bindAiPromptLauncher() {
    const promptForm = document.getElementById('aiPromptForm');
    const promptInput = document.getElementById('aiPromptInput');
    const chatModal = document.getElementById('aiChatModal');
    const chatMessages = document.getElementById('chatMessages');
    const closeChatModal = document.getElementById('btnCloseChatModal');
    const chatInput = document.getElementById('chatInput');
    const btnSendChat = document.getElementById('btnSendChat');

    const handlePromptSubmit = async (userText) => {
      if (!userText.trim()) return;

      if (!chatMessages) return;

      const userDiv = document.createElement('div');
      userDiv.className = 'chat-message user';
      userDiv.innerHTML = `<div class="msg-bubble">${userText}</div>`;
      chatMessages.appendChild(userDiv);

      const assistantDiv = document.createElement('div');
      assistantDiv.className = 'chat-message assistant';
      assistantDiv.innerHTML = `
        <div class="msg-avatar">💡</div>
        <div class="msg-bubble"><em>🤖 Nexus AI thinking...</em></div>
      `;
      chatMessages.appendChild(assistantDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      if (chatModal) chatModal.classList.remove('hidden');

      try {
        const response = await assistantAgent.processPromptAsync(userText);
        const bubble = assistantDiv.querySelector('.msg-bubble');
        if (bubble && response && response.message) {
          bubble.innerHTML = response.message.replace(/\n/g, '<br/>');
        }
      } catch (err) {
        const bubble = assistantDiv.querySelector('.msg-bubble');
        if (bubble) {
          const fallback = assistantAgent.processSmartRuleEngine(userText);
          bubble.innerHTML = fallback.message.replace(/\n/g, '<br/>');
        }
      }

      chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    if (promptForm && promptInput) {
      promptForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = promptInput.value;
        promptInput.value = '';
        handlePromptSubmit(text);
      });
    }

    if (btnSendChat && chatInput) {
      btnSendChat.addEventListener('click', () => {
        const text = chatInput.value;
        chatInput.value = '';
        handlePromptSubmit(text);
      });

      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const text = chatInput.value;
          chatInput.value = '';
          handlePromptSubmit(text);
        }
      });
    }

    if (closeChatModal && chatModal) {
      closeChatModal.addEventListener('click', () => {
        chatModal.classList.add('hidden');
      });
    }
  }

  bindTaskModal() {
    const modal = document.getElementById('taskModal');
    const openBtn = document.getElementById('btnCreateTaskModal');
    const closeBtn = document.getElementById('btnCloseTaskModal');
    const cancelBtn = document.getElementById('btnCancelTaskModal');
    const taskForm = document.getElementById('taskForm');
    const depSelect = document.getElementById('taskDependencySelect');
    const btnAiDecompose = document.getElementById('btnGenerateAiSubtasks');
    const subtaskPreview = document.getElementById('aiSubtasksPreview');

    if (!modal) return;

    const populateDependencies = () => {
      if (!depSelect) return;
      const tasks = store.getState().tasks;
      depSelect.innerHTML = '<option value="">None (Standalone)</option>' +
        tasks.map(t => `<option value="${t.id}">[${t.id}] ${t.title}</option>`).join('');
    };

    const deadlineInput = document.getElementById('taskDeadlineInput');

    if (openBtn) {
      openBtn.addEventListener('click', () => {
        populateDependencies();
        if (deadlineInput) {
          const today = new Date().toISOString().split('T')[0];
          deadlineInput.min = today;
          if (!deadlineInput.value) deadlineInput.value = today;
        }
        modal.classList.remove('hidden');
      });
    }

    const closeModal = () => modal.classList.add('hidden');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    if (btnAiDecompose) {
      btnAiDecompose.addEventListener('click', () => {
        const title = document.getElementById('taskTitleInput').value || 'New Component';
        const res = assistantAgent.generateSubtasks(title);
        subtaskPreview.innerHTML = res.subtasks.map(s => `<div style="margin-top:4px;">${s}</div>`).join('');
      });
    }

    if (taskForm) {
      taskForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = document.getElementById('taskTitleInput').value;
        const assignee = document.getElementById('taskAssigneeSelect').value;
        const priority = document.getElementById('taskPrioritySelect').value;
        const project = document.getElementById('taskProjectSelect').value;
        const dependsOn = document.getElementById('taskDependencySelect').value;
        const dueDate = document.getElementById('taskDeadlineInput').value;
        const description = document.getElementById('taskDescInput')?.value || '';

        store.addTask({ title, assignee, priority, project, dependsOn, dueDate, description });
        closeModal();
        taskForm.reset();
      });
    }
  }

  bindGraphControls() {
    const filterBtns = document.querySelectorAll('.graph-filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        filterBtns.forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        const filter = e.currentTarget.getAttribute('data-filter');
        this.graphEngine.setFilter(filter);
      });
    });

    document.getElementById('btnGraphReset')?.addEventListener('click', () => this.graphEngine.resetView());
    document.getElementById('btnGraphZoomIn')?.addEventListener('click', () => this.graphEngine.zoomIn());
    document.getElementById('btnGraphZoomOut')?.addEventListener('click', () => this.graphEngine.zoomOut());
    
    const physicsBtn = document.getElementById('btnTogglePhysics');
    if (physicsBtn) {
      physicsBtn.addEventListener('click', () => {
        const state = this.graphEngine.togglePhysics();
        physicsBtn.querySelector('span').textContent = `Physics: ${state ? 'ON' : 'OFF'}`;
      });
    }

    document.getElementById('btnCloseNodeDrawer')?.addEventListener('click', () => {
      document.getElementById('nodeDetailDrawer')?.classList.add('hidden');
    });
  }

  bindAiRiskScan() {
    const scanBtn = document.getElementById('btnRunAiScan');
    const banner = document.getElementById('aiAlertsBanner');
    const bannerText = document.getElementById('alertText');
    const closeAlert = document.getElementById('btnCloseAlert');

    if (scanBtn) {
      scanBtn.addEventListener('click', () => {
        scanBtn.disabled = true;
        scanBtn.innerHTML = '<span>Scanning Graph...</span>';

        setTimeout(() => {
          const report = monitoringAgent.generateProactiveAlerts();
          scanBtn.disabled = false;
          scanBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            <span>Run AI Risk Scan</span>
          `;

          if (banner && bannerText) {
            bannerText.textContent = report.summary;
            banner.classList.remove('hidden');
          }
        }, 600);
      });
    }

    if (closeAlert && banner) {
      closeAlert.addEventListener('click', () => banner.classList.add('hidden'));
    }

    document.getElementById('btnViewRiskDetails')?.addEventListener('click', () => {
      store.setView('graph');
      this.graphEngine.setFilter('risk');
    });
  }

  bindNotificationsDrawer() {
    const bellBtn = document.getElementById('btnNotifications');
    const drawer = document.getElementById('notificationsDrawer');
    const closeBtn = document.getElementById('btnCloseNotifications');
    const list = document.getElementById('notificationsList');

    if (!bellBtn || !drawer) return;

    bellBtn.addEventListener('click', () => {
      const state = store.getState();
      if (list) {
        list.innerHTML = state.aiAlerts.map(alt => `
          <div class="notification-card ${alt.severity}">
            <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.825rem;">
              <span>${alt.severity === 'critical' ? '🔴' : '⚠️'} ${alt.title}</span>
              <span style="font-size:0.65rem; color:var(--text-muted);">${alt.timestamp}</span>
            </div>
            <p style="font-size:0.775rem; color:var(--text-secondary); margin-top:4px; line-height:1.4;">${alt.message}</p>
          </div>
        `).join('');
      }

      drawer.classList.toggle('hidden');
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', () => drawer.classList.add('hidden'));
    }
  }

  bindAutoRebalancer() {
    const navBtn = document.getElementById('btnAutoRebalanceNav');
    if (navBtn) {
      navBtn.addEventListener('click', () => {
        const success = store.autoRebalanceWorkload();
        if (success) {
          navBtn.style.background = 'rgba(16, 185, 129, 0.2)';
          navBtn.style.color = '#10B981';
          navBtn.innerHTML = '✓ Rebalanced!';
          setTimeout(() => {
            navBtn.style.background = '';
            navBtn.style.color = '';
            navBtn.innerHTML = '⚡ AI Rebalance';
          }, 3000);
        }
      });
    }
  }

  bindDocumentViewerModal() {
    const modal = document.getElementById('docViewerModal');
    const closeBtn = document.getElementById('btnCloseDocModal');
    if (closeBtn && modal) {
      closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    }
  }

  bindMeetingModal() {
    const modal = document.getElementById('meetingModal');
    const closeBtn = document.getElementById('btnCloseMeetingModal');
    const cancelBtn = document.getElementById('btnCancelMeetingModal');
    const form = document.getElementById('meetingForm');
    const attendeesList = document.getElementById('meetingAttendeesList');
    const dateInput = document.getElementById('meetingDateInput');

    if (!modal) return;

    const populateAttendees = () => {
      if (!attendeesList) return;
      const state = store.getState();
      attendeesList.innerHTML = state.users
        .filter(u => u.role !== 'Administrator' || state.currentRole === 'admin')
        .map(u => `
          <label style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color: var(--text-primary); padding: 4px 0; cursor: pointer;">
            <input type="checkbox" class="meeting-attendee-checkbox" value="${u.name}" ${u.name === state.currentUser.name ? 'checked' : ''} />
            ${u.name} <span style="color: var(--text-muted);">(${u.role})</span>
          </label>
        `).join('');
    };

    const openModal = () => {
      populateAttendees();
      if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
        if (!dateInput.value) dateInput.value = today;
      }
      modal.classList.remove('hidden');
    };

    const closeModal = () => modal.classList.add('hidden');

    document.addEventListener('click', (e) => {
      if (e.target.closest('.btn-open-meeting-modal')) {
        openModal();
      }
    });

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();

        const title = document.getElementById('meetingTitleInput').value;
        const project = document.getElementById('meetingProjectSelect').value;
        const duration = document.getElementById('meetingDurationSelect').value;
        const date = document.getElementById('meetingDateInput').value;
        const time = document.getElementById('meetingTimeInput').value;
        const agenda = document.getElementById('meetingAgendaInput').value;
        const attendees = Array.from(attendeesList.querySelectorAll('.meeting-attendee-checkbox'))
          .filter(cb => cb.checked)
          .map(cb => cb.value);

        store.addMeeting({ title, project, duration, date, time, agenda, attendees });
        closeModal();
        form.reset();
      });
    }
  }

  bindLogoutButton() {
    const btn = document.getElementById('btnLogoutNav');
    if (!btn) return;

    btn.addEventListener('click', () => {
      store.logout();
      document.getElementById('app')?.classList.add('hidden');
      mountLoginScreen(async () => {
        await store.init();
        document.getElementById('app')?.classList.remove('hidden');
      });
    });
  }

  openDocModal(policy) {
    const modal = document.getElementById('docViewerModal');
    const title = document.getElementById('docModalTitle');
    const body = document.getElementById('docModalBody');

    if (modal && title && body) {
      title.textContent = `📄 ${policy.title}`;
      body.innerHTML = `
        <div style="display:flex; gap:8px; margin-bottom:12px;">
          <span class="search-item-tag">${policy.category}</span>
          ${policy.tags.map(t => `<span style="font-size:0.7rem; background:rgba(0,0,0,0.06); padding:2px 8px; border-radius:10px; color:var(--text-secondary);">#${t}</span>`).join('')}
        </div>
        <div style="background:rgba(0,0,0,0.2); border:1px solid var(--border-color); padding:14px; border-radius:10px; font-size:0.875rem; color:#F1F5F9; line-height:1.6;">
          ${policy.summary}
        </div>
      `;
      modal.classList.remove('hidden');
    }
  }
}

async function boot() {
  if (!api.isAuthenticated) {
    mountLoginScreen(async () => {
      await store.init();
      startApp();
    });
    return;
  }
  try {
    await store.init();
    startApp();
  } catch (err) {
    console.error('Session init fallback', err);
    mountLoginScreen(async () => {
      await store.init();
      startApp();
    });
  }
}

function startApp() {
  document.getElementById('nexusLoginOverlay')?.remove();
  document.getElementById('app')?.classList.remove('hidden');
  const app = new NexusApp();
  app.init();
}

document.addEventListener('DOMContentLoaded', boot);
