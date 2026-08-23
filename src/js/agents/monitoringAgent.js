/**
 * AI MONITORING AGENT
 * Architecture Role: Track Progress, Detect Risks, High-Risk Halos, Send Proactive Alerts
 * Single Source of Truth analysis over Live Task Graph.
 */

import { store } from '../state.js';

export class AiMonitoringAgent {
  constructor() {
    this.name = 'AI Monitoring Agent';
    this.status = 'Active';
  }

  /**
   * Run deep risk analysis across all nodes in the Live Task Graph
   */
  analyzeGraphRisks() {
    const state = store.getState();
    const tasks = state.tasks;
    const users = state.users;
    let newRisksFound = 0;

    // 1. Calculate workload per assignee
    const userTaskCount = {};
    tasks.forEach(t => {
      if (t.status !== 'done') {
        userTaskCount[t.assignee] = (userTaskCount[t.assignee] || 0) + 1;
      }
    });

    // 2. Evaluate risk score for each task
    tasks.forEach(task => {
      let riskScore = 0.1;
      let reasons = [];

      // Reason A: Overloaded Assignee
      const activeCount = userTaskCount[task.assignee] || 0;
      if (activeCount >= 4) {
        riskScore += 0.45;
        reasons.push(`Assignee ${task.assignee} has ${activeCount} active tasks (Workload overload hazard).`);
      }

      // Reason B: Prerequisite Risk Propagation
      if (task.dependsOn && task.dependsOn.length > 0) {
        task.dependsOn.forEach(depId => {
          const depTask = tasks.find(t => t.id === depId);
          if (depTask) {
            if (depTask.status === 'blocked') {
              riskScore += 0.5;
              reasons.push(`Prerequisite ${depId} is currently BLOCKED.`);
            } else if (depTask.aiRiskScore > 0.6) {
              riskScore += 0.35;
              reasons.push(`Prerequisite ${depId} has elevated risk (${Math.round(depTask.aiRiskScore * 100)}%).`);
            }
          }
        });
      }

      // Reason C: Priority vs Status
      if (task.priority === 'Critical' && task.status === 'blocked') {
        riskScore += 0.4;
        reasons.push('CRITICAL priority task is in BLOCKED state!');
      }

      // Cap at 0.99
      task.aiRiskScore = Math.min(0.99, Number(riskScore.toFixed(2)));
      task.riskReason = reasons.length > 0 ? reasons.join(' ') : null;

      if (task.aiRiskScore >= 0.7) {
        newRisksFound++;
      }
    });

    // Update state store
    store.saveState();

    // Return detailed diagnostic report
    return {
      totalTasksAnalyzed: tasks.length,
      highRiskCount: newRisksFound,
      systemHealthIndex: Math.max(20, Math.round(100 - (newRisksFound * 18))),
      summary: `${this.name} scanned ${tasks.length} live graph nodes. Detected ${newRisksFound} critical risk bottlenecks.`
    };
  }

  /**
   * Auto-generate proactive risk alerts
   */
  generateProactiveAlerts() {
    const analysis = this.analyzeGraphRisks();
    const state = store.getState();

    const highRiskTasks = state.tasks.filter(t => t.aiRiskScore >= 0.7);

    highRiskTasks.forEach(task => {
      const existingAlert = state.aiAlerts.find(a => a.taskId === task.id);
      if (!existingAlert) {
        store.addAlert({
          severity: task.aiRiskScore > 0.85 ? 'critical' : 'warning',
          title: `AI Risk Alert: ${task.id}`,
          message: task.riskReason || `Elevated risk detected on ${task.title}`,
          taskId: task.id
        });
      }
    });

    return analysis;
  }
}

export const monitoringAgent = new AiMonitoringAgent();
