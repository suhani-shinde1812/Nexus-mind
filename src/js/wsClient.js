/**
 * NEXUS MIND - REALTIME WEBSOCKET CLIENT
 * Connects to the FastAPI /ws endpoint (Redis-pub/sub backed on the server)
 * and forwards events to the store so every open tab/user sees live
 * updates to the task graph, alerts, and meetings without polling.
 */
import { api } from './api.js';

class WsClient {
  constructor() {
    this._socket = null;
    this._handlers = new Map(); // eventType -> Set<fn>
    this._reconnectTimer = null;
    this._reconnectAttempts = 0;
    this._manuallyClosed = false;
  }

  get isConnected() {
    return this._socket?.readyState === WebSocket.OPEN;
  }

  on(eventType, handler) {
    if (!this._handlers.has(eventType)) this._handlers.set(eventType, new Set());
    this._handlers.get(eventType).add(handler);
    return () => this._handlers.get(eventType)?.delete(handler);
  }

  connect() {
    if (!api.isAuthenticated) return;
    this._manuallyClosed = false;
    this._reconnectAttempts = 0;
    this._open();
  }

  disconnect() {
    this._manuallyClosed = true;
    clearTimeout(this._reconnectTimer);
    if (this._socket) {
      try {
        this._socket.close();
      } catch {}
      this._socket = null;
    }
  }

  _open() {
    if (!api.isAuthenticated || this._manuallyClosed) return;
    clearTimeout(this._reconnectTimer);

    try {
      const url = api.wsUrl;
      console.log(`[WS] Connecting to ${url.split('?')[0]}...`);
      this._socket = new WebSocket(url);
    } catch (e) {
      console.error('[WS] Connection failed to initialize:', e);
      this._scheduleReconnect();
      return;
    }

    this._socket.onopen = () => {
      console.log('✅ [WS] Real-time WebSocket Connected');
      const wasReconnected = this._reconnectAttempts > 0;
      this._reconnectAttempts = 0;
      const handlers = this._handlers.get('connected');
      if (handlers) handlers.forEach(fn => fn({ reconnected: wasReconnected }));
    };

    this._socket.onmessage = (event) => {
      let msg;
      try {
        msg = JSON.parse(event.data);
      } catch {
        return;
      }

      const eventType = msg.type;
      const payload = msg.payload !== undefined ? msg.payload : msg;

      // Dispatch specific event handlers (both exact and lowercase/uppercase aliases)
      const handlers = this._handlers.get(eventType);
      if (handlers) handlers.forEach((fn) => fn(payload));

      const lowerHandlers = this._handlers.get(eventType.toLowerCase());
      if (lowerHandlers && lowerHandlers !== handlers) lowerHandlers.forEach((fn) => fn(payload));

      const upperHandlers = this._handlers.get(eventType.toUpperCase());
      if (upperHandlers && upperHandlers !== handlers) upperHandlers.forEach((fn) => fn(payload));

      const wildcard = this._handlers.get('*');
      if (wildcard) wildcard.forEach((fn) => fn(msg));
    };

    this._socket.onclose = (event) => {
      console.log(`[WS] Socket disconnected (Code: ${event.code})`);
      const handlers = this._handlers.get('disconnected');
      if (handlers) handlers.forEach(fn => fn(event));

      if (this._manuallyClosed) return;
      this._scheduleReconnect();
    };

    this._socket.onerror = (err) => {
      console.warn('[WS] Socket error event:', err);
      try {
        this._socket?.close();
      } catch {}
    };
  }

  _scheduleReconnect() {
    if (this._manuallyClosed) return;
    this._reconnectAttempts++;
    // Exponential backoff: 1.5s, 3s, 6s, 12s, max 20s
    const delay = Math.min(1500 * Math.pow(1.5, this._reconnectAttempts - 1), 20000);
    console.log(`[WS] Scheduling reconnect attempt #${this._reconnectAttempts} in ${Math.round(delay)}ms...`);
    clearTimeout(this._reconnectTimer);
    this._reconnectTimer = setTimeout(() => {
      this._open();
    }, delay);
  }
}

export const wsClient = new WsClient();
