/**
 * NEXUS MIND - GANTT TIMELINE & CRITICAL PATH MATRIX
 * Visualizes sprint scheduling, task duration spans, prerequisite dependencies,
 * and critical path bottlenecks along a calibrated timeline.
 */
import { store } from '../state.js';

export class GanttEngine {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
  }

  render() {
    if (!this.container) return;

    const state = store.getState();
    const tasks = state.tasks;
    const projects = state.projects;

    // Determine min and max dates across tasks
    const dates = tasks
      .map(t => t.dueDate ? new Date(t.dueDate).getTime() : null)
      .filter(Boolean);

    const now = new Date();
    const minDate = dates.length ? new Date(Math.min(...dates, now.getTime() - 86400000 * 5)) : new Date(now.getTime() - 86400000 * 5);
    const maxDate = dates.length ? new Date(Math.max(...dates, now.getTime() + 86400000 * 20)) : new Date(now.getTime() + 86400000 * 20);

    const totalDays = Math.max(15, Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24)));
    const dayHeaders = [];
    for (let i = 0; i <= totalDays; i++) {
      const d = new Date(minDate.getTime() + i * 86400000);
      dayHeaders.push({
        label: `${d.getDate()} ${d.toLocaleString('default', { month: 'short' })}`,
        isToday: d.toDateString() === now.toDateString()
      });
    }

    this.container.innerHTML = `
      <div class="gantt-wrapper">
        <div class="gantt-header-toolbar">
          <div class="gantt-legend">
            <span class="gantt-legend-pill done">● Done</span>
            <span class="gantt-legend-pill in_progress">● In Progress</span>
            <span class="gantt-legend-pill blocked">● Blocked</span>
            <span class="gantt-legend-pill critical-path">⚡ Critical Path</span>
          </div>
          <div class="gantt-meta-info">
            <span>Timeline Span: <strong>${totalDays} Days</strong></span>
            <span>Forecast Delay: <strong>${state.sprintForecast.expectedDelayDays}d</strong></span>
          </div>
        </div>

        <div class="gantt-scrollable-area">
          <div class="gantt-grid-header">
            <div class="gantt-task-col-title">Task / Milestone</div>
            <div class="gantt-timeline-header-days">
              ${dayHeaders.map(d => `
                <div class="gantt-day-cell ${d.isToday ? 'today' : ''}">${d.label}</div>
              `).join('')}
            </div>
          </div>

          <div class="gantt-rows-container">
            ${projects.map(p => {
              const pTasks = tasks.filter(t => t.project === p.name);
              if (!pTasks.length) return '';

              return `
                <div class="gantt-project-group">
                  <div class="gantt-project-header">
                    <span class="gantt-proj-name">📁 ${p.name}</span>
                    <span class="gantt-proj-prog">${p.progress}% Complete</span>
                  </div>

                  ${pTasks.map(t => {
                    const taskDue = t.dueDate ? new Date(t.dueDate) : new Date(now.getTime() + 86400000 * 3);
                    const daysFromStart = Math.max(0, Math.ceil((taskDue - minDate) / (1000 * 60 * 60 * 24)));
                    const taskDurationDays = Math.max(3, (t.dependsOn ? t.dependsOn.length * 2 : 2) + 2);
                    const startDay = Math.max(0, daysFromStart - taskDurationDays);
                    
                    const leftPct = (startDay / totalDays) * 100;
                    const widthPct = Math.min(100 - leftPct, (taskDurationDays / totalDays) * 100);
                    const isCritical = t.priority === 'Critical' || t.aiRiskScore >= 0.75;

                    return `
                      <div class="gantt-task-row" data-task-id="${t.id}">
                        <div class="gantt-task-label">
                          <span class="gantt-task-id">[${t.id}]</span>
                          <span class="gantt-task-name" title="${t.title}">${t.title}</span>
                          <span class="gantt-task-assignee">${t.assignee}</span>
                        </div>

                        <div class="gantt-track">
                          <div class="gantt-bar ${t.status} ${isCritical ? 'critical-glow' : ''}" 
                               style="left: ${leftPct}%; width: ${Math.max(8, widthPct)}%;"
                               title="${t.title} (Due: ${t.dueDate || 'N/A'}) - Assignee: ${t.assignee}">
                            <span class="gantt-bar-title">${t.id}</span>
                            ${t.aiRiskScore >= 0.7 ? '<span class="gantt-risk-flag">⚠️</span>' : ''}
                          </div>
                        </div>
                      </div>
                    `;
                  }).join('')}
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    `;

    this._attachEvents();
  }

  _attachEvents() {
    this.container.querySelectorAll('.gantt-task-row').forEach(row => {
      row.addEventListener('click', () => {
        const id = row.getAttribute('data-task-id');
        store.setView('graph');
        window.dispatchEvent(new CustomEvent('nexus:inspect-node', { detail: { taskId: id } }));
      });
    });
  }
}
