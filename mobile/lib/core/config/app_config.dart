class AppConfig {
  static const String appName = 'Nexus Mind Enterprise';
  static const String appVersion = '2.0.0';
  
  // Production URL default with dart-define environment variable override
  static const String productionApiUrl = 'https://nexus-mind-qv03.onrender.com';
  static const String defaultApiUrl = String.fromEnvironment('API_BASE_URL', defaultValue: productionApiUrl);
  
  static const bool demoMode = bool.fromEnvironment('DEMO_MODE', defaultValue: false);

  static String get baseUrl => defaultApiUrl;
  static String get wsUrl => defaultApiUrl.startsWith('https')
      ? defaultApiUrl.replaceFirst('https', 'wss')
      : defaultApiUrl.replaceFirst('http', 'ws');
}
