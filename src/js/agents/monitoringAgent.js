/**
 * AI MONITORING AGENT
 * Single Source of Truth analysis over Live Task Graph:
 * Progress tracking, bottleneck detection, Monte Carlo sprint forecast trigger, and proactive alerting.
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
      if (task.status === 'done') {
        task.aiRiskScore = 0.05;
        task.riskReason = null;
        return;
      }

      let riskScore = 0.15;
      let reasons = [];

      // Reason A: Overloaded Assignee
      const activeCount = userTaskCount[task.assignee] || 0;
      const assigneeUser = users.find(u => u.name === task.assignee);
      if (activeCount >= 4 || (assigneeUser && assigneeUser.capacity > 95)) {
        riskScore += 0.45;
        reasons.push(`Assignee ${task.assignee} has ${activeCount} active tasks (${assigneeUser ? assigneeUser.capacity : 100}% workload).`);
      }

      // Reason B: Prerequisite Risk Propagation
      if (task.dependsOn && task.dependsOn.length > 0) {
        task.dependsOn.forEach(depId => {
          const depTask = tasks.find(t => t.id === depId);
          if (depTask) {
            if (depTask.status === 'blocked') {
              riskScore += 0.5;
              reasons.push(`Prerequisite [${depId}] is currently BLOCKED.`);
            } else if (depTask.aiRiskScore > 0.6) {
              riskScore += 0.35;
              reasons.push(`Prerequisite [${depId}] has elevated risk (${Math.round(depTask.aiRiskScore * 100)}%).`);
            }
          }
        });
      }

      // Reason C: Priority vs Status
      if (task.priority === 'Critical' && task.status === 'blocked') {
        riskScore += 0.4;
        reasons.push('CRITICAL priority task is in BLOCKED state!');
      }

      // Reason D: Deadline proximity
      if (task.dueDate) {
        const daysLeft = Math.ceil((new Date(task.dueDate) - new Date()) / (1000 * 60 * 60 * 24));
        if (daysLeft < 0) {
          riskScore += 0.3;
          reasons.push('Task is PAST target SLA due date!');
        } else if (daysLeft <= 2) {
          riskScore += 0.2;
          reasons.push(`Approaching target SLA deadline (${daysLeft} day left).`);
        }
      }

      task.aiRiskScore = Math.min(0.99, Number(riskScore.toFixed(2)));
      task.riskReason = reasons.length > 0 ? reasons.join(' ') : null;

      if (task.aiRiskScore >= 0.7) {
        newRisksFound++;
      }
    });

    // Run Monte Carlo Forecast Simulation
    store.runMonteCarloForecast();
    store.logSwarmActivity(this.name, 'Graph Anomaly Scan', `Scanned ${tasks.length} live nodes. Identified ${newRisksFound} risk bottlenecks. Health: ${Math.max(20, Math.round(100 - (newRisksFound * 18)))}%.`);
    store.saveState();

    return {
      totalTasksAnalyzed: tasks.length,
      highRiskCount: newRisksFound,
      systemHealthIndex: Math.max(20, Math.round(100 - (newRisksFound * 18))),
      summary: `${this.name} scanned ${tasks.length} live graph nodes. Detected ${newRisksFound} critical risk bottlenecks across active projects.`
    };
  }

  /**
   * Auto-generate proactive risk alerts
   */
  generateProactiveAlerts() {
    const analysis = this.analyzeGraphRisks();
    const state = store.getState();

    const highRiskTasks = state.tasks.filter(t => t.aiRiskScore >= 0.7 && t.status !== 'done');

    highRiskTasks.forEach(task => {
      const existingAlert = state.aiAlerts.find(a => a.taskId === task.id);
      if (!existingAlert) {
        store.addAlert({
          severity: task.aiRiskScore > 0.85 ? 'critical' : 'warning',
          title: `⚠️ AI SLA Alert: ${task.id}`,
          message: `${task.title} has elevated risk (${Math.round(task.aiRiskScore * 100)}%). ${task.riskReason || 'Requires team lead intervention.'}`,
          taskId: task.id
        });
      }
    });

    return analysis;
  }
}

export const monitoringAgent = new AiMonitoringAgent();
