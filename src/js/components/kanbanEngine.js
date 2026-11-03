/**
 * NEXUS MIND - INTERACTIVE KANBAN BOARD ENGINE
 * Drag-and-Drop task management across Backlog, In Progress, Under Review, Blocked, and Completed columns.
 */
import { store } from '../state.js';

export class KanbanEngine {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.columns = [
      { id: 'backlog', title: '📋 Backlog', color: '#64748B' },
      { id: 'in_progress', title: '⚡ In Progress', color: '#3B82F6' },
      { id: 'review', title: '🔍 Under Review', color: '#8B5CF6' },
      { id: 'blocked', title: '🚫 Blocked Bottlenecks', color: '#EF4444' },
      { id: 'done', title: '✅ Completed', color: '#10B981' }
    ];
    this.draggedTaskId = null;
  }

  render() {
    if (!this.container) return;

    const state = store.getState();
    const tasks = state.tasks;

    this.container.innerHTML = `
      <div class="kanban-board-wrapper">
        <div class="kanban-board-header">
          <div class="kanban-stats">
            <span class="badge-pill">Total: ${tasks.length}</span>
            <span class="badge-pill in-progress">Active: ${tasks.filter(t => t.status === 'in_progress').length}</span>
            <span class="badge-pill blocked">Blocked: ${tasks.filter(t => t.status === 'blocked').length}</span>
            <span class="badge-pill done">Done: ${tasks.filter(t => t.status === 'done').length}</span>
          </div>
          <div class="kanban-actions">
            <button class="btn btn-ghost btn-xs" id="btnKanbanAutoRebalance">⚡ AI Workload Rebalance</button>
            <button class="btn btn-primary btn-xs" id="btnKanbanNewTask">+ Add Task</button>
          </div>
        </div>

        <div class="kanban-columns-grid">
          ${this.columns.map(col => {
            const colTasks = this._getTasksForColumn(tasks, col.id);
            return `
              <div class="kanban-column" data-col-id="${col.id}">
                <div class="kanban-col-header" style="border-top-color: ${col.color};">
                  <div class="kanban-col-title">
                    <span>${col.title}</span>
                    <span class="col-count">${colTasks.length}</span>
                  </div>
                </div>

                <div class="kanban-card-dropzone" data-col-id="${col.id}">
                  ${colTasks.map(task => this._renderTaskCard(task, state)).join('')}
                  ${colTasks.length === 0 ? '<div class="kanban-empty-drop">Drop tasks here</div>' : ''}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;

    this._attachDragDropEvents();
    this._attachButtonEvents();
  }

  _getTasksForColumn(tasks, colId) {
    if (colId === 'backlog') {
      return tasks.filter(t => t.status === 'backlog' || (!t.status && t.status !== 'done'));
    }
    if (colId === 'review') {
      return tasks.filter(t => t.status === 'review' || t.status === 'under_review');
    }
    return tasks.filter(t => t.status === colId);
  }

  _renderTaskCard(task, state) {
    const isHighRisk = task.aiRiskScore >= 0.7;
    const isCritical = task.priority === 'Critical';
    const hasDeps = task.dependsOn && task.dependsOn.length > 0;
    const assignee = state.users.find(u => u.name === task.assignee);
    const avatar = assignee ? assignee.avatar : (task.assignee ? task.assignee.substring(0, 2).toUpperCase() : 'NA');

    return `
      <div class="kanban-task-card ${isHighRisk ? 'risk-halo' : ''} ${isCritical ? 'critical-border' : ''}" 
           draggable="true" 
           data-task-id="${task.id}">
        <div class="kanban-card-top">
          <span class="task-badge-id">${task.id}</span>
          <span class="priority-pill ${task.priority.toLowerCase()}">${task.priority}</span>
        </div>

        <div class="kanban-card-title">${task.title}</div>
        
        <div class="kanban-card-project">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
          <span>${task.project || 'General'}</span>
        </div>

        ${task.riskReason ? `
          <div class="kanban-card-risk">
            ⚠️ <span>${task.riskReason}</span>
          </div>
        ` : ''}

        <div class="kanban-card-meta">
          <div class="kanban-assignee">
            <span class="user-mini-avatar" title="${task.assignee || 'Unassigned'}">${avatar}</span>
            <span class="user-mini-name">${task.assignee || 'Unassigned'}</span>
          </div>

          <div class="kanban-card-right">
            ${hasDeps ? `<span class="dep-pill" title="Prerequisites: ${task.dependsOn.join(', ')}">🔗 ${task.dependsOn.length}</span>` : ''}
            <span class="due-date-pill ${this._isOverdue(task.dueDate) ? 'overdue' : ''}">📅 ${task.dueDate || 'No Due'}</span>
          </div>
        </div>

        <div class="kanban-card-footer-actions">
          <button class="btn-card-action btn-inspect-task" data-id="${task.id}" title="Inspect in Live Graph">🔍 Node</button>
          ${task.status !== 'done' ? `
            <button class="btn-card-action btn-quick-done" data-id="${task.id}" title="Mark Complete">✓ Done</button>
          ` : ''}
        </div>
      </div>
    `;
  }

  _isOverdue(dueDate) {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  }

  _attachDragDropEvents() {
    const cards = this.container.querySelectorAll('.kanban-task-card');
    const dropzones = this.container.querySelectorAll('.kanban-card-dropzone');

    cards.forEach(card => {
      card.addEventListener('dragstart', (e) => {
        this.draggedTaskId = card.getAttribute('data-task-id');
        card.classList.add('is-dragging');
        e.dataTransfer.setData('text/plain', this.draggedTaskId);
        e.dataTransfer.effectAllowed = 'move';
      });

      card.addEventListener('dragend', () => {
        card.classList.remove('is-dragging');
        this.draggedTaskId = null;
        dropzones.forEach(dz => dz.classList.remove('drag-over'));
      });
    });

    dropzones.forEach(zone => {
      zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        zone.classList.add('drag-over');
      });

      zone.addEventListener('dragleave', (e) => {
        if (!zone.contains(e.relatedTarget)) {
          zone.classList.remove('drag-over');
        }
      });

      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        const taskId = e.dataTransfer.getData('text/plain') || this.draggedTaskId;
        const targetColId = zone.getAttribute('data-col-id');

        if (taskId && targetColId) {
          const targetStatus = targetColId === 'review' ? 'review' : targetColId;
          store.updateTaskStatus(taskId, targetStatus);
          this.render();
        }
      });
    });
  }

  _attachButtonEvents() {
    this.container.querySelectorAll('.btn-quick-done').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = e.currentTarget.getAttribute('data-id');
        store.updateTaskStatus(id, 'done');
        this.render();
      });
    });

    this.container.querySelectorAll('.btn-inspect-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = e.currentTarget.getAttribute('data-id');
        store.setView('graph');
        window.dispatchEvent(new CustomEvent('nexus:inspect-node', { detail: { taskId: id } }));
      });
    });

    const btnRebalance = this.container.querySelector('#btnKanbanAutoRebalance');
    if (btnRebalance) {
      btnRebalance.addEventListener('click', () => {
        store.autoRebalanceWorkload();
        this.render();
      });
    }

    const btnNewTask = this.container.querySelector('#btnKanbanNewTask');
    if (btnNewTask) {
      btnNewTask.addEventListener('click', () => {
        const modal = document.getElementById('taskModal');
        if (modal) modal.classList.remove('hidden');
      });
    }
  }
}
