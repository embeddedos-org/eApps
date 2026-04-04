class Validators {
  Validators._();

  static String? trackingNumber(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Tracking number is required';
    }
    if (value.trim().length < 4) {
      return 'Tracking number is too short';
    }
    return null;
  }

  static String? label(String? value) {
    if (value != null && value.length > 100) {
      return 'Label must be under 100 characters';
    }
    return null;
  }

  static String? apiKey(String? value) {
    if (value != null && value.isNotEmpty && value.length < 5) {
      return 'API key seems too short';
    }
    return null;
  }
}
