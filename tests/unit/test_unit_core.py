import unittest

class TesteAppsUnit(unittest.TestCase):
    def test_widget_tree_layout_constraints(self):
        # Simulate widget tree layout engine
        widget = {"type": "Container", "width": 100, "height": 100, "child": {"type": "Text", "width": 50, "height": 20}}
        # Layout engine constrains child
        child_layout = {"width": min(widget["child"]["width"], widget["width"]), "height": min(widget["child"]["height"], widget["height"])}
        assert child_layout["width"] == 50
        assert child_layout["height"] == 20
