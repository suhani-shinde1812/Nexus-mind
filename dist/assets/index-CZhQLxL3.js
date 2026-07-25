(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const i of document.querySelectorAll('link[rel="modulepreload"]'))a(i);new MutationObserver(i=>{for(const t of i)if(t.type==="childList")for(const n of t.addedNodes)n.tagName==="LINK"&&n.rel==="modulepreload"&&a(n)}).observe(document,{childList:!0,subtree:!0});function s(i){const t={};return i.integrity&&(t.integrity=i.integrity),i.referrerPolicy&&(t.referrerPolicy=i.referrerPolicy),i.crossOrigin==="use-credentials"?t.credentials="include":i.crossOrigin==="anonymous"?t.credentials="omit":t.credentials="same-origin",t}function a(i){if(i.ep)return;i.ep=!0;const t=s(i);fetch(i.href,t)}})();const v="NEXUS_MIND_STATE_V3",f={theme:"dark",currentRole:"team_lead",currentUser:{id:"u2",name:"Sarah Jenkins",role:"Team Lead",avatar:"SJ",email:"sarah.jenkins@nexusmind.ai"},users:[{id:"u1",name:"Alex Vance",role:"Frontend Lead",avatar:"AV",capacity:80,activeTasks:3},{id:"u2",name:"Sarah Jenkins",role:"Team Lead",avatar:"SJ",capacity:60,activeTasks:2},{id:"u3",name:"Devon Reed",role:"Backend Engineer",avatar:"DR",capacity:110,activeTasks:5},{id:"u4",name:"Priya Sharma",role:"AI/ML Engineer",avatar:"PS",capacity:40,activeTasks:1},{id:"u5",name:"Marcus Chen",role:"Project Manager",avatar:"MC",capacity:50,activeTasks:2}],projects:[{id:"p1",name:"Sprint Alpha - Cloud Migration",lead:"Sarah Jenkins",deadline:"2026-08-15",progress:65},{id:"p2",name:"Mobile App v2.0",lead:"Alex Vance",deadline:"2026-09-01",progress:40},{id:"p3",name:"Security & Compliance",lead:"Elena Rostova",deadline:"2026-08-01",progress:90}],tasks:[{id:"TASK-101",title:"Cloud Infrastructure Provisioning (Terraform)",project:"Sprint Alpha - Cloud Migration",assignee:"Devon Reed",status:"done",priority:"High",dependsOn:[],x:120,y:180,dueDate:"2026-07-20",aiRiskScore:.1,riskReason:null},{id:"TASK-102",title:"PostgreSQL Database Schema & Migration Script",project:"Sprint Alpha - Cloud Migration",assignee:"Devon Reed",status:"in_progress",priority:"Critical",dependsOn:["TASK-101"],x:300,y:140,dueDate:"2026-07-28",aiRiskScore:.85,riskReason:"Devon Reed is at 110% capacity & SLA deadline approaching."},{id:"TASK-103",title:"OAuth2 Authentication API Gateway",project:"Security & Compliance",assignee:"Alex Vance",status:"in_progress",priority:"High",dependsOn:["TASK-102"],x:480,y:140,dueDate:"2026-07-30",aiRiskScore:.75,riskReason:"Prerequisite TASK-102 is at high risk of slipping."},{id:"TASK-104",title:"React Dashboard UI & Role Authorization Views",project:"Mobile App v2.0",assignee:"Alex Vance",status:"blocked",priority:"High",dependsOn:["TASK-103"],x:660,y:200,dueDate:"2026-08-05",aiRiskScore:.92,riskReason:"BLOCKED by TASK-103 which is delayed downstream."},{id:"TASK-105",title:"AI Assistant Vector Search Integration (Milvus)",project:"Sprint Alpha - Cloud Migration",assignee:"Priya Sharma",status:"in_progress",priority:"Medium",dependsOn:["TASK-101"],x:300,y:320,dueDate:"2026-08-02",aiRiskScore:.2,riskReason:null},{id:"TASK-106",title:"Real-Time Notification Websocket Cluster",project:"Mobile App v2.0",assignee:"Devon Reed",status:"blocked",priority:"Medium",dependsOn:["TASK-102","TASK-105"],x:480,y:320,dueDate:"2026-08-08",aiRiskScore:.8,riskReason:"Assignee Devon Reed has 5 assigned tasks simultaneously."},{id:"TASK-107",title:"Redis Caching Layer & Rate Limiter Middleware",project:"Security & Compliance",assignee:"Devon Reed",status:"in_progress",priority:"High",dependsOn:["TASK-103"],x:660,y:340,dueDate:"2026-08-10",aiRiskScore:.65,riskReason:"Depends on TASK-103 API Gateway."},{id:"TASK-108",title:"End-to-End System SLA Monitoring Dashboard",project:"Sprint Alpha - Cloud Migration",assignee:"Sarah Jenkins",status:"in_progress",priority:"Critical",dependsOn:["TASK-104","TASK-107"],x:840,y:260,dueDate:"2026-08-14",aiRiskScore:.4,riskReason:"Final release milestone node."}],policies:[{title:"Remote Work Policy",category:"HR & Operations",tags:["work","policy","remote"],summary:"Flexible hybrid schedule requires mandatory daily standup updates and core working hours (10 AM - 4 PM IST)."},{title:"SLA Escalation Guideline",category:"Engineering & QA",tags:["sla","critical","bugs"],summary:"P0 Critical Bugs must be acknowledged within 30 minutes and resolved within 24 hours with AI root-cause diagnostic reports."},{title:"Security Secret Storage Policy",category:"Infra & Security",tags:["oauth","credentials","vault"],summary:"All production secrets and API credentials must be stored in HashiCorp Vault. Storing raw tokens in repo is strictly prohibited."}],aiAlerts:[{id:"alt-1",severity:"critical",title:"Critical Path Hazard: Devon Reed",message:"Devon Reed is assigned 5 concurrent tasks (110% capacity load). TASK-102 is blocking 3 downstream milestones.",timestamp:"Just now",taskId:"TASK-102"},{id:"alt-2",severity:"warning",title:"Dependency SLA Delay",message:"TASK-104 (React Dashboard UI) is currently BLOCKED by delayed OAuth2 API Gateway.",timestamp:"10 mins ago",taskId:"TASK-104"},{id:"alt-3",severity:"info",title:"AI Workload Rebalance Recommendation",message:"Reassigning TASK-106 to Priya Sharma will reduce Devon Reed capacity load to 75% and unblock Sprint Alpha.",timestamp:"25 mins ago",taskId:"TASK-106"}],systemStats:{cpuLoad:"28%",memoryUsage:"3.4 / 8.0 GB",activeConnections:142,graphNodeCount:8,graphEdgeCount:7,aiInferenceLatency:"184ms"}};class x{constructor(){this.listeners=[],this.loadState()}loadState(){try{const e=localStorage.getItem(v);e?this.state=JSON.parse(e):(this.state=JSON.parse(JSON.stringify(f)),this.saveState())}catch{this.state=JSON.parse(JSON.stringify(f))}}saveState(){try{localStorage.setItem(v,JSON.stringify(this.state)),this.notify()}catch(e){console.error("Failed to save state",e)}}getState(){return this.state}subscribe(e){return this.listeners.push(e),()=>{this.listeners=this.listeners.filter(s=>s!==e)}}notify(){this.listeners.forEach(e=>e(this.state))}toggleTheme(){return this.state.theme=this.state.theme==="dark"?"light":"dark",this.saveState(),this.state.theme}setRole(e){this.state.currentRole=e;const s={employee:{id:"u1",name:"Alex Vance",role:"Frontend Lead",avatar:"AV",email:"alex.vance@nexusmind.ai"},team_lead:{id:"u2",name:"Sarah Jenkins",role:"Team Lead",avatar:"SJ",email:"sarah.jenkins@nexusmind.ai"},project_manager:{id:"u5",name:"Marcus Chen",role:"Project Manager",avatar:"MC",email:"marcus.chen@nexusmind.ai"},admin:{id:"u6",name:"Elena Rostova",role:"Administrator",avatar:"ER",email:"elena.rostova@nexusmind.ai"}};this.state.currentUser=s[e]||s.team_lead,this.saveState()}addTask(e){const a={id:`TASK-${100+this.state.tasks.length+1}`,title:e.title,project:e.project||"Sprint Alpha - Cloud Migration",assignee:e.assignee||"Sarah Jenkins",status:e.status||"in_progress",priority:e.priority||"Medium",dependsOn:e.dependsOn?[e.dependsOn]:[],x:400+(Math.random()*120-60),y:250+(Math.random()*120-60),dueDate:e.dueDate||"2026-08-10",aiRiskScore:.1,riskReason:null};return this.state.tasks.push(a),this.state.systemStats.graphNodeCount=this.state.tasks.length,this.state.systemStats.graphEdgeCount+=a.dependsOn.length,this.saveState(),a}updateTaskStatus(e,s){const a=this.state.tasks.find(i=>i.id===e);a&&(a.status=s,s==="done"&&(a.aiRiskScore=.05,a.riskReason=null,this.state.tasks.forEach(i=>{i.dependsOn.includes(e)&&i.status==="blocked"&&(i.status="in_progress",i.aiRiskScore=.2,i.riskReason="Unblocked by prerequisite completion!")})),this.saveState())}autoRebalanceWorkload(){const e=this.state.tasks.filter(s=>s.assignee==="Devon Reed"&&s.status!=="done");if(e.length>0){const s=e[e.length-1];s.assignee="Priya Sharma",s.riskReason="Reassigned by AI Workload Rebalancer to optimize team velocity.",s.aiRiskScore=.25;const a=this.state.users.find(t=>t.name==="Devon Reed"),i=this.state.users.find(t=>t.name==="Priya Sharma");return a&&(a.capacity=75,a.activeTasks-=1),i&&(i.capacity=70,i.activeTasks+=1),this.addAlert({severity:"info",title:"⚡ AI Workload Rebalanced!",message:`Successfully reassigned ${s.id} to Priya Sharma. Devon Reed capacity load reduced to 75%.`}),this.saveState(),!0}return!1}addAlert(e){const s={id:`alt-${Date.now()}`,severity:e.severity||"warning",title:e.title,message:e.message,timestamp:"Just now",taskId:e.taskId||null};this.state.aiAlerts.unshift(s),this.saveState()}}const d=new x;class A{constructor(e,s,a){this.svg=document.getElementById(e),this.tooltip=document.getElementById(s),this.drawer=document.getElementById(a),this.viewFilter="all",this.physicsEnabled=!0,this.zoomScale=1,this.panX=0,this.panY=0,this.isPanning=!1,this.startPanPos={x:0,y:0},this.clickStartPos={x:0,y:0},this.draggedNode=null,this.selectedTaskId=null,this.animFrame=null,this.initDelegatedEvents()}initDelegatedEvents(){this.svg&&(this.svg.addEventListener("mousedown",e=>{this.clickStartPos={x:e.clientX,y:e.clientY};const s=e.target.closest(".graph-node-group");if(s){e.stopPropagation();const a=s.getAttribute("data-id"),i=d.getState();this.draggedNode=i.tasks.find(t=>t.id===a)||null}else this.isPanning=!0,this.startPanPos={x:e.clientX-this.panX,y:e.clientY-this.panY}}),window.addEventListener("mousemove",e=>{if(this.isPanning)this.panX=e.clientX-this.startPanPos.x,this.panY=e.clientY-this.startPanPos.y,this.render();else if(this.draggedNode&&Math.hypot(e.clientX-this.clickStartPos.x,e.clientY-this.clickStartPos.y)>5){const a=this.svg.getBoundingClientRect(),i=(e.clientX-a.left-this.panX)/this.zoomScale,t=(e.clientY-a.top-this.panY)/this.zoomScale;this.draggedNode.x=i,this.draggedNode.y=t,this.render()}}),window.addEventListener("mouseup",e=>{if(Math.hypot(e.clientX-this.clickStartPos.x,e.clientY-this.clickStartPos.y)<6&&e.target){const a=e.target.closest(".graph-node-group");if(a){const i=a.getAttribute("data-id"),n=d.getState().tasks.find(r=>r.id===i);n&&(this.selectedTaskId=n.id,this.showNodeDrawer(n))}}this.isPanning=!1,this.draggedNode&&(this.draggedNode=null,d.saveState())}),this.svg.addEventListener("mousemove",e=>{const s=e.target.closest(".graph-node-group");if(s&&!this.draggedNode&&!this.isPanning){const a=s.getAttribute("data-id"),t=d.getState().tasks.find(n=>n.id===a);t&&this.tooltip&&(this.tooltip.classList.remove("hidden"),this.tooltip.style.top=`${e.clientY-50}px`,this.tooltip.style.left=`${e.clientX+15}px`,this.tooltip.innerHTML=`
            <strong>[${t.id}] ${t.title}</strong><br/>
            <span>Owner: ${t.assignee}</span><br/>
            <span>Status: ${t.status.toUpperCase()} • Priority: ${t.priority}</span>
            ${t.aiRiskScore>.5?`<br/><span style="color:#EF4444; font-weight:bold;">⚠️ AI Risk: ${Math.round(t.aiRiskScore*100)}% (${t.riskReason||"Elevated Bottleneck"})</span>`:""}
          `)}else this.tooltip&&this.tooltip.classList.add("hidden")}),this.svg.addEventListener("wheel",e=>{e.preventDefault();const s=e.deltaY<0?1.08:.92;this.zoomScale=Math.min(2.5,Math.max(.4,this.zoomScale*s)),this.render()}))}setFilter(e){this.viewFilter=e,this.render()}togglePhysics(){return this.physicsEnabled=!this.physicsEnabled,this.physicsEnabled&&this.startPhysicsLoop(),this.physicsEnabled}zoomIn(){this.zoomScale=Math.min(2.5,this.zoomScale*1.15),this.render()}zoomOut(){this.zoomScale=Math.max(.4,this.zoomScale*.85),this.render()}resetView(){this.zoomScale=1,this.panX=0,this.panY=0,this.render()}startPhysicsLoop(){if(!this.physicsEnabled)return;const s=d.getState().tasks;let a=!1;for(let i=0;i<s.length;i++)for(let t=i+1;t<s.length;t++){const n=s[i],r=s[t],o=r.x-n.x,c=r.y-n.y,l=Math.sqrt(o*o+c*c)||1,p=150;if(l<p){const u=(p-l)*.04,g=o/l*u,h=c/l*u;n!==this.draggedNode&&(n.x-=g,n.y-=h),r!==this.draggedNode&&(r.x+=g,r.y+=h),a=!0}}a&&this.render(),this.physicsEnabled&&(this.animFrame=requestAnimationFrame(()=>this.startPhysicsLoop()))}render(){if(!this.svg)return;const e=d.getState();let s=e.tasks;this.viewFilter==="risk"?s=s.filter(t=>t.aiRiskScore>=.6||t.status==="blocked"):this.viewFilter==="critical"&&(s=s.filter(t=>t.priority==="Critical"||t.priority==="High"));const a={};e.tasks.forEach(t=>a[t.id]=t);let i=`
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
    `;s.forEach(t=>{t.dependsOn&&t.dependsOn.length>0&&t.dependsOn.forEach(n=>{const r=a[n];if(r){const o=t.aiRiskScore>.6||r.aiRiskScore>.6,c=o?"#EF4444":"#00F2FE",l=o?"arrow-risk":"arrow-default",p=(r.x+t.x)/2,u=(r.y+t.y)/2-30,g=`M ${r.x} ${r.y} Q ${p} ${u} ${t.x} ${t.y}`;i+=`
              <path d="${g}"
                stroke="${c}"
                stroke-width="${o?2.8:2}"
                stroke-dasharray="${o?"6,4":"8,6"}"
                fill="none"
                opacity="0.85"
                marker-end="url(#${l})">
                <animate attributeName="stroke-dashoffset" from="20" to="0" dur="1s" repeatCount="indefinite"/>
              </path>
            `}})}),s.forEach(t=>{const n=t.aiRiskScore>=.7,r=this.selectedTaskId===t.id;let o="#3B82F6";t.status==="done"&&(o="#10B981"),t.status==="blocked"&&(o="#F59E0B"),n&&(o="#EF4444"),n&&(i+=`
          <circle cx="${t.x}" cy="${t.y}" r="34" fill="none" stroke="#EF4444" stroke-width="2.5" opacity="0.8" filter="url(#glow-risk)">
            <animate attributeName="r" values="24;38;24" dur="1.8s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.9;0.2;0.9" dur="1.8s" repeatCount="indefinite"/>
          </circle>
        `),r&&(i+=`
          <circle cx="${t.x}" cy="${t.y}" r="30" fill="none" stroke="#00F2FE" stroke-width="3" opacity="0.9"/>
        `),i+=`
        <g class="graph-node-group" data-id="${t.id}" style="cursor: pointer;">
          <!-- Node Circle -->
          <circle cx="${t.x}" cy="${t.y}" r="24" fill="#0F172A" stroke="${o}" stroke-width="${r?4:3}" filter="url(#glow-node)" pointer-events="all"/>
          
          <!-- Node ID text -->
          <text x="${t.x}" y="${t.y+4}" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="800" font-family="'JetBrains Mono', monospace" pointer-events="none">
            ${t.id.split("-")[1]}
          </text>

          <!-- Label Card -->
          <rect x="${t.x-65}" y="${t.y+30}" width="130" height="24" rx="6" fill="rgba(15, 23, 42, 0.95)" stroke="${o}" stroke-width="1.2" pointer-events="all"/>
          <text x="${t.x}" y="${t.y+46}" text-anchor="middle" fill="#F3F4F6" font-size="9.5" font-weight="700" pointer-events="none">
            ${t.title.length>18?t.title.substring(0,16)+"...":t.title}
          </text>

          ${n?`
            <circle cx="${t.x+18}" cy="${t.y-18}" r="10" fill="#EF4444" pointer-events="none"/>
            <text x="${t.x+18}" y="${t.y-14}" text-anchor="middle" fill="#FFF" font-size="11" font-weight="900" pointer-events="none">!</text>
          `:""}
        </g>
      `}),i+="</g>",this.svg.innerHTML=i}showNodeDrawer(e){if(!this.drawer||!e)return;this.selectedTaskId=e.id,this.render();const s=document.getElementById("nodeDrawerContent"),a=e.aiRiskScore>=.7;s.innerHTML=`
      <div style="margin-top: 10px; display: flex; align-items: center; justify-content: space-between;">
        <span class="task-status-pill ${e.status}">${e.status.replace("_"," ")}</span>
        <span style="font-size: 0.85rem; font-family: var(--font-mono); font-weight: 800; color: var(--cyan-primary);">${e.id}</span>
      </div>

      <h3 style="font-size: 1.15rem; color: var(--text-primary); margin: 14px 0 6px 0;">${e.title}</h3>
      <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 16px;">Project: <strong>${e.project}</strong></p>

      ${a?`
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; padding: 12px; border-radius: 10px; margin-bottom: 16px;">
          <div style="font-weight: 800; font-size: 0.85rem; color: #EF4444; display: flex; align-items: center; gap: 6px;">
            ⚠️ AI Risk Hazard (${Math.round(e.aiRiskScore*100)}%)
          </div>
          <p style="font-size: 0.775rem; color: var(--text-primary); margin-top: 4px; line-height: 1.4;">${e.riskReason||"Critical dependency delay hazard."}</p>
        </div>
      `:""}

      <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.85rem; color: var(--text-primary); margin-bottom: 20px; background: rgba(0,0,0,0.04); padding: 12px; border-radius: 8px;">
        <div><strong>👤 Assigned Owner:</strong> ${e.assignee}</div>
        <div><strong>🔥 Priority Level:</strong> ${e.priority}</div>
        <div><strong>📅 SLA Target Date:</strong> ${e.dueDate}</div>
        <div><strong>🔗 Prerequisite Tasks:</strong> ${e.dependsOn.length>0?e.dependsOn.map(i=>`<span style="color:var(--cyan-primary); font-weight:bold;">${i}</span>`).join(", "):"None (Root Node)"}</div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 8px;">
        <label style="font-size: 0.75rem; font-weight: 800; color: var(--text-secondary); letter-spacing: 0.5px;">UPDATE LIVE GRAPH STATUS</label>
        <button class="btn btn-ghost btn-sm btn-update-status" data-id="${e.id}" data-status="done" style="color: var(--status-done); border-color: var(--status-done);">Mark Complete (Done) ✓</button>
        <button class="btn btn-ghost btn-sm btn-update-status" data-id="${e.id}" data-status="in_progress" style="color: var(--status-progress); border-color: var(--status-progress);">Set In Progress</button>
        <button class="btn btn-ghost btn-sm btn-update-status" data-id="${e.id}" data-status="blocked" style="color: var(--status-blocked); border-color: var(--status-blocked);">Mark Blocked 🛑</button>
      </div>
    `,this.drawer.classList.remove("hidden"),s.querySelectorAll(".btn-update-status").forEach(i=>{i.addEventListener("click",t=>{const n=t.target.getAttribute("data-id"),r=t.target.getAttribute("data-status");d.updateTaskStatus(n,r);const o=d.getState().tasks.find(c=>c.id===n);this.showNodeDrawer(o)})})}}class E{constructor(){this.name="AI Monitoring Agent",this.status="Active"}analyzeGraphRisks(){const e=d.getState(),s=e.tasks;e.users;let a=0;const i={};return s.forEach(t=>{t.status!=="done"&&(i[t.assignee]=(i[t.assignee]||0)+1)}),s.forEach(t=>{let n=.1,r=[];const o=i[t.assignee]||0;o>=4&&(n+=.45,r.push(`Assignee ${t.assignee} has ${o} active tasks (Workload overload hazard).`)),t.dependsOn&&t.dependsOn.length>0&&t.dependsOn.forEach(c=>{const l=s.find(p=>p.id===c);l&&(l.status==="blocked"?(n+=.5,r.push(`Prerequisite ${c} is currently BLOCKED.`)):l.aiRiskScore>.6&&(n+=.35,r.push(`Prerequisite ${c} has elevated risk (${Math.round(l.aiRiskScore*100)}%).`)))}),t.priority==="Critical"&&t.status==="blocked"&&(n+=.4,r.push("CRITICAL priority task is in BLOCKED state!")),t.aiRiskScore=Math.min(.99,Number(n.toFixed(2))),t.riskReason=r.length>0?r.join(" "):null,t.aiRiskScore>=.7&&a++}),d.saveState(),{totalTasksAnalyzed:s.length,highRiskCount:a,systemHealthIndex:Math.max(20,Math.round(100-a*18)),summary:`${this.name} scanned ${s.length} live graph nodes. Detected ${a} critical risk bottlenecks.`}}generateProactiveAlerts(){const e=this.analyzeGraphRisks(),s=d.getState();return s.tasks.filter(i=>i.aiRiskScore>=.7).forEach(i=>{s.aiAlerts.find(n=>n.taskId===i.id)||d.addAlert({severity:i.aiRiskScore>.85?"critical":"warning",title:`AI Risk Alert: ${i.id}`,message:i.riskReason||`Elevated risk detected on ${i.title}`,taskId:i.id})}),e}}const b=new E;class T{constructor(e){this.container=document.getElementById(e),this.activeTab="overview"}setTab(e){this.activeTab=e,this.render()}render(){if(!this.container)return;const e=d.getState(),s=e.currentRole;if(this.activeTab==="agents"){this.renderAgentsTab(e);return}if(this.activeTab==="analytics"){this.renderAnalyticsTab(e);return}switch(s){case"employee":this.renderEmployeePortal(e);break;case"team_lead":this.renderTeamLeadPortal(e);break;case"project_manager":this.renderProjectManagerPortal(e);break;case"admin":this.renderAdminPortal(e);break;default:this.renderTeamLeadPortal(e)}}renderEmployeePortal(e){const s=e.tasks.filter(a=>a.assignee===e.currentUser.name);this.container.innerHTML=`
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">MY ACTIVE TASKS</span>
          <span class="stat-card-value">${s.filter(a=>a.status!=="done").length}</span>
          <span class="stat-card-trend up">⚡ High Priority Focus</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">COMPLETED THIS SPRINT</span>
          <span class="stat-card-value">${s.filter(a=>a.status==="done").length}</span>
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
          ${s.length>0?s.map(a=>`
            <div class="task-item-card" data-task-id="${a.id}">
              <div class="task-item-main">
                <span class="task-status-pill ${a.status}">${a.status.replace("_"," ")}</span>
                <div>
                  <div class="task-title">[${a.id}] ${a.title}</div>
                  <div class="task-meta">
                    <span>Project: ${a.project}</span>
                    <span>Due: ${a.dueDate}</span>
                  </div>
                </div>
              </div>
              <button class="btn btn-ghost btn-xs btn-complete-task" data-id="${a.id}">
                ${a.status==="done"?"Completed ✓":"Mark Done"}
              </button>
            </div>
          `).join(""):'<p class="text-muted">No assigned tasks found.</p>'}
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
    `,this.attachEmployeeEvents()}attachEmployeeEvents(){this.container.querySelectorAll(".btn-complete-task").forEach(s=>{s.addEventListener("click",a=>{const i=a.target.getAttribute("data-id");d.updateTaskStatus(i,"done"),this.render()})});const e=this.container.querySelector("#btnSubmitDailyLog");e&&e.addEventListener("click",()=>{const s=this.container.querySelector("#logSuccessMsg");s&&(s.style.display="block",setTimeout(()=>s.style.display="none",3e3))})}renderTeamLeadPortal(e){const s=e.tasks,a=s.filter(t=>t.status==="blocked").length,i=s.filter(t=>t.aiRiskScore>=.7).length;this.container.innerHTML=`
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">ACTIVE SPRINT TASKS</span>
          <span class="stat-card-value">${s.length}</span>
          <span class="stat-card-trend up">65% Overall Completion</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">BLOCKED BOTTLENECKS</span>
          <span class="stat-card-value" style="color: var(--status-blocked);">${a}</span>
          <span class="stat-card-trend warn">⚠️ Requires Lead Approval</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">AI HIGH RISK HALOS</span>
          <span class="stat-card-value" style="color: var(--status-risk);">${i}</span>
          <span class="stat-card-trend warn">🔴 Pulsing on Live Graph</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">👥 Team Member Capacity & Workload Balance</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px;">
          ${e.users.map(t=>`
            <div style="background: var(--bg-card); border: 1px solid ${t.capacity>100?"#EF4444":"var(--border-color)"}; border-radius: 8px; padding: 10px;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600;">
                <span>${t.name} (${t.role})</span>
                <span style="color: ${t.capacity>100?"#EF4444":"var(--cyan-primary)"};">${t.capacity}% Load</span>
              </div>
              <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; margin-top: 6px; overflow: hidden;">
                <div style="width: ${Math.min(100,t.capacity)}%; height: 100%; background: ${t.capacity>100?"#EF4444":"var(--cyan-primary)"};"></div>
              </div>
              <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px;">Assigned Tasks: ${t.activeTasks}</div>
            </div>
          `).join("")}
        </div>
      </div>

      <div>
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">📋 Approvals & Review Queue</h3>
        ${s.filter(t=>t.status==="blocked"||t.priority==="Critical").map(t=>`
          <div class="task-item-card" data-task-id="${t.id}">
            <div class="task-item-main">
              <span class="task-status-pill ${t.status}">${t.status.replace("_"," ")}</span>
              <div>
                <div class="task-title">[${t.id}] ${t.title}</div>
                <div class="task-meta">
                  <span>Owner: ${t.assignee}</span>
                  <span style="color:#EF4444;">${t.riskReason?"Risk: "+t.riskReason:""}</span>
                </div>
              </div>
            </div>
            <button class="btn btn-primary btn-xs btn-unblock-task" data-id="${t.id}">Unblock & Reassign</button>
          </div>
        `).join("")}
      </div>
    `,this.attachTeamLeadEvents()}attachTeamLeadEvents(){this.container.querySelectorAll(".btn-unblock-task").forEach(e=>{e.addEventListener("click",s=>{const a=s.target.getAttribute("data-id");d.updateTaskStatus(a,"in_progress"),this.render()})})}renderProjectManagerPortal(e){this.container.innerHTML=`
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
          <span class="stat-card-value">${e.projects.length}</span>
          <span class="stat-card-trend up">Cloud, Mobile, Security</span>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 10px;">🚀 Sprint Planning & Project Progress</h3>
        ${e.projects.map(s=>`
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700;">
              <span>${s.name}</span>
              <span style="color: var(--cyan-primary);">${s.progress}% Completed</span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Lead: ${s.lead} • Target Deadline: ${s.deadline}</div>
            <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; margin-top: 8px; overflow: hidden;">
              <div style="width: ${s.progress}%; height: 100%; background: linear-gradient(90deg, var(--cyan-primary), var(--purple-primary));"></div>
            </div>
          </div>
        `).join("")}
      </div>

      <div style="background: rgba(127,0,255,0.08); border: 1px solid var(--purple-primary); border-radius: 12px; padding: 16px;">
        <h4 style="font-size: 0.85rem; font-weight: 700; color: #fff; margin-bottom: 6px;">🧠 AI Insights & Delivery Forecast</h4>
        <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">
          The AI Monitoring Agent predicts a 88% likelihood of completing Sprint Alpha ahead of schedule if <strong>TASK-102 (Database Migration)</strong> is unblocked by reassigning secondary subtasks from Devon Reed to Priya Sharma.
        </p>
      </div>
    `}renderAdminPortal(e){const s=e.systemStats;this.container.innerHTML=`
      <div class="dashboard-grid">
        <div class="stat-card">
          <span class="stat-card-title">GRAPH ENGINE NODES</span>
          <span class="stat-card-value">${s.graphNodeCount} Nodes</span>
          <span class="stat-card-trend up">${s.graphEdgeCount} Active Edges</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">AI INFERENCE LATENCY</span>
          <span class="stat-card-value" style="color: var(--cyan-primary);">${s.aiInferenceLatency}</span>
          <span class="stat-card-trend up">⚡ Sub-second response</span>
        </div>
        <div class="stat-card">
          <span class="stat-card-title">SYSTEM MEMORY LOAD</span>
          <span class="stat-card-value">${s.memoryUsage}</span>
          <span class="stat-card-trend">CPU Load: ${s.cpuLoad}</span>
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
              ${e.users.map(a=>`
                <tr style="border-top: 1px solid var(--border-color);">
                  <td style="padding: 10px; font-weight: 600;">${a.name}</td>
                  <td style="padding: 10px; color: var(--cyan-primary);">${a.role}</td>
                  <td style="padding: 10px; color: var(--text-secondary);">Full Read/Write, Live Graph Access</td>
                  <td style="padding: 10px;"><span style="color: var(--status-done);">● Active</span></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </div>
    `}renderAgentsTab(e){const s=b.analyzeGraphRisks();this.container.innerHTML=`
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
          <p style="font-size: 0.825rem; color: var(--text-primary); margin-bottom: 10px;">${s.summary}</p>
          <div style="font-size: 0.75rem; color: var(--cyan-primary);">System Health Score: <strong>${s.systemHealthIndex}%</strong></div>
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
          <p style="font-size: 0.825rem; color: var(--text-primary);">Indexed ${e.tasks.length} tasks, ${e.policies.length} policies, and ${e.users.length} user skills.</p>
        </div>
      </div>
    `}renderAnalyticsTab(e){this.container.innerHTML=`
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px;">
        <h3 style="font-size: 1rem; color: #fff; margin-bottom: 16px;">📊 Live Sprint Analytics & Risk Matrix</h3>
        <canvas id="sprintAnalyticsChart" style="max-height: 260px; width: 100%;"></canvas>
      </div>
    `,setTimeout(()=>{const s=document.getElementById("sprintAnalyticsChart");s&&window.Chart&&new window.Chart(s,{type:"bar",data:{labels:["Done","In Progress","Blocked","High Risk"],datasets:[{label:"Task Count",data:[e.tasks.filter(a=>a.status==="done").length,e.tasks.filter(a=>a.status==="in_progress").length,e.tasks.filter(a=>a.status==="blocked").length,e.tasks.filter(a=>a.aiRiskScore>=.7).length],backgroundColor:["#10B981","#3B82F6","#F59E0B","#EF4444"]}]},options:{responsive:!0,plugins:{legend:{display:!1}},scales:{y:{beginAtZero:!0}}}})},100)}}class ${constructor(){this.name="AI Assistant Agent",this.ollamaUrl="http://localhost:11434/api/generate",this.preferredModel="llama3.2:latest",this.isOllamaAvailable=!1}async checkOllamaConnection(){try{const e=new AbortController,s=setTimeout(()=>e.abort(),1e3),a=await fetch("http://localhost:11434/api/tags",{method:"GET",signal:e.signal});if(clearTimeout(s),a.ok){const i=await a.json();if(i.models&&i.models.length>0){this.isOllamaAvailable=!0;const t=i.models.map(n=>n.name);return t.includes("llama3.2:latest")?this.preferredModel="llama3.2:latest":t.includes("llama3:latest")?this.preferredModel="llama3:latest":t.includes("phi3:mini")?this.preferredModel="phi3:mini":this.preferredModel=t[0],!0}}}catch{}return this.isOllamaAvailable=!1,!1}async processPromptAsync(e){const s=e.trim();if(!s)return{type:"empty",message:"Please enter a valid prompt."};if(await this.checkOllamaConnection())try{const i=await this.queryOllama(s);if(i&&i.trim())return{type:"ollama_llm",message:`🦙 **Ollama LLM (${this.preferredModel})**:

${i}`,model:this.preferredModel}}catch(i){console.warn("Ollama query error, using Smart AI Engine fallback",i)}return this.processSmartRuleEngine(s)}async queryOllama(e){try{const s=new AbortController,a=setTimeout(()=>s.abort(),3500),t=d.getState().tasks.map(o=>`[${o.id}] ${o.title} (Owner: ${o.assignee}, Status: ${o.status})`).join("; "),n={model:this.preferredModel,prompt:`Context: Active Tasks: ${t}.
User Question: ${e}
Answer concisely as Nexus AI Assistant:`,stream:!1},r=await fetch(this.ollamaUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(n),signal:s.signal});if(clearTimeout(a),r.ok)return(await r.json()).response}catch(s){console.warn("Ollama fetch error or CORS timeout",s)}return null}processSmartRuleEngine(e){const s=e.trim().toLowerCase(),a=d.getState();if(s.includes("break down")||s.includes("decompose")||s.includes("subtask")){const n=e.replace(/break down|decompose|subtasks|subtask|for|the/gi,"").trim()||"Selected Component";return this.generateSubtasks(n)}if(s.includes("bandwidth")||s.includes("load")||s.includes("who can take")||s.includes("capacity"))return{type:"workload_report",message:`📊 **Team Workload & Bandwidth Matrix**:

${a.users.map(r=>`• **${r.name}** (${r.role}): ${r.capacity}% capacity load (${r.activeTasks} active tasks)`).join(`
`)}

💡 **AI Recommendation**: Priya Sharma has the lowest load (40%) and is ready for new task assignment!`};if(s.includes("summary")||s.includes("report")||s.includes("status")||s.includes("sprint")){const n=a.tasks.length,r=a.tasks.filter(l=>l.status==="done").length,o=a.tasks.filter(l=>l.status==="blocked").length,c=Math.round(r/n*100);return{type:"sprint_summary",message:`📈 **Sprint Alpha Executive Report**:
• Total Tasks: **${n}**
• Completed: **${r}** (${c}%)
• Blocked Tasks: **${o}**

⚠️ **Critical Bottleneck**: Devon Reed is overloaded at 110% capacity. Unblocking TASK-102 will accelerate 3 dependent milestones!`}}if(s.includes("create task")||s.includes("add task")){const n=e.replace(/create task|add task/gi,"").trim()||"New AI Task",r=d.addTask({title:n,priority:"High",status:"in_progress",assignee:"Priya Sharma"});return{type:"task_created",message:`✅ Created and published task **${r.id}: ${r.title}** assigned to Priya Sharma live on the Task Graph!`}}const i=a.tasks.find(n=>s.includes(n.id.toLowerCase())||s.includes(n.title.toLowerCase())||s.includes(n.id.split("-")[1]));if(i)return{type:"task_info",message:`📋 **Task Details [${i.id}]**:
• **Title**: ${i.title}
• **Assignee**: ${i.assignee}
• **Status**: ${i.status.toUpperCase()}
• **Priority**: ${i.priority}
• **SLA Target**: ${i.dueDate}
${i.riskReason?`⚠️ **Risk Alert**: ${i.riskReason}`:"✓ No risk detected."}`};const t=a.users.find(n=>s.includes(n.name.toLowerCase())||s.includes(n.name.split(" ")[0].toLowerCase()));if(t){const n=a.tasks.filter(r=>r.assignee===t.name);return{type:"user_info",message:`👤 **Team Member: ${t.name}**
• **Role**: ${t.role}
• **Capacity Load**: ${t.capacity}%
• **Active Tasks**: ${n.map(r=>`[${r.id}] ${r.title}`).join(", ")||"None"}`}}return{type:"general_ai",message:`🤖 **Nexus AI Assistant**:
I analyzed your query: "${e}".

💡 **Live Context Analytics**:
• Active Graph Nodes: **${a.tasks.length}**
• High-Risk Hazards: **${a.tasks.filter(n=>n.aiRiskScore>=.7).length}**

Try asking me: *"Break down OAuth feature"*, *"Who has bandwidth?"*, *"Status of TASK-102"*, or *"Generate Sprint Summary"*!`}}generateSubtasks(e){const s=[`1. Draft technical design doc & API contract schema for "${e}"`,"2. Implement backend service endpoints & unit tests","3. Integrate frontend state, error boundaries, & UI components","4. Conduct end-to-end integration tests & security policy audit"];return{type:"subtasks",feature:e,subtasks:s,message:`✨ AI generated 4 subtasks for **"${e}"**:

${s.join(`
`)}`}}}const y=new $;class w{constructor(){this.name="AI Search Agent"}search(e){if(!e||e.trim().length===0)return[];const s=e.trim().toLowerCase(),a=d.getState(),i=[];return a.tasks.forEach(t=>{(t.id.toLowerCase().includes(s)||t.title.toLowerCase().includes(s)||t.assignee.toLowerCase().includes(s)||t.project.toLowerCase().includes(s))&&i.push({type:"Task",id:t.id,title:`[${t.id}] ${t.title}`,subtitle:`Assignee: ${t.assignee} • Status: ${t.status.toUpperCase()} • Priority: ${t.priority}`,badge:"Task Node",data:t})}),a.policies.forEach(t=>{(t.title.toLowerCase().includes(s)||t.category.toLowerCase().includes(s)||t.summary.toLowerCase().includes(s)||t.tags.some(n=>n.toLowerCase().includes(s)))&&i.push({type:"Policy",id:t.title,title:`📄 ${t.title}`,subtitle:`${t.category} Policy: ${t.summary}`,badge:"Doc Vault",data:t})}),a.users.forEach(t=>{(t.name.toLowerCase().includes(s)||t.role.toLowerCase().includes(s))&&i.push({type:"User",id:t.id,title:`👤 ${t.name}`,subtitle:`Role: ${t.role} • Capacity: ${t.capacity}%`,badge:"Team Member",data:t})}),i}}const L=new w;class I{constructor(){this.graphEngine=null,this.rolePortals=null}init(){this.rolePortals=new T("portalTabContent"),this.graphEngine=new A("graphSvg","graphTooltip","nodeDetailDrawer"),this.rolePortals.render(),this.graphEngine.render(),this.graphEngine.startPhysicsLoop(),this.bindThemeToggler(),this.bindRoleSelector(),this.bindTabNavigation(),this.bindSearchEngine(),this.bindAiPromptLauncher(),this.bindTaskModal(),this.bindGraphControls(),this.bindAiRiskScan(),this.bindNotificationsDrawer(),this.bindAutoRebalancer(),this.bindDocumentViewerModal(),d.subscribe(()=>{this.rolePortals.render(),this.graphEngine.render(),this.updateNavbarUser(),this.updateUnreadCount(),this.syncThemeUI()}),this.updateNavbarUser(),this.updateUnreadCount(),this.syncThemeUI(),console.log("🚀 Nexus Mind Platform Initialized successfully!")}bindThemeToggler(){const e=document.getElementById("btnToggleTheme");e&&e.addEventListener("click",()=>{d.toggleTheme(),this.syncThemeUI()})}syncThemeUI(){const s=d.getState().theme||"dark";document.body.className=`theme-${s}`;const a=document.getElementById("themeToggleIcon"),i=document.getElementById("themeToggleText");a&&i&&(a.textContent=s==="dark"?"🌙":"☀️",i.textContent=s==="dark"?"Dark":"Light")}updateNavbarUser(){const e=d.getState(),s=e.currentUser,a=document.getElementById("navUserName"),i=document.getElementById("navUserRole"),t=document.getElementById("navUserAvatar"),n=document.getElementById("portalTitle");a&&(a.textContent=s.name),i&&(i.textContent=s.role),t&&(t.textContent=s.avatar);const r={employee:"👨‍💻 Employee Workspace Portal",team_lead:"👩‍💼 Team Lead Management Portal",project_manager:"📊 Project Manager Sprint Portal",admin:"🛡️ Administrator Organization Portal"};n&&(n.textContent=r[e.currentRole]||"Workspace Portal")}updateUnreadCount(){const e=d.getState(),s=document.getElementById("unreadCount");s&&(s.textContent=e.aiAlerts.length)}bindRoleSelector(){const e=document.getElementById("roleSelect");e&&(e.value=d.getState().currentRole,e.addEventListener("change",s=>{d.setRole(s.target.value)}))}bindTabNavigation(){const e=document.querySelectorAll(".portal-tabs .tab-btn");e.forEach(s=>{s.addEventListener("click",a=>{e.forEach(n=>n.classList.remove("active"));const i=a.currentTarget;i.classList.add("active");const t=i.getAttribute("data-tab");this.rolePortals.setTab(t)})})}bindSearchEngine(){const e=document.getElementById("globalSearchInput"),s=document.getElementById("searchResultsDropdown");!e||!s||(window.addEventListener("keydown",a=>{a.key==="/"&&document.activeElement!==e&&(a.preventDefault(),e.focus())}),e.addEventListener("input",a=>{const i=a.target.value;if(!i.trim()){s.classList.add("hidden");return}const t=L.search(i);t.length===0?s.innerHTML='<div style="padding:10px; font-size:0.8rem; color:var(--text-muted);">No matching items found.</div>':s.innerHTML=t.map(n=>`
          <div class="search-item" data-id="${n.id}" data-type="${n.type}">
            <div>
              <div class="search-item-title">${n.title}</div>
              <div style="font-size:0.725rem; color:var(--text-secondary);">${n.subtitle}</div>
            </div>
            <span class="search-item-tag">${n.badge}</span>
          </div>
        `).join(""),s.classList.remove("hidden")}),s.addEventListener("click",a=>{const i=a.target.closest(".search-item");if(i){const t=i.getAttribute("data-id"),n=i.getAttribute("data-type");if(s.classList.add("hidden"),n==="Task"){const r=d.getState().tasks.find(o=>o.id===t);r&&this.graphEngine.showNodeDrawer(r)}else if(n==="Policy"){const r=d.getState().policies.find(o=>o.title===t);r&&this.openDocModal(r)}}}),document.addEventListener("click",a=>{!e.contains(a.target)&&!s.contains(a.target)&&s.classList.add("hidden")}))}bindAiPromptLauncher(){const e=document.getElementById("aiPromptForm"),s=document.getElementById("aiPromptInput"),a=document.getElementById("aiChatModal"),i=document.getElementById("chatMessages"),t=document.getElementById("btnCloseChatModal"),n=document.getElementById("chatInput"),r=document.getElementById("btnSendChat"),o=async c=>{if(!c.trim()||!i)return;const l=document.createElement("div");l.className="chat-message user",l.innerHTML=`<div class="msg-bubble">${c}</div>`,i.appendChild(l);const p=document.createElement("div");p.className="chat-message assistant",p.innerHTML=`
        <div class="msg-avatar">💡</div>
        <div class="msg-bubble"><em>🤖 Nexus AI analyzing...</em></div>
      `,i.appendChild(p),i.scrollTop=i.scrollHeight,a&&a.classList.remove("hidden");try{const u=await y.processPromptAsync(c),g=p.querySelector(".msg-bubble");g&&u&&u.message&&(g.innerHTML=u.message.replace(/\n/g,"<br/>"))}catch{const g=p.querySelector(".msg-bubble");if(g){const h=y.processSmartRuleEngine(c);g.innerHTML=h.message.replace(/\n/g,"<br/>")}}i.scrollTop=i.scrollHeight};e&&s&&e.addEventListener("submit",c=>{c.preventDefault();const l=s.value;s.value="",o(l)}),r&&n&&(r.addEventListener("click",()=>{const c=n.value;n.value="",o(c)}),n.addEventListener("keydown",c=>{if(c.key==="Enter"){const l=n.value;n.value="",o(l)}})),t&&a&&t.addEventListener("click",()=>{a.classList.add("hidden")})}bindTaskModal(){const e=document.getElementById("taskModal"),s=document.getElementById("btnCreateTaskModal"),a=document.getElementById("btnCloseTaskModal"),i=document.getElementById("btnCancelTaskModal"),t=document.getElementById("taskForm"),n=document.getElementById("taskDependencySelect"),r=document.getElementById("btnGenerateAiSubtasks"),o=document.getElementById("aiSubtasksPreview");if(!e)return;const c=()=>{if(!n)return;const p=d.getState().tasks;n.innerHTML='<option value="">None (Standalone)</option>'+p.map(u=>`<option value="${u.id}">[${u.id}] ${u.title}</option>`).join("")};s&&s.addEventListener("click",()=>{c(),e.classList.remove("hidden")});const l=()=>e.classList.add("hidden");a&&a.addEventListener("click",l),i&&i.addEventListener("click",l),r&&r.addEventListener("click",()=>{const p=document.getElementById("taskTitleInput").value||"New Component",u=y.generateSubtasks(p);o.innerHTML=u.subtasks.map(g=>`<div style="margin-top:4px;">${g}</div>`).join("")}),t&&t.addEventListener("submit",p=>{p.preventDefault();const u=document.getElementById("taskTitleInput").value,g=document.getElementById("taskAssigneeSelect").value,h=document.getElementById("taskPrioritySelect").value,k=document.getElementById("taskProjectSelect").value,S=document.getElementById("taskDependencySelect").value;d.addTask({title:u,assignee:g,priority:h,project:k,dependsOn:S}),l(),t.reset()})}bindGraphControls(){var a,i,t,n;const e=document.querySelectorAll(".graph-filter-btn");e.forEach(r=>{r.addEventListener("click",o=>{e.forEach(l=>l.classList.remove("active")),o.currentTarget.classList.add("active");const c=o.currentTarget.getAttribute("data-filter");this.graphEngine.setFilter(c)})}),(a=document.getElementById("btnGraphReset"))==null||a.addEventListener("click",()=>this.graphEngine.resetView()),(i=document.getElementById("btnGraphZoomIn"))==null||i.addEventListener("click",()=>this.graphEngine.zoomIn()),(t=document.getElementById("btnGraphZoomOut"))==null||t.addEventListener("click",()=>this.graphEngine.zoomOut());const s=document.getElementById("btnTogglePhysics");s&&s.addEventListener("click",()=>{const r=this.graphEngine.togglePhysics();s.querySelector("span").textContent=`Physics: ${r?"ON":"OFF"}`}),(n=document.getElementById("btnCloseNodeDrawer"))==null||n.addEventListener("click",()=>{var r;(r=document.getElementById("nodeDetailDrawer"))==null||r.classList.add("hidden")})}bindAiRiskScan(){var t;const e=document.getElementById("btnRunAiScan"),s=document.getElementById("aiAlertsBanner"),a=document.getElementById("alertText"),i=document.getElementById("btnCloseAlert");e&&e.addEventListener("click",()=>{e.disabled=!0,e.innerHTML="<span>Scanning Graph...</span>",setTimeout(()=>{const n=b.generateProactiveAlerts();e.disabled=!1,e.innerHTML=`
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            <span>Run AI Risk Scan</span>
          `,s&&a&&(a.textContent=n.summary,s.classList.remove("hidden"))},600)}),i&&s&&i.addEventListener("click",()=>s.classList.add("hidden")),(t=document.getElementById("btnViewRiskDetails"))==null||t.addEventListener("click",()=>{this.graphEngine.setFilter("risk")})}bindNotificationsDrawer(){const e=document.getElementById("btnNotifications"),s=document.getElementById("notificationsDrawer"),a=document.getElementById("btnCloseNotifications"),i=document.getElementById("notificationsList");!e||!s||(e.addEventListener("click",()=>{const t=d.getState();i&&(i.innerHTML=t.aiAlerts.map(n=>`
          <div class="notification-card ${n.severity}">
            <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.825rem;">
              <span>${n.severity==="critical"?"🔴":"⚠️"} ${n.title}</span>
              <span style="font-size:0.65rem; color:var(--text-muted);">${n.timestamp}</span>
            </div>
            <p style="font-size:0.775rem; color:var(--text-secondary); margin-top:4px; line-height:1.4;">${n.message}</p>
          </div>
        `).join("")),s.classList.toggle("hidden")}),a&&a.addEventListener("click",()=>s.classList.add("hidden")))}bindAutoRebalancer(){const e=document.getElementById("btnAutoRebalanceNav");e&&e.addEventListener("click",()=>{d.autoRebalanceWorkload()&&(e.style.background="rgba(16, 185, 129, 0.2)",e.style.color="#10B981",e.innerHTML="✓ Rebalanced!",setTimeout(()=>{e.style.background="",e.style.color="",e.innerHTML="⚡ AI Rebalance"},3e3))})}bindDocumentViewerModal(){const e=document.getElementById("docViewerModal"),s=document.getElementById("btnCloseDocModal");s&&e&&s.addEventListener("click",()=>e.classList.add("hidden"))}openDocModal(e){const s=document.getElementById("docViewerModal"),a=document.getElementById("docModalTitle"),i=document.getElementById("docModalBody");s&&a&&i&&(a.textContent=`📄 ${e.title}`,i.innerHTML=`
        <div style="display:flex; gap:8px; margin-bottom:12px;">
          <span class="search-item-tag">${e.category}</span>
          ${e.tags.map(t=>`<span style="font-size:0.7rem; background:rgba(0,0,0,0.06); padding:2px 8px; border-radius:10px; color:var(--text-secondary);">#${t}</span>`).join("")}
        </div>
        <div style="background:rgba(0,0,0,0.04); border:1px solid var(--border-color); padding:14px; border-radius:10px; font-size:0.875rem;">
          ${e.summary}
        </div>
      `,s.classList.remove("hidden"))}}document.addEventListener("DOMContentLoaded",()=>{new I().init()});
