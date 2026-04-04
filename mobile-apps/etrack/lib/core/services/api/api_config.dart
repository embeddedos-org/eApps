import 'package:shared_preferences/shared_preferences.dart';
import '../../constants/app_constants.dart';

class ApiConfig {
  static Future<String?> getUspsUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.keyUspsUserId);
  }

  static Future<void> setUspsUserId(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyUspsUserId, value);
  }

  static Future<String?> getFedexClientId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.keyFedexClientId);
  }

  static Future<void> setFedexClientId(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyFedexClientId, value);
  }

  static Future<String?> getFedexClientSecret() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.keyFedexClientSecret);
  }

  static Future<void> setFedexClientSecret(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyFedexClientSecret, value);
  }

  static Future<String?> getUpsClientId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.keyUpsClientId);
  }

  static Future<void> setUpsClientId(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyUpsClientId, value);
  }

  static Future<String?> getUpsClientSecret() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.keyUpsClientSecret);
  }

  static Future<void> setUpsClientSecret(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyUpsClientSecret, value);
  }

  static Future<String?> getAviationStackKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.keyAviationStackKey);
  }

  static Future<void> setAviationStackKey(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyAviationStackKey, value);
  }

  static Future<bool> hasApiKey(String carrier) async {
    switch (carrier.toUpperCase()) {
      case 'USPS':
        return (await getUspsUserId())?.isNotEmpty ?? false;
      case 'FEDEX':
        return (await getFedexClientId())?.isNotEmpty ?? false;
      case 'UPS':
        return (await getUpsClientId())?.isNotEmpty ?? false;
      case 'AVIATIONSTACK':
        return (await getAviationStackKey())?.isNotEmpty ?? false;
      default:
        return false;
    }
  }
}
