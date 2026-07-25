/**
 * AI SEARCH AGENT
 * Architecture Role: Search Tasks, Docs, People, Policies, Contextual Results
 */

import { store } from '../state.js';

export class AiSearchAgent {
  constructor() {
    this.name = 'AI Search Agent';
  }

  /**
   * Execute hybrid search across tasks, policies, users, and projects
   */
  search(query) {
    if (!query || query.trim().length === 0) return [];
    
    const q = query.trim().toLowerCase();
    const state = store.getState();
    const results = [];

    // 1. Search Tasks
    state.tasks.forEach(t => {
      if (
        t.id.toLowerCase().includes(q) ||
        t.title.toLowerCase().includes(q) ||
        t.assignee.toLowerCase().includes(q) ||
        t.project.toLowerCase().includes(q)
      ) {
        results.push({
          type: 'Task',
          id: t.id,
          title: `[${t.id}] ${t.title}`,
          subtitle: `Assignee: ${t.assignee} • Status: ${t.status.toUpperCase()} • Priority: ${t.priority}`,
          badge: 'Task Node',
          data: t
        });
      }
    });

    // 2. Search Policies & Knowledge Base
    state.policies.forEach(p => {
      if (
        p.title.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q) ||
        p.summary.toLowerCase().includes(q) ||
        p.tags.some(tag => tag.toLowerCase().includes(q))
      ) {
        results.push({
          type: 'Policy',
          id: p.title,
          title: `📄 ${p.title}`,
          subtitle: `${p.category} Policy: ${p.summary}`,
          badge: 'Doc Vault',
          data: p
        });
      }
    });

    // 3. Search People / Users
    state.users.forEach(u => {
      if (
        u.name.toLowerCase().includes(q) ||
        u.role.toLowerCase().includes(q)
      ) {
        results.push({
          type: 'User',
          id: u.id,
          title: `👤 ${u.name}`,
          subtitle: `Role: ${u.role} • Capacity: ${u.capacity}%`,
          badge: 'Team Member',
          data: u
        });
      }
    });

    return results;
  }
}

export const searchAgent = new AiSearchAgent();
