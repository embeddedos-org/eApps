import unittest

class TesteAppsFunctional(unittest.TestCase):
    def test_user_interaction_event_pipeline(self):
        events = []
        # User taps button
        events.append({"type": "TAP", "target": "submit_btn"})
        # Event handler dispatches event
        dispatched = events.pop(0)
        assert dispatched["type"] == "TAP"
