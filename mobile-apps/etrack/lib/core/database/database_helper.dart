import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/tracking_item.dart';
import '../models/tracking_event.dart';
import '../models/reminder.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('etrack.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);
    return await openDatabase(path, version: 1, onCreate: _createDB);
  }

  Future<void> _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE tracking_items (
        id TEXT PRIMARY KEY,
        tracking_number TEXT NOT NULL,
        carrier TEXT NOT NULL,
        tracking_type TEXT NOT NULL,
        label TEXT DEFAULT '',
        status TEXT DEFAULT 'unknown',
        status_explanation TEXT DEFAULT '',
        estimated_delivery TEXT,
        tags TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        last_refreshed TEXT
      )
    ''');

    await db.execute('''
      CREATE TABLE tracking_events (
        id TEXT PRIMARY KEY,
        tracking_item_id TEXT NOT NULL,
        status TEXT NOT NULL,
        status_explanation TEXT DEFAULT '',
        location TEXT DEFAULT '',
        description TEXT DEFAULT '',
        timestamp TEXT NOT NULL,
        FOREIGN KEY (tracking_item_id) REFERENCES tracking_items (id) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE reminders (
        id TEXT PRIMARY KEY,
        tracking_item_id TEXT NOT NULL,
        scheduled_time TEXT NOT NULL,
        message TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (tracking_item_id) REFERENCES tracking_items (id) ON DELETE CASCADE
      )
    ''');

    await db.execute(
      'CREATE INDEX idx_events_item ON tracking_events (tracking_item_id)',
    );
    await db.execute(
      'CREATE INDEX idx_reminders_item ON reminders (tracking_item_id)',
    );
  }

  // --- Tracking Items CRUD ---

  Future<void> insertTrackingItem(TrackingItem item) async {
    final db = await database;
    await db.insert('tracking_items', item.toMap(),
        conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<void> updateTrackingItem(TrackingItem item) async {
    final db = await database;
    await db.update('tracking_items', item.toMap(),
        where: 'id = ?', whereArgs: [item.id]);
  }

  Future<void> deleteTrackingItem(String id) async {
    final db = await database;
    await db.delete('tracking_events',
        where: 'tracking_item_id = ?', whereArgs: [id]);
    await db.delete('reminders',
        where: 'tracking_item_id = ?', whereArgs: [id]);
    await db.delete('tracking_items', where: 'id = ?', whereArgs: [id]);
  }

  Future<List<TrackingItem>> getAllTrackingItems() async {
    final db = await database;
    final itemMaps = await db.query('tracking_items', orderBy: 'created_at DESC');
    final items = <TrackingItem>[];
    for (final map in itemMaps) {
      final eventMaps = await db.query('tracking_events',
          where: 'tracking_item_id = ?',
          whereArgs: [map['id']],
          orderBy: 'timestamp DESC');
      final events = eventMaps.map((e) => TrackingEvent.fromMap(e)).toList();
      items.add(TrackingItem.fromMap(map, events: events));
    }
    return items;
  }

  Future<TrackingItem?> getTrackingItemById(String id) async {
    final db = await database;
    final maps = await db.query('tracking_items', where: 'id = ?', whereArgs: [id]);
    if (maps.isEmpty) return null;
    final eventMaps = await db.query('tracking_events',
        where: 'tracking_item_id = ?', whereArgs: [id], orderBy: 'timestamp DESC');
    final events = eventMaps.map((e) => TrackingEvent.fromMap(e)).toList();
    return TrackingItem.fromMap(maps.first, events: events);
  }

  Future<List<TrackingItem>> searchTrackingItems(String query) async {
    final db = await database;
    final maps = await db.query('tracking_items',
        where: 'tracking_number LIKE ? OR label LIKE ?',
        whereArgs: ['%$query%', '%$query%'],
        orderBy: 'created_at DESC');
    final items = <TrackingItem>[];
    for (final map in maps) {
      final eventMaps = await db.query('tracking_events',
          where: 'tracking_item_id = ?',
          whereArgs: [map['id']],
          orderBy: 'timestamp DESC');
      final events = eventMaps.map((e) => TrackingEvent.fromMap(e)).toList();
      items.add(TrackingItem.fromMap(map, events: events));
    }
    return items;
  }

  // --- Tracking Events CRUD ---

  Future<void> insertTrackingEvent(TrackingEvent event) async {
    final db = await database;
    await db.insert('tracking_events', event.toMap(),
        conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<void> insertTrackingEvents(List<TrackingEvent> events) async {
    final db = await database;
    final batch = db.batch();
    for (final event in events) {
      batch.insert('tracking_events', event.toMap(),
          conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  Future<void> deleteEventsForItem(String trackingItemId) async {
    final db = await database;
    await db.delete('tracking_events',
        where: 'tracking_item_id = ?', whereArgs: [trackingItemId]);
  }

  Future<List<TrackingEvent>> getEventsForItem(String trackingItemId) async {
    final db = await database;
    final maps = await db.query('tracking_events',
        where: 'tracking_item_id = ?',
        whereArgs: [trackingItemId],
        orderBy: 'timestamp DESC');
    return maps.map((e) => TrackingEvent.fromMap(e)).toList();
  }

  // --- Reminders CRUD ---

  Future<void> insertReminder(Reminder reminder) async {
    final db = await database;
    await db.insert('reminders', reminder.toMap(),
        conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<void> updateReminder(Reminder reminder) async {
    final db = await database;
    await db.update('reminders', reminder.toMap(),
        where: 'id = ?', whereArgs: [reminder.id]);
  }

  Future<void> deleteReminder(String id) async {
    final db = await database;
    await db.delete('reminders', where: 'id = ?', whereArgs: [id]);
  }

  Future<List<Reminder>> getRemindersForItem(String trackingItemId) async {
    final db = await database;
    final maps = await db.query('reminders',
        where: 'tracking_item_id = ?', whereArgs: [trackingItemId]);
    return maps.map((r) => Reminder.fromMap(r)).toList();
  }

  Future<List<Reminder>> getActiveReminders() async {
    final db = await database;
    final maps = await db.query('reminders', where: 'is_active = 1');
    return maps.map((r) => Reminder.fromMap(r)).toList();
  }

  Future<void> close() async {
    final db = await database;
    db.close();
    _database = null;
  }
}
