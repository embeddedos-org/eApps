import 'package:flutter/material.dart';

enum TrackingType {
  package('Package', Icons.local_shipping),
  flight('Flight', Icons.flight),
  immigrationCase('Immigration Case', Icons.gavel);

  const TrackingType(this.label, this.icon);
  final String label;
  final IconData icon;
}

enum TrackingStatus {
  unknown('Unknown'),
  pending('Pending'),
  preTransit('Pre-Transit'),
  inTransit('In Transit'),
  outForDelivery('Out for Delivery'),
  delivered('Delivered'),
  failed('Failed'),
  delayed('Delayed'),
  returned('Returned'),
  availableForPickup('Available for Pickup');

  const TrackingStatus(this.label);
  final String label;

  Color get color {
    switch (this) {
      case TrackingStatus.delivered:
      case TrackingStatus.availableForPickup:
        return const Color(0xFF4CAF50);
      case TrackingStatus.inTransit:
      case TrackingStatus.outForDelivery:
        return const Color(0xFF2962FF);
      case TrackingStatus.pending:
      case TrackingStatus.preTransit:
        return const Color(0xFFFF9800);
      case TrackingStatus.failed:
      case TrackingStatus.returned:
        return const Color(0xFFF44336);
      case TrackingStatus.delayed:
        return const Color(0xFFFF5722);
      case TrackingStatus.unknown:
        return const Color(0xFF9E9E9E);
    }
  }

  String get emoji {
    switch (this) {
      case TrackingStatus.delivered:
        return '✅';
      case TrackingStatus.inTransit:
        return '🚚';
      case TrackingStatus.outForDelivery:
        return '📦';
      case TrackingStatus.pending:
      case TrackingStatus.preTransit:
        return '⏳';
      case TrackingStatus.failed:
        return '❌';
      case TrackingStatus.delayed:
        return '⚠️';
      case TrackingStatus.returned:
        return '↩️';
      case TrackingStatus.availableForPickup:
        return '📬';
      case TrackingStatus.unknown:
        return '❓';
    }
  }
}

enum TrackingTag {
  important('Important', Color(0xFFE91E63)),
  delayed('Delayed', Color(0xFFFF5722)),
  delivered('Delivered', Color(0xFF4CAF50));

  const TrackingTag(this.label, this.color);
  final String label;
  final Color color;
}

enum Carrier {
  usps('USPS', 'United States Postal Service', Icons.local_post_office),
  ups('UPS', 'United Parcel Service', Icons.local_shipping),
  fedex('FedEx', 'Federal Express', Icons.flight),
  dhl('DHL', 'DHL Express', Icons.public),
  indiaPost('India Post', 'India Post', Icons.mail),
  australiaPost('Australia Post', 'Australia Post', Icons.mail_outline),
  canadaPost('Canada Post', 'Canada Post', Icons.markunread_mailbox),
  royalMail('Royal Mail', 'Royal Mail', Icons.mail),
  uscis('USCIS', 'U.S. Citizenship and Immigration Services', Icons.gavel),
  airline('Airline', 'Airline Flight', Icons.flight_takeoff),
  other('Other', 'Other Carrier', Icons.help_outline);

  const Carrier(this.label, this.fullName, this.icon);
  final String label;
  final String fullName;
  final IconData icon;
}
