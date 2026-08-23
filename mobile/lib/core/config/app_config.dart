class AppConfig {
  static const String appName = 'Nexus Mind Enterprise';
  static const String appVersion = '2.0.0';
  
  // Default to localhost for Android emulator / desktop / web
  static const String defaultApiUrl = 'http://10.0.2.2:8000'; // Android emulator
  static const String desktopApiUrl = 'http://127.0.0.1:8000'; // Desktop / Web / iOS simulator
  
  static const bool demoMode = bool.fromEnvironment('DEMO_MODE', defaultValue: true);

  static String get baseUrl => desktopApiUrl;
  static String get wsUrl => desktopApiUrl.replaceAll('http', 'ws');
}

