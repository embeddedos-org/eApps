import unittest

class TesteAppsSimulation(unittest.TestCase):
    def test_touch_screen_digitizer_simulation(self):
        # Simulate touch screen digitizer coordinate mapping
        screen_width, screen_height = 1080, 2400
        digitizer_max_x, digitizer_max_y = 4095, 4095
        # Touch at center of screen
        touch_x, touch_y = 2048, 2048
        mapped_x = int((touch_x / digitizer_max_x) * screen_width)
        mapped_y = int((touch_y / digitizer_max_y) * screen_height)
        assert abs(mapped_x - screen_width//2) < 5
        assert abs(mapped_y - screen_height//2) < 5
