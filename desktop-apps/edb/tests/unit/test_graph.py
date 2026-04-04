"""Unit tests for the graph store."""

from edb.core.graph import GraphStore


def test_add_and_get_node(engine):
    g = GraphStore(engine)
    node = g.add_node("Person", {"name": "Alice"}, node_id="n1")
    assert node["id"] == "n1"
    assert node["label"] == "Person"

    found = g.get_node("n1")
    assert found is not None
    assert found["properties"]["name"] == "Alice"


def test_find_nodes_by_label(engine):
    g = GraphStore(engine)
    g.add_node("Person", {"name": "Alice"})
    g.add_node("Person", {"name": "Bob"})
    g.add_node("City", {"name": "NYC"})

    people = g.find_nodes(label="Person")
    assert len(people) == 2

    cities = g.find_nodes(label="City")
    assert len(cities) == 1


def test_delete_node(engine):
    g = GraphStore(engine)
    g.add_node("Person", {"name": "Alice"}, node_id="n1")
    assert g.delete_node("n1") is True
    assert g.get_node("n1") is None


def test_add_and_get_edges(engine):
    g = GraphStore(engine)
    g.add_node("Person", {"name": "Alice"}, node_id="n1")
    g.add_node("Person", {"name": "Bob"}, node_id="n2")
    edge = g.add_edge("n1", "n2", "FRIENDS_WITH", {"since": 2020})

    assert edge["relationship"] == "FRIENDS_WITH"

    edges = g.get_edges("n1", direction="out")
    assert len(edges) == 1
    assert edges[0]["target_id"] == "n2"


def test_edge_directions(engine):
    g = GraphStore(engine)
    g.add_node("A", node_id="a")
    g.add_node("B", node_id="b")
    g.add_edge("a", "b", "LINKS_TO")

    assert len(g.get_edges("a", direction="out")) == 1
    assert len(g.get_edges("a", direction="in")) == 0
    assert len(g.get_edges("b", direction="in")) == 1
    assert len(g.get_edges("a", direction="both")) == 1


def test_delete_node_removes_edges(engine):
    g = GraphStore(engine)
    g.add_node("A", node_id="a")
    g.add_node("B", node_id="b")
    g.add_edge("a", "b", "LINKS")

    g.delete_node("a")
    assert g.edge_count() == 0


def test_traverse(engine):
    g = GraphStore(engine)
    g.add_node("A", node_id="a")
    g.add_node("B", node_id="b")
    g.add_node("C", node_id="c")
    g.add_edge("a", "b", "NEXT")
    g.add_edge("b", "c", "NEXT")

    result = g.traverse("a", depth=2)
    ids = [n["id"] for n in result]
    assert "a" in ids
    assert "b" in ids
    assert "c" in ids


def test_traverse_depth_1(engine):
    g = GraphStore(engine)
    g.add_node("A", node_id="a")
    g.add_node("B", node_id="b")
    g.add_node("C", node_id="c")
    g.add_edge("a", "b", "NEXT")
    g.add_edge("b", "c", "NEXT")

    result = g.traverse("a", depth=1)
    ids = [n["id"] for n in result]
    assert "a" in ids
    assert "b" in ids
    assert "c" not in ids


def test_shortest_path(engine):
    g = GraphStore(engine)
    g.add_node("A", node_id="a")
    g.add_node("B", node_id="b")
    g.add_node("C", node_id="c")
    g.add_edge("a", "b", "NEXT")
    g.add_edge("b", "c", "NEXT")

    path = g.shortest_path("a", "c")
    assert path == ["a", "b", "c"]


def test_shortest_path_no_path(engine):
    g = GraphStore(engine)
    g.add_node("A", node_id="a")
    g.add_node("B", node_id="b")

    path = g.shortest_path("a", "b")
    assert path is None


def test_node_and_edge_count(engine):
    g = GraphStore(engine)
    assert g.node_count() == 0
    assert g.edge_count() == 0

    g.add_node("A", node_id="a")
    g.add_node("B", node_id="b")
    g.add_edge("a", "b", "LINKS")

    assert g.node_count() == 2
    assert g.edge_count() == 1
