"""Unit tests for full-text search."""

from edb.core.fts import FullTextSearch


def test_create_and_list_indexes(engine):
    fts = FullTextSearch(engine)
    fts.create_index("articles", ["title", "body"])

    indexes = fts.list_indexes()
    assert "articles" in indexes


def test_index_and_search(engine):
    fts = FullTextSearch(engine)
    fts.create_index("articles", ["title", "body"])

    fts.index_document(
        "articles", "1",
        {"title": "Python Programming", "body": "Learn Python basics"},
    )
    fts.index_document(
        "articles", "2",
        {"title": "Database Design", "body": "SQL and NoSQL patterns"},
    )
    fts.index_document(
        "articles", "3",
        {"title": "Python Advanced", "body": "Async and concurrency"},
    )

    results = fts.search("articles", "Python")
    assert len(results) == 2


def test_search_no_results(engine):
    fts = FullTextSearch(engine)
    fts.create_index("articles", ["title"])
    fts.index_document("articles", "1", {"title": "Hello World"})

    results = fts.search("articles", "nonexistent")
    assert len(results) == 0


def test_search_nonexistent_index(engine):
    fts = FullTextSearch(engine)
    results = fts.search("missing_index", "query")
    assert results == []


def test_drop_index(engine):
    fts = FullTextSearch(engine)
    fts.create_index("temp", ["content"])
    assert "temp" in fts.list_indexes()

    fts.drop_index("temp")
    assert "temp" not in fts.list_indexes()
