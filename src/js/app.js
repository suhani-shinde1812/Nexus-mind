/**
 * NEXUS MIND - APPLICATION BOOTSTRAP & MAIN ORCHESTRATOR
 */

import { store } from './state.js';
import { LiveTaskGraphEngine } from './graphEngine.js';
import { RolePortals } from './components/rolePortals.js';
import { monitoringAgent } from './agents/monitoringAgent.js';
import { assistantAgent } from './agents/assistantAgent.js';
import { searchAgent } from './agents/searchAgent.js';

class NexusApp {
  constructor() {
    this.graphEngine = null;
    this.rolePortals = null;
  }

  init() {
    this.rolePortals = new RolePortals('portalTabContent');
    this.graphEngine = new LiveTaskGraphEngine('graphSvg', 'graphTooltip', 'nodeDetailDrawer');

    this.rolePortals.render();
    this.graphEngine.render();
    this.graphEngine.startPhysicsLoop();

    this.bindThemeToggler();
    this.bindRoleSelector();
    this.bindTabNavigation();
    this.bindSearchEngine();
    this.bindAiPromptLauncher();
    this.bindTaskModal();
    this.bindGraphControls();
    this.bindAiRiskScan();
    this.bindNotificationsDrawer();
    this.bindAutoRebalancer();
    this.bindDocumentViewerModal();

    store.subscribe(() => {
      this.rolePortals.render();
      this.graphEngine.render();
      this.updateNavbarUser();
      this.updateUnreadCount();
      this.syncThemeUI();
    });

    this.updateNavbarUser();
    this.updateUnreadCount();
    this.syncThemeUI();
    console.log('🚀 Nexus Mind Platform Initialized successfully!');
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
          if (task) this.graphEngine.showNodeDrawer(task);
        } else if (type === 'Policy') {
          const policy = store.getState().policies.find(p => p.title === id);
          if (policy) this.openDocModal(policy);
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
        <div class="msg-bubble"><em>🤖 Nexus AI analyzing...</em></div>
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

    if (openBtn) {
      openBtn.addEventListener('click', () => {
        populateDependencies();
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

        store.addTask({ title, assignee, priority, project, dependsOn });
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
        <div style="background:rgba(0,0,0,0.04); border:1px solid var(--border-color); padding:14px; border-radius:10px; font-size:0.875rem;">
          ${policy.summary}
        </div>
      `;
      modal.classList.remove('hidden');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new NexusApp();
  app.init();
});
