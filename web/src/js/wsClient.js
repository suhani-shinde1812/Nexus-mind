/**
 * NEXUS MIND - REALTIME WEBSOCKET CLIENT
 * Connects to the FastAPI /ws endpoint (Redis-pub/sub backed on the server)
 * and forwards events to the store so every open tab/user sees live
 * updates to the task graph, alerts, and meetings without polling.
 */
import { api } from './api.js';

const RECONNECT_DELAY_MS = 2500;

class WsClient {
  constructor() {
    this._socket = null;
    this._handlers = new Map(); // eventType -> Set<fn>
    this._reconnectTimer = null;
    this._manuallyClosed = false;
  }

  on(eventType, handler) {
    if (!this._handlers.has(eventType)) this._handlers.set(eventType, new Set());
    this._handlers.get(eventType).add(handler);
    return () => this._handlers.get(eventType)?.delete(handler);
  }

  connect() {
    if (!api.isAuthenticated) return;
    this._manuallyClosed = false;
    this._open();
  }

  disconnect() {
    this._manuallyClosed = true;
    clearTimeout(this._reconnectTimer);
    this._socket?.close();
    this._socket = null;
  }

  _open() {
    try {
      this._socket = new WebSocket(api.wsUrl);
    } catch (e) {
      console.error('WebSocket connection failed', e);
      return;
    }

    this._socket.onmessage = (event) => {
      let msg;
      try {
        msg = JSON.parse(event.data);
      } catch {
        return;
      }
      const handlers = this._handlers.get(msg.type);
      if (handlers) handlers.forEach((fn) => fn(msg.payload));
      const wildcard = this._handlers.get('*');
      if (wildcard) wildcard.forEach((fn) => fn(msg));
    };

    this._socket.onclose = () => {
      if (this._manuallyClosed) return;
      this._reconnectTimer = setTimeout(() => this._open(), RECONNECT_DELAY_MS);
    };

    this._socket.onerror = () => {
      this._socket?.close();
    };
  }
}

export const wsClient = new WsClient();
