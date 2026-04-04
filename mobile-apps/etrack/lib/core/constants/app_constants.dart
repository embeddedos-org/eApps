class AppConstants {
  AppConstants._();

  // Routes
  static const String dashboardRoute = '/';
  static const String addTrackingRoute = '/add';
  static const String trackingDetailRoute = '/detail/:id';
  static const String settingsRoute = '/settings';

  // API Endpoints
  static const String uspsApiUrl =
      'https://production.shippingapis.com/ShippingAPI.dll';
  static const String fedexAuthUrl =
      'https://apis.fedex.com/oauth/token';
  static const String fedexTrackUrl =
      'https://apis.fedex.com/track/v1/trackingnumbers';
  static const String upsAuthUrl =
      'https://onlinetools.ups.com/security/v1/oauth/token';
  static const String upsTrackUrl =
      'https://onlinetools.ups.com/api/track/v1/details';
  static const String aviationStackUrl =
      'https://api.aviationstack.com/v1/flights';

  // SharedPreferences Keys
  static const String keyUspsUserId = 'api_key_usps_user_id';
  static const String keyFedexClientId = 'api_key_fedex_client_id';
  static const String keyFedexClientSecret = 'api_key_fedex_client_secret';
  static const String keyUpsClientId = 'api_key_ups_client_id';
  static const String keyUpsClientSecret = 'api_key_ups_client_secret';
  static const String keyAviationStackKey = 'api_key_aviationstack';
  static const String keyThemeMode = 'theme_mode';
  static const String keyNotificationsEnabled = 'notifications_enabled';

  // Supported carriers for display
  static const List<String> supportedCarriers = [
    'USPS', 'FedEx', 'UPS', 'DHL',
    'India Post', 'Australia Post', 'Canada Post', 'Royal Mail',
  ];
}
