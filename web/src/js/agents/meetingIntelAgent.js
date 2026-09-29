/**
 * NEXUS MIND — MEETING INTELLIGENCE AGENT
 * Real-time WebRTC meeting transcription using the Web Speech API +
 * NLP action-item extraction engine.
 *
 * Capabilities:
 *  - Live speech-to-text transcription during Jitsi meetings
 *  - NLP pattern matching for action items ("X will do Y", "we need to", etc.)
 *  - Assignee + deadline suggestion from live team member list
 *  - End-of-meeting summary with one-click task insertion into the Live Graph
 */
import { store } from '../state.js';
import { api } from '../api.js';

// NLP patterns to detect action items
const ACTION_PATTERNS = [
  /(\w[\w\s]+?)\s+will\s+(.+?)(?:\.|$)/gi,
  /action item[:\s]+(.+?)(?:\.|$)/gi,
  /(\w[\w\s]+?)\s+(?:needs to|has to|should)\s+(.+?)(?:\.|$)/gi,
  /(?:we|team)\s+(?:need to|have to|will)\s+(.+?)(?:\.|$)/gi,
  /(?:todo|to-do|follow.?up)[:\s]+(.+?)(?:\.|$)/gi,
  /(\w[\w\s]+?)\s+is\s+responsible\s+for\s+(.+?)(?:\.|$)/gi,
];

export class MeetingIntelAgent {
  constructor() {
    this._recognition = null;
    this._isRecording = false;
    this._transcript = [];         // [{time, speaker, text}]
    this._actionItems = [];        // [{id, text, assignee, deadline, confidence}]
    this._onTranscriptUpdate = null;
    this._onActionItemsUpdate = null;
    this._meetingTitle = '';
    this._startTime = null;
  }

  get isSupported() {
    return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
  }

  get isRecording() { return this._isRecording; }
  get transcript() { return this._transcript; }
  get actionItems() { return this._actionItems; }

  onTranscriptUpdate(cb) { this._onTranscriptUpdate = cb; }
  onActionItemsUpdate(cb) { this._onActionItemsUpdate = cb; }

  /** Start live transcription for a meeting. */
  startTranscription(meetingTitle = 'Team Meeting') {
    if (!this.isSupported) {
      console.warn('Web Speech API not supported in this browser.');
      return false;
    }
    if (this._isRecording) return true;

    this._meetingTitle = meetingTitle;
    this._startTime = new Date();
    this._transcript = [];
    this._actionItems = [];

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    this._recognition = new SR();
    this._recognition.continuous = true;
    this._recognition.interimResults = true;
    this._recognition.lang = 'en-US';
    this._recognition.maxAlternatives = 1;

    this._recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          const text = result[0].transcript.trim();
          if (text.length < 3) continue;

          const entry = {
            id: Date.now(),
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            text,
            isFinal: true,
          };
          this._transcript.push(entry);

          // NLP action item extraction
          this._extractActionItems(text);

          if (this._onTranscriptUpdate) this._onTranscriptUpdate([...this._transcript]);
        }
      }
    };

    this._recognition.onerror = (e) => {
      if (e.error !== 'no-speech') console.warn('Speech recognition error:', e.error);
    };

    this._recognition.onend = () => {
      // Auto-restart unless explicitly stopped
      if (this._isRecording) {
        try { this._recognition.start(); } catch {}
      }
    };

    this._recognition.start();
    this._isRecording = true;
    return true;
  }

  /** Stop transcription and return final summary. */
  stopTranscription() {
    this._isRecording = false;
    if (this._recognition) {
      try { this._recognition.stop(); } catch {}
      this._recognition = null;
    }
    return this._buildMeetingSummary();
  }

  /** Simulate transcription (for demo mode / testing). */
  simulateTranscription(meetingTitle = 'Sprint Planning') {
    this._meetingTitle = meetingTitle;
    this._startTime = new Date();
    this._transcript = [];
    this._actionItems = [];
    this._isRecording = true;  // Set BEFORE scheduling timeouts to avoid race condition

    const DEMO_LINES = [
      { delay: 500, text: 'Alright everyone, let\'s kick off the sprint planning meeting.' },
      { delay: 2000, text: 'Sarah will complete the OAuth2 integration by end of this week.' },
      { delay: 3500, text: 'Action item: Devon needs to fix the WebSocket reconnect bug before Thursday.' },
      { delay: 5000, text: 'We need to review the API rate limiting policy with the security team.' },
      { delay: 6500, text: 'Alex is responsible for updating the Docker compose configuration.' },
      { delay: 8000, text: 'Follow-up: schedule a performance test for the graph engine with Marcus.' },
      { delay: 9500, text: 'Jordan will do the mobile build and submit to App Store review.' },
      { delay: 11000, text: 'Todo: update the README with the new deployment steps.' },
      { delay: 13000, text: 'Great, I think we have a solid plan. Let\'s wrap up.' },
    ];

    const lastDelay = DEMO_LINES[DEMO_LINES.length - 1].delay;

    DEMO_LINES.forEach(({ delay, text }) => {
      setTimeout(() => {
        if (!this._isRecording) return;
        const entry = {
          id: Date.now() + delay,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text,
          isFinal: true,
        };
        this._transcript.push(entry);
        this._extractActionItems(text);
        if (this._onTranscriptUpdate) this._onTranscriptUpdate([...this._transcript]);
      }, delay);
    });

    // Auto-stop after all demo lines have played — resets UI button state
    setTimeout(() => {
      if (this._isRecording) {
        this._isRecording = false;
        // Notify UI that demo has finished so button can revert
        if (this._onTranscriptUpdate) this._onTranscriptUpdate([...this._transcript]);
      }
    }, lastDelay + 800);
  }

  // ─────────────────────────────────────────────────────────
  // NLP Action Item Extraction
  // ─────────────────────────────────────────────────────────
  _extractActionItems(text) {
    const state = store.getState();
    const teamNames = (state.users || []).map(u => u.name?.split(' ')[0]?.toLowerCase());

    ACTION_PATTERNS.forEach((pattern, pi) => {
      pattern.lastIndex = 0;
      let match;
      while ((match = pattern.exec(text)) !== null) {
        const raw = match[0].trim();
        if (raw.length < 10) continue;

        // Extract who (first captured group for person-specific patterns)
        let assigneeName = null;
        if (pi < 3 && match[1]) {
          const candidate = match[1].trim().toLowerCase();
          const found = teamNames.find(n => candidate.includes(n));
          if (found) {
            const user = (state.users || []).find(u => u.name?.toLowerCase().startsWith(found));
            if (user) assigneeName = user.name;
          }
        }

        // Auto-suggest deadline from sprint (7 days default)
        const suggestedDeadline = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);

        const item = {
          id: `ai-${Date.now()}-${pi}`,
          text: raw.length > 120 ? raw.slice(0, 120) + '...' : raw,
          rawText: raw,
          assignee: assigneeName,
          deadline: suggestedDeadline,
          confidence: pi === 0 ? 0.92 : pi <= 2 ? 0.87 : 0.75,
          inserted: false,
        };

        // Deduplicate by text similarity
        const isDuplicate = this._actionItems.some(existing =>
          this._similarity(existing.rawText, item.rawText) > 0.75
        );
        if (!isDuplicate) {
          this._actionItems.push(item);
          if (this._onActionItemsUpdate) this._onActionItemsUpdate([...this._actionItems]);
        }
      }
    });
  }

  _similarity(a, b) {
    const aW = new Set(a.toLowerCase().split(/\s+/));
    const bW = b.toLowerCase().split(/\s+/);
    const matches = bW.filter(w => aW.has(w)).length;
    return matches / Math.max(aW.size, bW.length);
  }

  // ─────────────────────────────────────────────────────────
  // Task Insertion
  // ─────────────────────────────────────────────────────────
  async insertActionItemAsTask(itemId) {
    const item = this._actionItems.find(i => i.id === itemId);
    if (!item || item.inserted) return;

    const state = store.getState();
    const project = state.projects?.[0]?.name || 'General';

    try {
      await api.createTask({
        title: item.rawText.slice(0, 80),
        description: `Extracted from meeting: "${this._meetingTitle}" on ${this._startTime?.toLocaleDateString()}`,
        assignee: item.assignee || null,
        project,
        priority: 'medium',
        status: 'todo',
        due_date: item.deadline,
      });

      item.inserted = true;
      if (this._onActionItemsUpdate) this._onActionItemsUpdate([...this._actionItems]);

      store.addToast('Task Inserted', `"${item.rawText.slice(0, 50)}..." added to Live Graph`, 'success');
      await store.init(); // refresh graph
    } catch (err) {
      store.addToast('Insert Failed', err.message, 'critical');
    }
  }

  /** Insert all un-inserted action items at once. */
  async insertAllActionItems() {
    const pending = this._actionItems.filter(i => !i.inserted);
    for (const item of pending) {
      await this.insertActionItemAsTask(item.id);
    }
  }

  // ─────────────────────────────────────────────────────────
  // Meeting Summary
  // ─────────────────────────────────────────────────────────
  _buildMeetingSummary() {
    const duration = this._startTime
      ? Math.round((Date.now() - this._startTime.getTime()) / 60000)
      : 0;

    return {
      title: this._meetingTitle,
      date: this._startTime?.toLocaleDateString() || new Date().toLocaleDateString(),
      duration: `${duration} min`,
      transcript: [...this._transcript],
      actionItems: [...this._actionItems],
      summary: `Meeting "${this._meetingTitle}" lasted ${duration} minutes. ` +
        `${this._transcript.length} utterances recorded. ` +
        `${this._actionItems.length} action item(s) extracted.`,
    };
  }
}

export const meetingIntelAgent = new MeetingIntelAgent();
