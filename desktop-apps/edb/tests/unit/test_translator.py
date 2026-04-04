"""Unit tests for the NL query translator."""

from edb.ebot.translator import NLQueryTranslator


def test_translate_show_all():
    t = NLQueryTranslator()
    result = t.translate("show all users")

    assert result.translated_query is not None
    assert result.translated_query["type"] == "sql"
    assert result.translated_query["action"] == "select"
    assert result.translated_query["table"] == "users"
    assert result.confidence > 0


def test_translate_count():
    t = NLQueryTranslator()
    result = t.translate("count orders")

    assert result.translated_query is not None
    assert result.translated_query["action"] == "count"


def test_translate_list_tables():
    t = NLQueryTranslator()
    result = t.translate("list tables")

    assert result.translated_query is not None
    assert result.confidence == 0.9


def test_translate_list_collections():
    t = NLQueryTranslator()
    result = t.translate("list collections")

    assert result.translated_query is not None
    assert result.translated_query["action"] == "list_collections"


def test_translate_list_keys():
    t = NLQueryTranslator()
    result = t.translate("list keys")

    assert result.translated_query is not None
    assert result.translated_query["type"] == "kv"
    assert result.translated_query["action"] == "list"


def test_translate_unknown():
    t = NLQueryTranslator()
    result = t.translate("quantum flux capacitor")

    assert result.error is not None
    assert result.translated_query is None


def test_translate_empty():
    t = NLQueryTranslator()
    result = t.translate("")

    assert result.error == "Empty query"


def test_translate_delete():
    t = NLQueryTranslator()
    result = t.translate("delete from users where id=5")

    assert result.translated_query is not None
    assert result.translated_query["action"] == "delete"
    assert result.translated_query["table"] == "users"
