/**
 * LIVE TASK GRAPH ENGINE (SINGLE SOURCE OF TRUTH)
 * Handles mouse clicks, dragging, spring physics, and guaranteed node detail inspection.
 */

import { store } from './state.js';

export class LiveTaskGraphEngine {
  constructor(svgElementId, tooltipId, drawerId) {
    this.svg = document.getElementById(svgElementId);
    this.tooltip = document.getElementById(tooltipId);
    this.drawer = document.getElementById(drawerId);
    
    this.viewFilter = 'all'; // 'all' | 'risk' | 'critical'
    this.physicsEnabled = true;
    this.zoomScale = 1;
    this.panX = 0;
    this.panY = 0;
    this.isPanning = false;
    this.startPanPos = { x: 0, y: 0 };
    this.clickStartPos = { x: 0, y: 0 };

    this.draggedNode = null;
    this.selectedTaskId = null;
    this.animFrame = null;

    this.initDelegatedEvents();
  }

  /**
   * Mouse events using threshold check (dist < 6px => Click, dist >= 6px => Drag)
   * This guarantees 100% reliable node clicking even if the mouse shifts 1-2 pixels during click!
   */
  initDelegatedEvents() {
    if (!this.svg) return;

    // 1. Mouse Down
    this.svg.addEventListener('mousedown', (e) => {
      this.clickStartPos = { x: e.clientX, y: e.clientY };

      const nodeGroup = e.target.closest('.graph-node-group');
      if (nodeGroup) {
        e.stopPropagation();
        const taskId = nodeGroup.getAttribute('data-id');
        const state = store.getState();
        this.draggedNode = state.tasks.find(t => t.id === taskId) || null;
      } else {
        this.isPanning = true;
        this.startPanPos = { x: e.clientX - this.panX, y: e.clientY - this.panY };
      }
    });

    // 2. Mouse Move
    window.addEventListener('mousemove', (e) => {
      if (this.isPanning) {
        this.panX = e.clientX - this.startPanPos.x;
        this.panY = e.clientY - this.startPanPos.y;
        this.render();
      } else if (this.draggedNode) {
        const dist = Math.hypot(e.clientX - this.clickStartPos.x, e.clientY - this.clickStartPos.y);
        if (dist > 5) {
          const rect = this.svg.getBoundingClientRect();
          const mouseX = (e.clientX - rect.left - this.panX) / this.zoomScale;
          const mouseY = (e.clientY - rect.top - this.panY) / this.zoomScale;
          this.draggedNode.x = mouseX;
          this.draggedNode.y = mouseY;
          this.render();
        }
      }
    });

    // 3. Mouse Up (Handles Node Click Drawer Opening Guaranteed!)
    window.addEventListener('mouseup', (e) => {
      const dist = Math.hypot(e.clientX - this.clickStartPos.x, e.clientY - this.clickStartPos.y);

      // If mouse moved less than 6 pixels, it is a CLICK!
      if (dist < 6 && e.target) {
        const nodeGroup = e.target.closest('.graph-node-group');
        if (nodeGroup) {
          const taskId = nodeGroup.getAttribute('data-id');
          const state = store.getState();
          const task = state.tasks.find(t => t.id === taskId);
          if (task) {
            this.selectedTaskId = task.id;
            this.showNodeDrawer(task);
          }
        }
      }

      this.isPanning = false;
      if (this.draggedNode) {
        this.draggedNode = null;
        store.saveState();
      }
    });

    // 4. Tooltip Hover
    this.svg.addEventListener('mousemove', (e) => {
      const nodeGroup = e.target.closest('.graph-node-group');
      if (nodeGroup && !this.draggedNode && !this.isPanning) {
        const taskId = nodeGroup.getAttribute('data-id');
        const state = store.getState();
        const task = state.tasks.find(t => t.id === taskId);
        if (task && this.tooltip) {
          this.tooltip.classList.remove('hidden');
          this.tooltip.style.top = `${e.clientY - 50}px`;
          this.tooltip.style.left = `${e.clientX + 15}px`;
          this.tooltip.innerHTML = `
            <strong>[${task.id}] ${task.title}</strong><br/>
            <span>Owner: ${task.assignee}</span><br/>
            <span>Status: ${task.status.toUpperCase()} • Priority: ${task.priority}</span>
            ${task.aiRiskScore > 0.5 ? `<br/><span style="color:#EF4444; font-weight:bold;">⚠️ AI Risk: ${Math.round(task.aiRiskScore * 100)}% (${task.riskReason || 'Elevated Bottleneck'})</span>` : ''}
          `;
        }
      } else if (this.tooltip) {
        this.tooltip.classList.add('hidden');
      }
    });

    // 5. Zoom Wheel
    this.svg.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
      this.zoomScale = Math.min(2.5, Math.max(0.4, this.zoomScale * zoomFactor));
      this.render();
    });
  }

  setFilter(filterName) {
    this.viewFilter = filterName;
    this.render();
  }

  togglePhysics() {
    this.physicsEnabled = !this.physicsEnabled;
    if (this.physicsEnabled) {
      this.startPhysicsLoop();
    }
    return this.physicsEnabled;
  }

  zoomIn() {
    this.zoomScale = Math.min(2.5, this.zoomScale * 1.15);
    this.render();
  }

  zoomOut() {
    this.zoomScale = Math.max(0.4, this.zoomScale * 0.85);
    this.render();
  }

  resetView() {
    this.zoomScale = 1;
    this.panX = 0;
    this.panY = 0;
    this.render();
  }

  startPhysicsLoop() {
    if (!this.physicsEnabled) return;
    
    const state = store.getState();
    const tasks = state.tasks;

    let moved = false;
    for (let i = 0; i < tasks.length; i++) {
      for (let j = i + 1; j < tasks.length; j++) {
        const n1 = tasks[i];
        const n2 = tasks[j];
        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const minDist = 150;

        if (dist < minDist) {
          const force = (minDist - dist) * 0.04;
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          if (n1 !== this.draggedNode) { n1.x -= fx; n1.y -= fy; }
          if (n2 !== this.draggedNode) { n2.x += fx; n2.y += fy; }
          moved = true;
        }
      }
    }

    if (moved) {
      this.render();
    }

    if (this.physicsEnabled) {
      this.animFrame = requestAnimationFrame(() => this.startPhysicsLoop());
    }
  }

  render() {
    if (!this.svg) return;

    const state = store.getState();
    let tasks = state.tasks;

    if (this.viewFilter === 'risk') {
      tasks = tasks.filter(t => t.aiRiskScore >= 0.6 || t.status === 'blocked');
    } else if (this.viewFilter === 'critical') {
      tasks = tasks.filter(t => t.priority === 'Critical' || t.priority === 'High');
    }

    const taskMap = {};
    state.tasks.forEach(t => taskMap[t.id] = t);

    let svgHtml = `
      <defs>
        <marker id="arrow-default" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#00F2FE" />
        </marker>
        <marker id="arrow-risk" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#EF4444" />
        </marker>
        <filter id="glow-risk" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <filter id="glow-node" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      <g transform="translate(${this.panX}, ${this.panY}) scale(${this.zoomScale})">
        <rect class="graph-bg" width="3000" height="2000" x="-1000" y="-1000" fill="transparent"/>
    `;

    // 1. Dependency Vectors
    tasks.forEach(targetNode => {
      if (targetNode.dependsOn && targetNode.dependsOn.length > 0) {
        targetNode.dependsOn.forEach(sourceId => {
          const sourceNode = taskMap[sourceId];
          if (sourceNode) {
            const isRiskEdge = targetNode.aiRiskScore > 0.6 || sourceNode.aiRiskScore > 0.6;
            const strokeColor = isRiskEdge ? '#EF4444' : '#00F2FE';
            const markerId = isRiskEdge ? 'arrow-risk' : 'arrow-default';

            const midX = (sourceNode.x + targetNode.x) / 2;
            const midY = (sourceNode.y + targetNode.y) / 2 - 30;
            const pathD = `M ${sourceNode.x} ${sourceNode.y} Q ${midX} ${midY} ${targetNode.x} ${targetNode.y}`;

            svgHtml += `
              <path d="${pathD}"
                stroke="${strokeColor}"
                stroke-width="${isRiskEdge ? 2.8 : 2}"
                stroke-dasharray="${isRiskEdge ? '6,4' : '8,6'}"
                fill="none"
                opacity="0.85"
                marker-end="url(#${markerId})">
                <animate attributeName="stroke-dashoffset" from="20" to="0" dur="1s" repeatCount="indefinite"/>
              </path>
            `;
          }
        });
      }
    });

    // 2. Nodes
    tasks.forEach(node => {
      const isHighRisk = node.aiRiskScore >= 0.7;
      const isSelected = this.selectedTaskId === node.id;

      let statusColor = '#3B82F6';
      if (node.status === 'done') statusColor = '#10B981';
      if (node.status === 'blocked') statusColor = '#F59E0B';
      if (isHighRisk) statusColor = '#EF4444';

      if (isHighRisk) {
        svgHtml += `
          <circle cx="${node.x}" cy="${node.y}" r="34" fill="none" stroke="#EF4444" stroke-width="2.5" opacity="0.8" filter="url(#glow-risk)">
            <animate attributeName="r" values="24;38;24" dur="1.8s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.9;0.2;0.9" dur="1.8s" repeatCount="indefinite"/>
          </circle>
        `;
      }

      // Selection Ring
      if (isSelected) {
        svgHtml += `
          <circle cx="${node.x}" cy="${node.y}" r="30" fill="none" stroke="#00F2FE" stroke-width="3" opacity="0.9"/>
        `;
      }

      svgHtml += `
        <g class="graph-node-group" data-id="${node.id}" style="cursor: pointer;">
          <!-- Node Circle -->
          <circle cx="${node.x}" cy="${node.y}" r="24" fill="#0F172A" stroke="${statusColor}" stroke-width="${isSelected ? 4 : 3}" filter="url(#glow-node)" pointer-events="all"/>
          
          <!-- Node ID text -->
          <text x="${node.x}" y="${node.y + 4}" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="800" font-family="'JetBrains Mono', monospace" pointer-events="none">
            ${node.id.split('-')[1]}
          </text>

          <!-- Label Card -->
          <rect x="${node.x - 65}" y="${node.y + 30}" width="130" height="24" rx="6" fill="rgba(15, 23, 42, 0.95)" stroke="${statusColor}" stroke-width="1.2" pointer-events="all"/>
          <text x="${node.x}" y="${node.y + 46}" text-anchor="middle" fill="#F3F4F6" font-size="9.5" font-weight="700" pointer-events="none">
            ${node.title.length > 18 ? node.title.substring(0, 16) + '...' : node.title}
          </text>

          ${isHighRisk ? `
            <circle cx="${node.x + 18}" cy="${node.y - 18}" r="10" fill="#EF4444" pointer-events="none"/>
            <text x="${node.x + 18}" y="${node.y - 14}" text-anchor="middle" fill="#FFF" font-size="11" font-weight="900" pointer-events="none">!</text>
          ` : ''}
        </g>
      `;
    });

    svgHtml += `</g>`;
    this.svg.innerHTML = svgHtml;
  }

  showNodeDrawer(task) {
    if (!this.drawer || !task) return;
    
    this.selectedTaskId = task.id;
    this.render();

    const drawerContent = document.getElementById('nodeDrawerContent');
    const isHighRisk = task.aiRiskScore >= 0.7;

    drawerContent.innerHTML = `
      <div style="margin-top: 10px; display: flex; align-items: center; justify-content: space-between;">
        <span class="task-status-pill ${task.status}">${task.status.replace('_', ' ')}</span>
        <span style="font-size: 0.85rem; font-family: var(--font-mono); font-weight: 800; color: var(--cyan-primary);">${task.id}</span>
      </div>

      <h3 style="font-size: 1.15rem; color: var(--text-primary); margin: 14px 0 6px 0;">${task.title}</h3>
      <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 16px;">Project: <strong>${task.project}</strong></p>

      ${isHighRisk ? `
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
          <div style="font-weight: 800; font-size: 0.85rem; color: #EF4444; display: flex; align-items: center; gap: 6px;">
            ⚠️ AI Risk Hazard (${Math.round(task.aiRiskScore * 100)}%)
          </div>
          <p style="font-size: 0.775rem; color: var(--text-primary); margin-top: 4px; line-height: 1.4;">${task.riskReason || 'Critical dependency delay hazard.'}</p>
        </div>
      ` : ''}

      <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.85rem; color: var(--text-primary); margin-bottom: 20px; background: rgba(0,0,0,0.04); padding: 12px; border-radius: 8px;">
        <div><strong>👤 Assigned Owner:</strong> ${task.assignee}</div>
        <div><strong>🔥 Priority Level:</strong> ${task.priority}</div>
        <div><strong>📅 SLA Target Date:</strong> ${task.dueDate}</div>
        <div><strong>🔗 Prerequisite Tasks:</strong> ${task.dependsOn.length > 0 ? task.dependsOn.map(id => `<span style="color:var(--cyan-primary); font-weight:bold;">${id}</span>`).join(', ') : 'None (Root Node)'}</div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 8px;">
        <label style="font-size: 0.75rem; font-weight: 800; color: var(--text-secondary); letter-spacing: 0.5px;">UPDATE LIVE GRAPH STATUS</label>
        <button class="btn btn-ghost btn-sm btn-update-status" data-id="${task.id}" data-status="done" style="color: var(--status-done); border-color: var(--status-done);">Mark Complete (Done) ✓</button>
        <button class="btn btn-ghost btn-sm btn-update-status" data-id="${task.id}" data-status="in_progress" style="color: var(--status-progress); border-color: var(--status-progress);">Set In Progress</button>
        <button class="btn btn-ghost btn-sm btn-update-status" data-id="${task.id}" data-status="blocked" style="color: var(--status-blocked); border-color: var(--status-blocked);">Mark Blocked 🛑</button>
      </div>
    `;

    this.drawer.classList.remove('hidden');

    drawerContent.querySelectorAll('.btn-update-status').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        const status = e.target.getAttribute('data-status');
        store.updateTaskStatus(id, status);
        const updatedTask = store.getState().tasks.find(t => t.id === id);
        this.showNodeDrawer(updatedTask);
      });
    });
  }
}
