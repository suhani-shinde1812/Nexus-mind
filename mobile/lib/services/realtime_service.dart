/// Nexus Mind Mobile - realtime WebSocket client.
/// Same protocol as web/src/js/wsClient.js: connects to /ws?token=...,
/// receives {"type": ..., "payload": ...} events fanned out via Redis
/// pub/sub on the server, and re-broadcasts them to in-app listeners.
import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

import 'api_service.dart';

class RealtimeService {
  RealtimeService(this._api);

  final ApiService _api;
  WebSocketChannel? _channel;
  final _controller = StreamController<Map<String, dynamic>>.broadcast();
  Timer? _reconnectTimer;
  bool _manuallyClosed = false;

  Stream<Map<String, dynamic>> get events => _controller.stream;

  void connect() {
    if (!_api.isAuthenticated) return;
    _manuallyClosed = false;
    _open();
  }

  void disconnect() {
    _manuallyClosed = true;
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
  }

  void _open() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(_api.wsUrl));
      _channel!.stream.listen(
        (raw) {
          try {
            final msg = jsonDecode(raw as String) as Map<String, dynamic>;
            _controller.add(msg);
          } catch (_) {}
        },
        onDone: _scheduleReconnect,
        onError: (_) => _scheduleReconnect(),
      );
    } catch (_) {
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    if (_manuallyClosed) return;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), _open);
  }
}
