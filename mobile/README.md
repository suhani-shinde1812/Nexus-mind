# Nexus Mind Mobile (Flutter)

Scoped-down companion app hitting the same FastAPI backend as the web app:
task list + status updates, live alerts (WebSocket), and Firebase Cloud
Messaging push notifications.

## Setup

```bash
flutter pub get

# Point the app at your backend (defaults to http://10.0.2.2:8000, i.e.
# localhost:8000 as seen from the Android emulator):
flutter run --dart-define=NEXUS_API_BASE_URL=https://your-api.example.com
```

## Enabling push notifications (Firebase Cloud Messaging)

1. Create a Firebase project and add Android/iOS apps to it.
2. Download `google-services.json` into `android/app/` and
   `GoogleService-Info.plist` into `ios/Runner/`.
3. Run `flutterfire configure` to generate `lib/firebase_options.dart`.
4. Uncomment the Firebase init + `PushService` lines in `lib/main.dart`.
5. Set `FCM_SERVER_KEY` in the backend's `.env` (legacy FCM HTTP API key,
   from Project Settings -> Cloud Messaging in the Firebase console).

## What's scoped down vs. the web app

- Live task **graph** (force-directed canvas) isn't reproduced natively —
  the mobile app shows the same tasks as a flat, sortable list instead.
- Reassignment / meeting scheduling / AI decomposition UIs are not
  included; the mobile scope here is "view + update status + get
  notified," per the brief. All of those endpoints already exist on the
  backend, so adding screens for them is additive, not a backend change.
