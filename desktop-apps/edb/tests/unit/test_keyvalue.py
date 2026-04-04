"""Unit tests for the key-value store."""

import time

from edb.core.keyvalue import KeyValueStore


def test_set_and_get(engine):
    kv = KeyValueStore(engine)
    kv.set("name", "Alice")

    assert kv.get("name") == "Alice"


def test_get_nonexistent(engine):
    kv = KeyValueStore(engine)
    assert kv.get("nonexistent") is None


def test_set_overwrites(engine):
    kv = KeyValueStore(engine)
    kv.set("key", "value1")
    kv.set("key", "value2")

    assert kv.get("key") == "value2"


def test_delete(engine):
    kv = KeyValueStore(engine)
    kv.set("key", "value")
    assert kv.delete("key") is True
    assert kv.get("key") is None


def test_delete_nonexistent(engine):
    kv = KeyValueStore(engine)
    assert kv.delete("nonexistent") is False


def test_exists(engine):
    kv = KeyValueStore(engine)
    kv.set("key", "value")

    assert kv.exists("key") is True
    assert kv.exists("nonexistent") is False


def test_list_keys(engine):
    kv = KeyValueStore(engine)
    kv.set("user:1", "Alice")
    kv.set("user:2", "Bob")
    kv.set("config:theme", "dark")

    all_keys = kv.list_keys()
    assert len(all_keys) == 3

    user_keys = kv.list_keys(prefix="user:")
    assert len(user_keys) == 2


def test_json_values(engine):
    kv = KeyValueStore(engine)
    kv.set("config", {"theme": "dark", "lang": "en"})

    value = kv.get("config")
    assert value == {"theme": "dark", "lang": "en"}


def test_list_values(engine):
    kv = KeyValueStore(engine)
    kv.set("tags", ["python", "database", "nosql"])

    value = kv.get("tags")
    assert value == ["python", "database", "nosql"]


def test_numeric_values(engine):
    kv = KeyValueStore(engine)
    kv.set("count", 42)
    kv.set("ratio", 3.14)

    assert kv.get("count") == 42
    assert kv.get("ratio") == 3.14


def test_ttl_expiration(engine):
    kv = KeyValueStore(engine)
    entry = kv.set("temp", "value", ttl=1)

    assert entry.expires_at is not None
    assert kv.get("temp") == "value"

    time.sleep(1.5)
    assert kv.get("temp") is None


def test_count(engine):
    kv = KeyValueStore(engine)
    kv.set("a", 1)
    kv.set("b", 2)
    kv.set("c", 3)

    assert kv.count() == 3


def test_get_many(engine):
    kv = KeyValueStore(engine)
    kv.set("a", 1)
    kv.set("b", 2)
    kv.set("c", 3)

    result = kv.get_many(["a", "c", "missing"])
    assert result == {"a": 1, "c": 3}


def test_set_many(engine):
    kv = KeyValueStore(engine)
    entries = kv.set_many({"x": 10, "y": 20, "z": 30})

    assert len(entries) == 3
    assert kv.get("x") == 10
    assert kv.get("y") == 20
    assert kv.get("z") == 30
