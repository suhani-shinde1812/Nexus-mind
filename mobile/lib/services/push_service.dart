/// Nexus Mind Mobile - Firebase Cloud Messaging push notifications.
///
/// Requires a Firebase project wired up per platform:
///   - android/app/google-services.json  (from Firebase console)
///   - ios/Runner/GoogleService-Info.plist
/// and `flutterfire configure` run once to generate firebase_options.dart.
/// This file intentionally has no hard Firebase project reference baked in
/// -- it's environment config, not app code.
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import 'api_service.dart';

class PushService {
  PushService(this._api);

  final ApiService _api;
  final _localNotifications = FlutterLocalNotificationsPlugin();

  Future<void> init() async {
    final messaging = FirebaseMessaging.instance;
    await messaging.requestPermission(alert: true, badge: true, sound: true);

    const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
    const initSettings = InitializationSettings(android: androidInit);
    await _localNotifications.initialize(initSettings);

    final token = await messaging.getToken();
    if (token != null && _api.isAuthenticated) {
      await _api.registerPushToken(token);
    }
    messaging.onTokenRefresh.listen((newToken) {
      if (_api.isAuthenticated) _api.registerPushToken(newToken);
    });

    // Foreground push -> show a local notification (FCM does this
    // automatically in background/terminated states on Android/iOS).
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      final notification = message.notification;
      if (notification == null) return;
      _localNotifications.show(
        notification.hashCode,
        notification.title,
        notification.body,
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'nexus_mind_default',
            'Nexus Mind Alerts',
            importance: Importance.high,
            priority: Priority.high,
          ),
        ),
      );
    });
  }
}
