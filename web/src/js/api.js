/**
 * NEXUS MIND - API CLIENT
 * High-performance fetch/axios-style wrapper around FastAPI backend.
 * Provides resilient fallback for standalone / demo mode.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_BASE_URL || API_BASE.replace(/^http/, 'ws');
const TOKEN_KEY = 'NEXUS_MIND_AUTH_TOKENS_V1';

class ApiClient {
  constructor() {
    this._tokens = this._loadTokens();
  }

  _loadTokens() {
    try {
      const raw = localStorage.getItem(TOKEN_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  _saveTokens(tokens) {
    this._tokens = tokens;
    localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  }

  clearTokens() {
    this._tokens = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  get isAuthenticated() {
    return !!this._tokens?.access_token;
  }

  get accessToken() {
    return this._tokens?.access_token || null;
  }

  get wsUrl() {
    return `${WS_BASE}/ws?token=${encodeURIComponent(this.accessToken || '')}`;
  }

  async _request(path, { method = 'GET', body, auth = true, form = false } = {}) {
    const headers = {};
    if (!form) headers['Content-Type'] = 'application/json';
    if (auth && this.accessToken) headers['Authorization'] = `Bearer ${this.accessToken}`;

    let res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: form ? body : body ? JSON.stringify(body) : undefined,
    });

    // Transparent refresh-on-401, one retry.
    if (res.status === 401 && auth && this._tokens?.refresh_token && path !== '/api/auth/refresh') {
      const refreshed = await this._tryRefresh();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
        res = await fetch(`${API_BASE}${path}`, {
          method,
          headers,
          body: form ? body : body ? JSON.stringify(body) : undefined,
        });
      }
    }

    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detail.detail || `Request failed: ${res.status}`);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  async _tryRefresh() {
    try {
      const tokens = await this._request('/api/auth/refresh', {
        method: 'POST',
        body: { refresh_token: this._tokens.refresh_token },
        auth: false,
      });
      this._saveTokens(tokens);
      return true;
    } catch {
      this.clearTokens();
      return false;
    }
  }

  // ---- Auth & MFA ----
  async login(email, password) {
    const form = new URLSearchParams();
    form.set('username', email);
    form.set('password', password);
    const tokens = await this._request('/api/auth/login', { method: 'POST', body: form, auth: false, form: true });
    if (!tokens.mfa_required) {
      this._saveTokens(tokens);
    }
    return tokens;
  }

  async register(payload) {
    const tokens = await this._request('/api/auth/register', { method: 'POST', body: payload, auth: false });
    this._saveTokens(tokens);
    return tokens;
  }

  setupMfa() {
    return this._request('/api/auth/mfa/setup', { method: 'POST' });
  }

  enableMfa(secret, code) {
    return this._request('/api/auth/mfa/enable', { method: 'POST', body: { secret, code } });
  }

  async verifyMfa(tempToken, code) {
    const tokens = await this._request('/api/auth/mfa/verify', { method: 'POST', body: { temp_token: tempToken, code }, auth: false });
    this._saveTokens(tokens);
    return tokens;
  }

  getSessions() {
    return this._request('/api/auth/sessions');
  }

  revokeSession(sessionId) {
    return this._request(`/api/auth/sessions/${sessionId}`, { method: 'DELETE' });
  }

  me() {
    return this._request('/api/auth/me');
  }

  // ---- Bootstrap ----
  bootstrap() {
    return this._request('/api/bootstrap');
  }

  // ---- Tasks & Comments ----
  createTask(payload) {
    return this._request('/api/tasks', { method: 'POST', body: payload });
  }
  updateTaskStatus(taskId, status) {
    return this._request(`/api/tasks/${taskId}/status`, { method: 'PATCH', body: { status } });
  }
  updateTaskDeadline(taskId, dueDate) {
    return this._request(`/api/tasks/${taskId}/deadline`, { method: 'PATCH', body: { dueDate } });
  }
  reassignTask(taskId, assignee) {
    return this._request(`/api/tasks/${taskId}/reassign`, { method: 'POST', body: { assignee } });
  }
  updateTaskPosition(taskId, x, y) {
    return this._request(`/api/tasks/${taskId}/position`, { method: 'PATCH', body: { x, y } });
  }
  addDependency(taskId, depId) {
    return this._request(`/api/tasks/${taskId}/dependency/${depId}`, { method: 'POST' });
  }
  removeDependency(taskId, depId) {
    return this._request(`/api/tasks/${taskId}/dependency/${depId}`, { method: 'DELETE' });
  }
  deleteTask(taskId) {
    return this._request(`/api/tasks/${taskId}`, { method: 'DELETE' });
  }
  getReassignmentCandidates(taskId) {
    return this._request(`/api/tasks/${taskId}/reassignment-candidates`);
  }
  rescanRisk(taskId) {
    return this._request(`/api/tasks/${taskId}/rescan-risk`, { method: 'POST' });
  }
  getTaskComments(taskId) {
    return this._request(`/api/tasks/${taskId}/comments`);
  }
  addTaskComment(taskId, content) {
    return this._request(`/api/tasks/${taskId}/comments`, { method: 'POST', body: { content } });
  }

  // ---- Multi-Agent AI Swarm & Simulations ----
  queryAgentSwarm(query) {
    return this._request('/api/ai/query', { method: 'POST', body: { query } });
  }
  decompose(payload) {
    return this._request('/api/ai/decompose', { method: 'POST', body: payload });
  }
  decomposeAndApply(taskId) {
    return this._request(`/api/ai/decompose/${taskId}/apply`, { method: 'POST' });
  }
  forecastSprint() {
    return this._request('/api/ai/forecast', { method: 'POST' });
  }
  getRebalancePlan() {
    return this._request('/api/ai/rebalance', { method: 'POST' });
  }
  simulateScenario(scenario) {
    return this._request('/api/simulation/what-if', { method: 'POST', body: scenario });
  }
  getTaskMlRisk(taskId) {
    return this._request(`/api/simulation/risk/${taskId}`);
  }

  // ---- RAG Knowledge Base ----
  getDocuments() {
    return this._request('/api/documents');
  }
  queryRag(query, top_k = 3) {
    return this._request('/api/documents/query', { method: 'POST', body: { query, top_k } });
  }

  // ---- Cybersecurity Center ----
  getThreatRadar() {
    return this._request('/api/security/threat-radar');
  }
  getSecurityEvents() {
    return this._request('/api/security/events');
  }
  getAuditLogs(limit = 50) {
    return this._request(`/api/audit/logs?limit=${limit}`);
  }

  // ---- Engineering Intelligence ----
  getGithubMetrics() {
    return this._request('/api/integrations/github/metrics');
  }

  // ---- Meetings ----
  createMeeting(payload) {
    return this._request('/api/meetings', { method: 'POST', body: payload });
  }
  cancelMeeting(meetingId) {
    return this._request(`/api/meetings/${meetingId}/cancel`, { method: 'POST' });
  }

  // ---- Alerts ----
  createAlert(payload) {
    return this._request('/api/alerts', { method: 'POST', body: payload });
  }

  // ---- Push ----
  registerPushToken(token, platform = 'web') {
    return this._request(`/api/users/me/push-token?token=${encodeURIComponent(token)}&platform=${platform}`, {
      method: 'POST',
    });
  }

  // ---- AI Evaluation Center ----
  getEvaluationSummary() {
    return this._request('/api/evaluation/summary');
  }
}

export const api = new ApiClient();
