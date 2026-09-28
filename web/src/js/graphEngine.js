/**
 * NEXUS MIND - ADVANCED LIVE TASK GRAPH ENGINE
 * Force-directed physics canvas, drag-to-connect dependency vectors,
 * critical path glowing particle flows, AI risk halos, and node inspection.
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

    // Interactive dependency connecting
    this.isConnectingDep = false;
    this.connectingSourceId = null;
    this.connectingMousePos = { x: 0, y: 0 };

    this.reassignPanelOpen = false;
    this.editDeadlineMode = false;

    this.initDelegatedEvents();
    this.initCustomListeners();
  }

  initCustomListeners() {
    window.addEventListener('nexus:inspect-node', (e) => {
      const { taskId } = e.detail;
      const task = store.getState().tasks.find(t => t.id === taskId);
      if (task) {
        this.selectedTaskId = taskId;
        this.panX = (this.svg.clientWidth / 2) - (task.x * this.zoomScale);
        this.panY = (this.svg.clientHeight / 2) - (task.y * this.zoomScale);
        this.render();
        this.showNodeDrawer(task);
      }
    });
  }

  initDelegatedEvents() {
    if (!this.svg) return;

    // 1. Mouse Down
    this.svg.addEventListener('mousedown', (e) => {
      this.clickStartPos = { x: e.clientX, y: e.clientY };

      const connectHandle = e.target.closest('.dep-connect-handle');
      if (connectHandle) {
        e.stopPropagation();
        this.isConnectingDep = true;
        this.connectingSourceId = connectHandle.getAttribute('data-id');
        const rect = this.svg.getBoundingClientRect();
        this.connectingMousePos = {
          x: (e.clientX - rect.left - this.panX) / this.zoomScale,
          y: (e.clientY - rect.top - this.panY) / this.zoomScale
        };
        return;
      }

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
      if (this.isConnectingDep) {
        const rect = this.svg.getBoundingClientRect();
        this.connectingMousePos = {
          x: (e.clientX - rect.left - this.panX) / this.zoomScale,
          y: (e.clientY - rect.top - this.panY) / this.zoomScale
        };
        this.render();
      } else if (this.isPanning) {
        this.panX = e.clientX - this.startPanPos.x;
        this.panY = e.clientY - this.startPanPos.y;
        this.render();
      } else if (this.draggedNode) {
        const dist = Math.hypot(e.clientX - this.clickStartPos.x, e.clientY - this.clickStartPos.y);
        if (dist > 5) {
          const rect = this.svg.getBoundingClientRect();
          this.draggedNode.x = (e.clientX - rect.left - this.panX) / this.zoomScale;
          this.draggedNode.y = (e.clientY - rect.top - this.panY) / this.zoomScale;
          this.render();
        }
      }
    });

    // 3. Mouse Up
    window.addEventListener('mouseup', (e) => {
      if (this.isConnectingDep) {
        const targetNodeGroup = document.elementFromPoint(e.clientX, e.clientY)?.closest('.graph-node-group');
        if (targetNodeGroup) {
          const targetId = targetNodeGroup.getAttribute('data-id');
          if (targetId && targetId !== this.connectingSourceId) {
            // Add dependency: connectingSourceId -> targetId
            store.addDependency(targetId, this.connectingSourceId);
          }
        }
        this.isConnectingDep = false;
        this.connectingSourceId = null;
        this.render();
        return;
      }

      const dist = Math.hypot(e.clientX - this.clickStartPos.x, e.clientY - this.clickStartPos.y);
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
        const { id, x, y } = this.draggedNode;
        this.draggedNode = null;
        store.persistTaskPosition(id, x, y);
      }
    });

    // 4. Tooltip Hover
    this.svg.addEventListener('mousemove', (e) => {
      const nodeGroup = e.target.closest('.graph-node-group');
      if (nodeGroup && !this.draggedNode && !this.isPanning && !this.isConnectingDep) {
        const taskId = nodeGroup.getAttribute('data-id');
        const state = store.getState();
        const task = state.tasks.find(t => t.id === taskId);
        if (task && this.tooltip) {
          this.tooltip.classList.remove('hidden');
          this.tooltip.style.top = `${e.clientY - 60}px`;
          this.tooltip.style.left = `${e.clientX + 15}px`;
          this.tooltip.innerHTML = `
            <div style="font-weight:800; color:var(--cyan-primary);">[${task.id}] ${task.title}</div>
            <div style="color:#CBD5E1; font-size:0.75rem;">👤 ${task.assignee} • 📅 ${task.dueDate || 'No SLA'}</div>
            <div style="font-size:0.75rem; margin-top:2px;">Status: <strong>${task.status.toUpperCase()}</strong> • Priority: <strong>${task.priority}</strong></div>
            ${task.aiRiskScore >= 0.5 ? `<div style="color:#EF4444; font-size:0.72rem; font-weight:bold; margin-top:2px;">⚠️ Risk: ${Math.round(task.aiRiskScore * 100)}% (${task.riskReason || 'Critical Bottleneck'})</div>` : ''}
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

  // ─────────────────────────────────────────────────────────────────────────
  // CPM OVERLAY — Glowing Critical Path + Slack Float Badges
  // ─────────────────────────────────────────────────────────────────────────
  get cpmModeActive() { return this._cpmMode; }

  async toggleCpmMode() {
    if (!this._cpmMode) {
      try {
        const { api } = await import('./api.js');
        const data = await api.getCriticalPath();
        this._cpmData = data;
        this._cpmMode = true;
        store.addToast('CPM Mode', `Critical path: ${data.critical_path?.length || 0} tasks (${data.project_duration_days}d)`, 'info');
      } catch (err) {
        // Build CPM locally from state
        this._cpmData = this._buildLocalCpm();
        this._cpmMode = true;
        store.addToast('CPM Mode (Local)', `Critical path computed from ${store.getState().tasks.length} tasks`, 'info');
      }
    } else {
      this._cpmMode = false;
      this._cpmData = null;
      store.addToast('CPM Mode Off', 'Returned to standard graph view.', 'info');
    }
    this.render();
    return this._cpmMode;
  }

  _buildLocalCpm() {
    // Client-side CPM approximation for demo/offline mode
    const tasks = store.getState().tasks || [];
    const taskMap = {};
    tasks.forEach(t => taskMap[t.id] = t);

    const durations = {};
    tasks.forEach(t => {
      const p = (t.priority || 'medium').toLowerCase();
      durations[t.id] = p === 'critical' ? 4.5 : p === 'high' ? 3.5 : p === 'medium' ? 2.5 : 1.5;
    });

    // Forward pass
    const es = {}, ef = {};
    const parents = {};
    tasks.forEach(t => {
      parents[t.id] = (t.dependsOn || []).filter(d => taskMap[d]);
    });

    const topo = this._topoSort(tasks.map(t => t.id), parents);
    topo.forEach(id => {
      const maxParentEf = parents[id].length ? Math.max(...parents[id].map(p => ef[p] || 0)) : 0;
      es[id] = maxParentEf;
      ef[id] = es[id] + (durations[id] || 2.5);
    });

    const projectDuration = topo.length ? Math.max(...topo.map(id => ef[id] || 0)) : 14.4;

    // Backward pass
    const children = {};
    tasks.forEach(t => { children[t.id] = []; });
    tasks.forEach(t => { (t.dependsOn || []).forEach(p => { if (children[p]) children[p].push(t.id); }); });

    const lf = {}, ls = {};
    [...topo].reverse().forEach(id => {
      lf[id] = children[id].length ? Math.min(...children[id].map(c => ls[c] || projectDuration)) : projectDuration;
      ls[id] = lf[id] - (durations[id] || 2.5);
    });

    const criticalPath = topo.filter(id => Math.abs((lf[id] || 0) - (ef[id] || 0)) <= 0.05);
    const schedule = {};
    topo.forEach(id => {
      const t = taskMap[id];
      schedule[id] = {
        task_id: id,
        title: t?.title || id,
        duration: durations[id],
        early_start: Math.round((es[id] || 0) * 10) / 10,
        early_finish: Math.round((ef[id] || 0) * 10) / 10,
        late_start: Math.round((ls[id] || 0) * 10) / 10,
        late_finish: Math.round((lf[id] || 0) * 10) / 10,
        slack: Math.round(((lf[id] || 0) - (ef[id] || 0)) * 10) / 10,
        is_critical: criticalPath.includes(id),
      };
    });

    return { project_duration_days: Math.round(projectDuration * 10) / 10, critical_path: criticalPath, schedule };
  }

  _topoSort(ids, parents) {
    const inDeg = {};
    ids.forEach(id => inDeg[id] = (parents[id] || []).length);
    const queue = ids.filter(id => inDeg[id] === 0);
    const result = [];
    const children = {};
    ids.forEach(id => { children[id] = []; });
    ids.forEach(id => { (parents[id] || []).forEach(p => { if (children[p]) children[p].push(id); }); });
    while (queue.length) {
      const u = queue.shift();
      result.push(u);
      (children[u] || []).forEach(v => { inDeg[v]--; if (inDeg[v] === 0) queue.push(v); });
    }
    ids.forEach(id => { if (!result.includes(id)) result.push(id); });
    return result;
  }

  startPhysicsLoop() {
    if (!this.physicsEnabled) return;
    
    const state = store.getState();
    const tasks = state.tasks;
    if (!tasks || tasks.length === 0) return;

    let moved = false;
    for (let i = 0; i < tasks.length; i++) {
      const n1 = tasks[i];
      if (typeof n1.x !== 'number' || isNaN(n1.x)) n1.x = 180 + (i % 5) * 160;
      if (typeof n1.y !== 'number' || isNaN(n1.y)) n1.y = 140 + Math.floor(i / 5) * 140;

      for (let j = i + 1; j < tasks.length; j++) {
        const n2 = tasks[j];
        if (typeof n2.x !== 'number' || isNaN(n2.x)) n2.x = 180 + (j % 5) * 160;
        if (typeof n2.y !== 'number' || isNaN(n2.y)) n2.y = 140 + Math.floor(j / 5) * 140;

        let dx = n2.x - n1.x;
        let dy = n2.y - n1.y;
        if (Math.abs(dx) < 0.001 && Math.abs(dy) < 0.001) {
          dx = (Math.random() - 0.5) * 30;
          dy = (Math.random() - 0.5) * 30;
        }

        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const minDist = 160;

        if (dist < minDist) {
          const force = (minDist - dist) * 0.035;
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
    let tasks = state.tasks || [];

    if (this.viewFilter === 'risk') {
      tasks = tasks.filter(t => t.aiRiskScore >= 0.6 || t.status === 'blocked');
    } else if (this.viewFilter === 'critical') {
      tasks = tasks.filter(t => t.priority === 'Critical' || t.priority === 'High');
    }

    const taskMap = {};
    (state.tasks || []).forEach((t, idx) => {
      if (typeof t.x !== 'number' || isNaN(t.x)) t.x = 180 + (idx % 5) * 160;
      if (typeof t.y !== 'number' || isNaN(t.y)) t.y = 140 + Math.floor(idx / 5) * 140;
      taskMap[t.id] = t;
    });


    let svgHtml = `
      <defs>
        <marker id="arrow-default" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#00F2FE" />
        </marker>
        <marker id="arrow-risk" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#EF4444" />
        </marker>
        <marker id="arrow-critical" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#F59E0B" />
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
        <linearGradient id="edge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#00F2FE" />
          <stop offset="100%" stop-color="#7F00FF" />
        </linearGradient>
        ${this._cpmMode ? `
        <filter id="glow-cpm" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="8" result="coloredBlur"/>
          <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <marker id="arrow-cpm" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#FFD700" />
        </marker>
        ` : ''}
      </defs>
      <g transform="translate(${this.panX}, ${this.panY}) scale(${this.zoomScale})">
        <rect class="graph-bg" width="3600" height="2400" x="-1200" y="-1200" fill="transparent"/>
    `;

    // 1. Dependency Vectors
    const criticalPathSet = new Set(this._cpmMode && this._cpmData ? (this._cpmData.critical_path || []) : []);
    const scheduleMap = this._cpmMode && this._cpmData ? (this._cpmData.schedule || {}) : {};

    tasks.forEach(targetNode => {
      if (targetNode.dependsOn && targetNode.dependsOn.length > 0) {
        targetNode.dependsOn.forEach(sourceId => {
          const sourceNode = taskMap[sourceId];
          if (sourceNode) {
            const isCpmCriticalEdge = this._cpmMode && criticalPathSet.has(targetNode.id) && criticalPathSet.has(sourceId);
            const isRiskEdge = !isCpmCriticalEdge && (targetNode.aiRiskScore > 0.6 || sourceNode.aiRiskScore > 0.6);
            const isCriticalPath = !isCpmCriticalEdge && !isRiskEdge && targetNode.priority === 'Critical' && sourceNode.priority === 'Critical';

            let strokeColor = isCpmCriticalEdge ? '#FFD700' : (isRiskEdge ? '#EF4444' : (isCriticalPath ? '#F59E0B' : '#00F2FE'));
            let markerId = isCpmCriticalEdge ? 'arrow-cpm' : (isRiskEdge ? 'arrow-risk' : (isCriticalPath ? 'arrow-critical' : 'arrow-default'));
            let strokeWidth = isCpmCriticalEdge ? 4 : (isRiskEdge || isCriticalPath ? 3 : 2);
            let filter = isCpmCriticalEdge ? 'filter="url(#glow-cpm)"' : '';
            let dashArray = isCpmCriticalEdge ? '12,0' : (isRiskEdge ? '6,4' : '8,6');

            const midX = (sourceNode.x + targetNode.x) / 2;
            const midY = (sourceNode.y + targetNode.y) / 2 - 30;
            const pathD = `M ${sourceNode.x} ${sourceNode.y} Q ${midX} ${midY} ${targetNode.x} ${targetNode.y}`;

            svgHtml += `
              <path d="${pathD}"
                stroke="${strokeColor}"
                stroke-width="${strokeWidth}"
                stroke-dasharray="${dashArray}"
                fill="none"
                opacity="${isCpmCriticalEdge ? 1 : 0.85}"
                ${filter}
                marker-end="url(#${markerId})">
                <animate attributeName="stroke-dashoffset" from="${isCpmCriticalEdge ? 48 : 24}" to="0" dur="${isCpmCriticalEdge ? '0.8s' : '1.2s'}" repeatCount="indefinite"/>
              </path>
            `;

            // CPM particle tracer on critical edges
            if (isCpmCriticalEdge) {
              svgHtml += `
                <circle r="5" fill="#FFD700" opacity="0.9">
                  <animateMotion dur="2s" repeatCount="indefinite" path="${pathD}"/>
                  <animate attributeName="opacity" values="0.9;0.3;0.9" dur="2s" repeatCount="indefinite"/>
                </circle>
              `;
            }
          }
        });
      }
    });

    // 1b. CPM Slack Float Badges (non-critical tasks)
    if (this._cpmMode && scheduleMap) {
      tasks.forEach(t => {
        const sched = scheduleMap[t.id];
        if (sched && !sched.is_critical && sched.slack > 0) {
          svgHtml += `
            <g transform="translate(${t.x + 30}, ${t.y - 22})">
              <rect rx="4" ry="4" width="58" height="16" fill="rgba(168,85,247,0.15)" stroke="#A855F7" stroke-width="0.8" opacity="0.9"/>
              <text font-size="8" fill="#A855F7" x="4" y="11" font-family="monospace" font-weight="700">+${sched.slack}d float</text>
            </g>
          `;
        }
        if (sched && sched.is_critical) {
          svgHtml += `
            <g transform="translate(${t.x - 28}, ${t.y - 22})">
              <rect rx="4" ry="4" width="56" height="16" fill="rgba(255,215,0,0.12)" stroke="#FFD700" stroke-width="0.8" opacity="0.9"/>
              <text font-size="8" fill="#FFD700" x="4" y="11" font-family="monospace" font-weight="700">CRITICAL</text>
            </g>
          `;
        }
      });
    }

    // CPM sidebar panel (injected into DOM overlay, not SVG)
    if (this._cpmMode && this._cpmData) {
      setTimeout(() => this._renderCpmPanel(), 50);
    } else {
      const panel = document.getElementById('cpmSidePanel');
      if (panel) panel.remove();
    }


    // 1b. Live Dragging Dependency Line
    if (this.isConnectingDep && this.connectingSourceId) {
      const srcNode = taskMap[this.connectingSourceId];
      if (srcNode) {
        svgHtml += `
          <line x1="${srcNode.x}" y1="${srcNode.y}" x2="${this.connectingMousePos.x}" y2="${this.connectingMousePos.y}"
                stroke="#00F2FE" stroke-width="2.5" stroke-dasharray="4,4" marker-end="url(#arrow-default)">
            <animate attributeName="stroke-dashoffset" from="12" to="0" dur="0.5s" repeatCount="indefinite"/>
          </line>
        `;
      }
    }

    // 2. Nodes
    tasks.forEach(node => {
      const isHighRisk = node.aiRiskScore >= 0.7;
      const isSelected = this.selectedTaskId === node.id;

      let statusColor = '#3B82F6';
      if (node.status === 'done') statusColor = '#10B981';
      if (node.status === 'blocked') statusColor = '#EF4444';
      if (node.priority === 'Critical') statusColor = '#F59E0B';
      if (isHighRisk) statusColor = '#EF4444';

      if (isHighRisk) {
        svgHtml += `
          <circle cx="${node.x}" cy="${node.y}" r="34" fill="none" stroke="#EF4444" stroke-width="2.5" opacity="0.8" filter="url(#glow-risk)">
            <animate attributeName="r" values="24;38;24" dur="1.8s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.9;0.2;0.9" dur="1.8s" repeatCount="indefinite"/>
          </circle>
        `;
      }

      if (isSelected) {
        svgHtml += `
          <circle cx="${node.x}" cy="${node.y}" r="32" fill="none" stroke="#00F2FE" stroke-width="3.5" opacity="0.9"/>
        `;
      }

      svgHtml += `
        <g class="graph-node-group" data-id="${node.id}" style="cursor: pointer;">
          <!-- Node Circle Body -->
          <circle cx="${node.x}" cy="${node.y}" r="24" fill="#0F172A" stroke="${statusColor}" stroke-width="${isSelected ? 4 : 3}" filter="url(#glow-node)" pointer-events="all"/>
          
          <!-- Node ID text -->
          <text x="${node.x}" y="${node.y + 4}" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="800" font-family="'JetBrains Mono', monospace" pointer-events="none">
            ${node.id && node.id.includes('-') ? node.id.split('-')[1] : (node.id || 'N')}
          </text>


          <!-- Label Card -->
          <rect x="${node.x - 65}" y="${node.y + 30}" width="130" height="24" rx="6" fill="rgba(15, 23, 42, 0.95)" stroke="${statusColor}" stroke-width="1.2" pointer-events="all"/>
          <text x="${node.x}" y="${node.y + 46}" text-anchor="middle" fill="#F3F4F6" font-size="9.5" font-weight="700" pointer-events="none">
            ${node.title.length > 18 ? node.title.substring(0, 16) + '...' : node.title}
          </text>

          <!-- Dependency Drag Port (small circle on right) -->
          <circle class="dep-connect-handle" data-id="${node.id}" cx="${node.x + 24}" cy="${node.y}" r="6" fill="#00F2FE" stroke="#0F172A" stroke-width="2" title="Drag to connect dependency" style="cursor: crosshair;" pointer-events="all"/>

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

    if (this.selectedTaskId !== task.id) {
      this.reassignPanelOpen = false;
      this.editDeadlineMode = false;
    }

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
      <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 16px;">Project: <strong>${task.project || 'General'}</strong></p>

      ${isHighRisk ? `
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
          <div style="font-weight: 800; font-size: 0.85rem; color: #EF4444; display: flex; align-items: center; gap: 6px;">
            ⚠️ AI Risk Hazard (${Math.round(task.aiRiskScore * 100)}%)
          </div>
          <p style="font-size: 0.775rem; color: var(--text-primary); margin-top: 4px; line-height: 1.4;">${task.riskReason || 'Critical dependency delay hazard.'}</p>
        </div>
      ` : ''}

      <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.85rem; color: var(--text-primary); margin-bottom: 16px; background: rgba(0,0,0,0.25); border: 1px solid var(--border-color); padding: 12px; border-radius: 8px;">
        <div><strong>👤 Assigned Owner:</strong> ${task.assignee}</div>
        <div><strong>🔥 Priority Level:</strong> ${task.priority}</div>

        <div id="deadlineRow">
          ${this.editDeadlineMode ? `
            <div style="display:flex; align-items:center; gap:8px;">
              <strong>📅 SLA Target Date:</strong>
              <input type="date" id="editDeadlineInput" value="${task.dueDate}" style="background: rgba(0,0,0,0.3); border: 1px solid var(--border-color); border-radius: 6px; padding: 4px 6px; color: #fff; font-size: 0.8rem;" />
              <button id="btnSaveDeadline" class="btn btn-primary btn-xs">Save</button>
              <button id="btnCancelDeadline" class="btn btn-ghost btn-xs">Cancel</button>
            </div>
          ` : `
            <div style="display:flex; align-items:center; justify-content:space-between;">
              <span><strong>📅 SLA Target Date:</strong> ${task.dueDate || 'Unset'}</span>
              <button id="btnEditDeadline" class="btn btn-ghost btn-xs">✏️ Edit Deadline</button>
            </div>
          `}
        </div>

        <div>
          <strong>🔗 Prerequisite Dependencies:</strong>
          <div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 6px;">
            ${task.dependsOn && task.dependsOn.length > 0 ? task.dependsOn.map(id => `
              <span style="font-size: 0.75rem; background: rgba(0,242,254,0.15); border: 1px solid var(--cyan-primary); color: #fff; padding: 2px 8px; border-radius: 12px; display: inline-flex; align-items: center; gap: 4px;">
                ${id}
                <button class="btn-remove-dep" data-task-id="${task.id}" data-dep-id="${id}" style="background:none; border:none; color:#EF4444; font-size:10px; cursor:pointer;">&times;</button>
              </span>
            `).join('') : '<span class="text-muted" style="font-size:0.75rem;">None (Standalone Node)</span>'}
          </div>
        </div>
      </div>

      <div style="margin-bottom: 16px;">
        <button id="btnToggleReassign" class="btn btn-ghost btn-sm" style="width:100%; color: var(--purple-primary); border-color: var(--purple-primary);">
          🔄 ${this.reassignPanelOpen ? 'Hide Reassignment Options' : 'Reassign Task to Another Teammate'}
        </button>
        ${this.reassignPanelOpen ? this.renderReassignPanel(task) : ''}
      </div>

      <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px;">
        <label style="font-size: 0.75rem; font-weight: 800; color: var(--text-secondary); letter-spacing: 0.5px;">UPDATE LIVE STATUS</label>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <button class="btn btn-ghost btn-xs btn-update-status" data-id="${task.id}" data-status="done" style="color: var(--status-done); border-color: var(--status-done);">✓ Completed</button>
          <button class="btn btn-ghost btn-xs btn-update-status" data-id="${task.id}" data-status="in_progress" style="color: var(--status-progress); border-color: var(--status-progress);">⚡ In Progress</button>
          <button class="btn btn-ghost btn-xs btn-update-status" data-id="${task.id}" data-status="blocked" style="color: var(--status-blocked); border-color: var(--status-blocked);">🛑 Blocked</button>
          <button class="btn btn-ghost btn-xs btn-update-status" data-id="${task.id}" data-status="review" style="color: #8B5CF6; border-color: #8B5CF6;">🔍 Review</button>
        </div>
      </div>

      <div style="border-top: 1px solid var(--border-color); padding-top: 12px; display: flex; justify-content: space-between;">
        <button id="btnDeleteTaskDrawer" class="btn btn-ghost btn-xs" style="color: #EF4444;" data-id="${task.id}">🗑️ Delete Node</button>
        <button id="btnCloseDrawerFooter" class="btn btn-primary btn-xs">Close</button>
      </div>
    `;

    this.drawer.classList.remove('hidden');
    this.attachDrawerEvents(task);
  }

  renderReassignPanel(task) {
    const candidates = store.getReassignmentCandidates(task.id);

    if (candidates.length === 0) {
      return `<p style="font-size:0.75rem; color:var(--text-muted); margin-top:8px;">No other teammates available for reassignment.</p>`;
    }

    return `
      <div style="display:flex; flex-direction:column; gap:8px; margin-top:10px; background: rgba(127,0,255,0.06); border: 1px solid var(--purple-primary); border-radius: 10px; padding: 10px;">
        <span style="font-size:0.7rem; color: var(--text-muted); letter-spacing:0.5px;">SUGGESTED BY SKILL MATCH & LOWEST WORKLOAD</span>
        ${candidates.map(c => `
          <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 8px 10px;">
            <div style="flex:1;">
              <div style="font-size:0.8rem; font-weight:700; color: var(--text-primary); display:flex; align-items:center; gap:6px;">
                ${c.name}
                ${c.skillMatch ? `<span style="font-size:0.65rem; background: rgba(16,185,129,0.2); color:#10B981; padding:1px 6px; border-radius:8px;">✓ Skill Match</span>` : ''}
              </div>
              <div style="font-size:0.7rem; color: var(--text-muted);">${c.role} • ${c.activeTasks} active task(s)</div>
              <div style="background: rgba(255,255,255,0.1); height: 5px; border-radius: 3px; margin-top: 4px; width: 140px; overflow: hidden;">
                <div style="width: ${Math.min(100, c.capacity)}%; height: 100%; background: ${c.capacity > 100 ? '#EF4444' : 'var(--cyan-primary)'};"></div>
              </div>
              <div style="font-size:0.65rem; color: var(--text-muted); margin-top:2px;">${c.capacity}% workload</div>
            </div>
            <button class="btn btn-primary btn-xs btn-confirm-reassign" data-id="${task.id}" data-assignee="${c.name}">Assign</button>
          </div>
        `).join('')}
      </div>
    `;
  }

  attachDrawerEvents(task) {
    const drawerContent = document.getElementById('nodeDrawerContent');

    drawerContent.querySelectorAll('.btn-update-status').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        const status = e.target.getAttribute('data-status');
        store.updateTaskStatus(id, status);
        const updatedTask = store.getState().tasks.find(t => t.id === id);
        if (updatedTask) this.showNodeDrawer(updatedTask);
      });
    });

    drawerContent.querySelectorAll('.btn-remove-dep').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const taskId = e.currentTarget.getAttribute('data-task-id');
        const depId = e.currentTarget.getAttribute('data-dep-id');
        store.removeDependency(taskId, depId);
        const updatedTask = store.getState().tasks.find(t => t.id === taskId);
        if (updatedTask) this.showNodeDrawer(updatedTask);
      });
    });

    // Deadline edit
    const editBtn = drawerContent.querySelector('#btnEditDeadline');
    if (editBtn) {
      editBtn.addEventListener('click', () => {
        this.editDeadlineMode = true;
        this.showNodeDrawer(task);
      });
    }

    const cancelDeadlineBtn = drawerContent.querySelector('#btnCancelDeadline');
    if (cancelDeadlineBtn) {
      cancelDeadlineBtn.addEventListener('click', () => {
        this.editDeadlineMode = false;
        this.showNodeDrawer(task);
      });
    }

    const saveDeadlineBtn = drawerContent.querySelector('#btnSaveDeadline');
    if (saveDeadlineBtn) {
      saveDeadlineBtn.addEventListener('click', () => {
        const input = document.getElementById('editDeadlineInput');
        if (input && input.value) {
          store.updateTaskDeadline(task.id, input.value);
        }
        this.editDeadlineMode = false;
        const updatedTask = store.getState().tasks.find(t => t.id === task.id);
        if (updatedTask) this.showNodeDrawer(updatedTask);
      });
    }

    // Reassignment
    const toggleReassignBtn = drawerContent.querySelector('#btnToggleReassign');
    if (toggleReassignBtn) {
      toggleReassignBtn.addEventListener('click', () => {
        this.reassignPanelOpen = !this.reassignPanelOpen;
        this.showNodeDrawer(task);
      });
    }

    drawerContent.querySelectorAll('.btn-confirm-reassign').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        const assignee = e.currentTarget.getAttribute('data-assignee');
        store.reassignTask(id, assignee);
        this.reassignPanelOpen = false;
        const updatedTask = store.getState().tasks.find(t => t.id === id);
        if (updatedTask) this.showNodeDrawer(updatedTask);
      });
    });

    // Delete task
    const deleteBtn = drawerContent.querySelector('#btnDeleteTaskDrawer');
    if (deleteBtn) {
      deleteBtn.addEventListener('click', () => {
        if (confirm(`Delete ${task.id}: "${task.title}" from live task graph?`)) {
          store.deleteTask(task.id);
          this.drawer.classList.add('hidden');
          this.render();
        }
      });
    }

    const closeBtn = drawerContent.querySelector('#btnCloseDrawerFooter');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        this.drawer.classList.add('hidden');
      });
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // CPM Sidebar Table Panel
  // ─────────────────────────────────────────────────────────────────────────
  _renderCpmPanel() {
    const existingPanel = document.getElementById('cpmSidePanel');
    if (existingPanel) existingPanel.remove();

    const data = this._cpmData;
    if (!data || !data.schedule) return;

    const schedules = Object.values(data.schedule);
    const criticalItems = schedules.filter(s => s.is_critical);
    const nonCritical = schedules.filter(s => !s.is_critical);

    const panel = document.createElement('div');
    panel.id = 'cpmSidePanel';
    panel.style.cssText = `
      position: absolute; top: 80px; right: 16px; width: 280px;
      background: rgba(11,15,25,0.95); border: 1px solid rgba(255,215,0,0.3);
      border-radius: 12px; padding: 14px; z-index: 20;
      backdrop-filter: blur(16px); box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      max-height: 70vh; overflow-y: auto;
      font-family: 'Inter', sans-serif;
      animation: slideInRight 0.3s cubic-bezier(0.16,1,0.3,1);
    `;

    panel.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <div>
          <div style="font-size:0.82rem; font-weight:800; color:#FFD700;">🏗️ CPM Schedule</div>
          <div style="font-size:0.68rem; color:#94A3B8; margin-top:1px;">Duration: ${data.project_duration_days}d</div>
        </div>
        <button id="btnCloseCpmPanel" style="background:none; border:none; color:#94A3B8; cursor:pointer; font-size:1rem; line-height:1;">×</button>
      </div>
      <div style="font-size:0.68rem; color:#FFD700; font-weight:700; margin-bottom:6px; letter-spacing:0.05em;">CRITICAL PATH (${criticalItems.length} tasks)</div>
      <div style="margin-bottom:12px;">
        ${criticalItems.map(s => `
          <div style="display:flex; justify-content:space-between; align-items:center; padding:5px 8px; margin-bottom:4px; background:rgba(255,215,0,0.06); border-left:2px solid #FFD700; border-radius:4px;">
            <div>
              <div style="font-size:0.72rem; color:#fff; font-weight:600;">${s.title.slice(0,24)}${s.title.length > 24 ? '…' : ''}</div>
              <div style="font-size:0.62rem; color:#94A3B8; font-family:monospace;">ES:${s.early_start} EF:${s.early_finish} LS:${s.late_start} LF:${s.late_finish}</div>
            </div>
            <div style="font-size:0.65rem; color:#FFD700; font-weight:700;">${s.duration}d</div>
          </div>
        `).join('')}
      </div>
      ${nonCritical.length > 0 ? `
        <div style="font-size:0.68rem; color:#A855F7; font-weight:700; margin-bottom:6px; letter-spacing:0.05em;">FLOAT TASKS (${nonCritical.length})</div>
        ${nonCritical.map(s => `
          <div style="display:flex; justify-content:space-between; align-items:center; padding:5px 8px; margin-bottom:4px; background:rgba(168,85,247,0.06); border-left:2px solid rgba(168,85,247,0.4); border-radius:4px;">
            <div>
              <div style="font-size:0.72rem; color:#fff;">${s.title.slice(0,24)}${s.title.length > 24 ? '…' : ''}</div>
              <div style="font-size:0.62rem; color:#94A3B8; font-family:monospace;">Slack: +${s.slack}d</div>
            </div>
            <div style="font-size:0.65rem; color:#A855F7; font-weight:700;">${s.duration}d</div>
          </div>
        `).join('')}
      ` : ''}
    `;

    // Mount to graph canvas container
    const canvasContainer = document.getElementById('graphCanvasContainer');
    if (canvasContainer) {
      canvasContainer.style.position = 'relative';
      canvasContainer.appendChild(panel);
    }

    document.getElementById('btnCloseCpmPanel')?.addEventListener('click', () => {
      this._cpmMode = false;
      this._cpmData = null;
      panel.remove();
      this.render();
    });
  }
}
