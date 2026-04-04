"""Unit tests for the document (NoSQL/JSON) store."""

from edb.core.document import DocumentStore


def test_create_and_list_collections(engine):
    store = DocumentStore(engine)
    store.create_collection("users")
    store.create_collection("logs")

    collections = store.list_collections()
    assert "users" in collections
    assert "logs" in collections


def test_insert_document(engine):
    store = DocumentStore(engine)
    doc = store.insert("users", {"name": "Alice", "age": 30})

    assert doc.id is not None
    assert doc.data["name"] == "Alice"
    assert doc.created_at is not None


def test_insert_with_custom_id(engine):
    store = DocumentStore(engine)
    doc = store.insert("users", {"name": "Bob"}, doc_id="custom-123")

    assert doc.id == "custom-123"


def test_find_by_id(engine):
    store = DocumentStore(engine)
    inserted = store.insert("users", {"name": "Alice", "email": "alice@test.com"})

    found = store.find_by_id("users", inserted.id)
    assert found is not None
    assert found.data["name"] == "Alice"
    assert found.data["email"] == "alice@test.com"


def test_find_by_id_not_found(engine):
    store = DocumentStore(engine)
    store.create_collection("users")

    found = store.find_by_id("users", "nonexistent")
    assert found is None


def test_find_with_filter(engine):
    store = DocumentStore(engine)
    store.insert("users", {"name": "Alice", "role": "admin"})
    store.insert("users", {"name": "Bob", "role": "user"})
    store.insert("users", {"name": "Charlie", "role": "user"})

    results = store.find("users", filter_dict={"role": "user"})
    assert len(results) == 2


def test_find_all(engine):
    store = DocumentStore(engine)
    store.insert("logs", {"event": "login"})
    store.insert("logs", {"event": "logout"})

    results = store.find("logs")
    assert len(results) == 2


def test_find_with_limit(engine):
    store = DocumentStore(engine)
    for i in range(10):
        store.insert("items", {"index": i})

    results = store.find("items", limit=3)
    assert len(results) == 3


def test_update_merge(engine):
    store = DocumentStore(engine)
    doc = store.insert("users", {"name": "Alice", "age": 30, "city": "NYC"})

    updated = store.update("users", doc.id, {"age": 31}, merge=True)
    assert updated is not None
    assert updated.data["age"] == 31
    assert updated.data["name"] == "Alice"
    assert updated.data["city"] == "NYC"


def test_update_replace(engine):
    store = DocumentStore(engine)
    doc = store.insert("users", {"name": "Alice", "age": 30, "city": "NYC"})

    updated = store.update("users", doc.id, {"name": "Alicia"}, merge=False)
    assert updated is not None
    assert updated.data["name"] == "Alicia"
    assert "age" not in updated.data


def test_delete_document(engine):
    store = DocumentStore(engine)
    doc = store.insert("users", {"name": "Alice"})

    deleted = store.delete("users", doc.id)
    assert deleted is True

    found = store.find_by_id("users", doc.id)
    assert found is None


def test_delete_nonexistent(engine):
    store = DocumentStore(engine)
    store.create_collection("users")

    deleted = store.delete("users", "nonexistent")
    assert deleted is False


def test_count(engine):
    store = DocumentStore(engine)
    store.insert("logs", {"event": "a"})
    store.insert("logs", {"event": "b"})
    store.insert("logs", {"event": "a"})

    assert store.count("logs") == 3
    assert store.count("logs", filter_dict={"event": "a"}) == 2


def test_insert_many(engine):
    store = DocumentStore(engine)
    docs = [{"name": f"user_{i}"} for i in range(5)]
    results = store.insert_many("users", docs)

    assert len(results) == 5
    assert store.count("users") == 5


def test_drop_collection(engine):
    store = DocumentStore(engine)
    store.insert("temp", {"data": "test"})
    assert "temp" in store.list_collections()

    store.drop_collection("temp")
    assert "temp" not in store.list_collections()
