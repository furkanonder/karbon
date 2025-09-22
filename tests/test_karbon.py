from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from screeninfo import Monitor

mock_mouse = MagicMock()
mock_mouse.Button = MagicMock()
mock_mouse.Button.left = "left"
mock_mouse.Button.right = "right"
mock_mouse.Listener = MagicMock()

with patch.dict("sys.modules", {"pynput": MagicMock(), "pynput.mouse": mock_mouse}):
    from karbon.karbon import Karbon


@pytest.fixture  # type: ignore[misc]
def mock_monitors() -> list[Monitor]:
    return [
        Monitor(x=0, y=0, width=1920, height=1080, name="Monitor 1"),
        Monitor(x=1920, y=0, width=1920, height=1080, name="Monitor 2"),
    ]


class TestKarbonCore:
    def test_get_current_datetime(self) -> None:
        result = Karbon.get_current_datetime()
        assert isinstance(result, str)
        assert len(result) == 15  # YYYYMMDD_HHMMSS format
        assert result.count("_") == 1

    def test_create_snapshot_folder(self, tmp_path: Path) -> None:
        with patch("pathlib.Path.home", return_value=tmp_path):
            folder_path = Karbon.create_snapshot_folder()
            expected_path = tmp_path / ".karbon_snapshots"
            assert folder_path == expected_path
            assert folder_path.exists()

    def test_create_snapshot_folder_already_exists(self, tmp_path: Path) -> None:
        existing_folder = tmp_path / ".karbon_snapshots"
        existing_folder.mkdir()

        with patch("pathlib.Path.home", return_value=tmp_path):
            folder_path = Karbon.create_snapshot_folder()
            assert folder_path == existing_folder
            assert folder_path.exists()

    def test_monitor_processing(self) -> None:
        # Mock monitors
        mock_monitor1 = Mock()
        mock_monitor1.width = 1920
        mock_monitor1.height = 1080
        mock_monitor1.x = 0
        mock_monitor1.y = 0

        mock_monitor2 = Mock()
        mock_monitor2.width = 1920
        mock_monitor2.height = 1080
        mock_monitor2.x = 1920
        mock_monitor2.y = 0

        monitors = [mock_monitor1, mock_monitor2]
        monitor_names = [f"Monitor {i}: {m.width} x {m.height}" for i, m in enumerate(monitors, start=1)]

        # Test monitor name generation
        assert len(monitor_names) == 2
        assert monitor_names[0] == "Monitor 1: 1920 x 1080"
        assert monitor_names[1] == "Monitor 2: 1920 x 1080"

        # Test monitor selection logic
        current_monitor_index = 0
        current_monitor = monitors[current_monitor_index]
        assert current_monitor == mock_monitor1
        assert current_monitor.width == 1920
        assert current_monitor.height == 1080

    def test_adjust_mouse_coordinates_within_bounds(self) -> None:
        app = Karbon()
        app.current_monitor = Mock()
        app.current_monitor.x = 0
        app.current_monitor.y = 0
        app.window_width = 1920
        app.window_height = 1080

        result = app.adjust_mouse_coordinates(100, 100)
        assert result == (100, 100)

    def test_adjust_mouse_coordinates_outside_bounds(self) -> None:
        app = Karbon()
        app.current_monitor = Mock()
        app.current_monitor.x = 0
        app.current_monitor.y = 0
        app.window_width = 1920
        app.window_height = 1080

        result = app.adjust_mouse_coordinates(2000, 2000)
        assert result is None

    def test_adjust_mouse_coordinates_different_monitor(self) -> None:
        app = Karbon()
        app.current_monitor = Mock()
        app.current_monitor.x = 1920  # Second monitor
        app.current_monitor.y = 0
        app.window_width = 1920
        app.window_height = 1080

        result = app.adjust_mouse_coordinates(2000, 100)
        assert result == (80, 100)

    def test_adjust_mouse_coordinates_edge_cases(self) -> None:
        app = Karbon()
        app.current_monitor = Mock()
        app.current_monitor.x = 0
        app.current_monitor.y = 0
        app.window_width = 1920
        app.window_height = 1080

        # Test exact boundaries
        assert app.adjust_mouse_coordinates(0, 0) == (0, 0)
        assert app.adjust_mouse_coordinates(1919, 1079) == (1919, 1079)

        # Test just outside boundaries
        assert app.adjust_mouse_coordinates(1920, 1080) is None
        assert app.adjust_mouse_coordinates(-1, 0) is None
        assert app.adjust_mouse_coordinates(0, -1) is None


class TestMouseEventHandling:
    def test_mouse_coordinate_consistency(self) -> None:
        app = Karbon()
        app.current_monitor = Mock()
        app.current_monitor.x = 0
        app.current_monitor.y = 0
        app.window_width = 1920
        app.window_height = 1080

        test_coords = [(50, 75), (500, 300), (1000, 800)]

        for x, y in test_coords:
            adjusted = app.adjust_mouse_coordinates(x, y)
            assert adjusted == (x, y)

    def test_mouse_coordinates_multiple_monitors(self) -> None:
        # First monitor
        app = Karbon.__new__(Karbon)
        app.current_monitor = Mock()
        app.current_monitor.x = 0
        app.current_monitor.y = 0
        app.window_width = 1920
        app.window_height = 1080

        assert app.adjust_mouse_coordinates(100, 100) == (100, 100)
        assert app.adjust_mouse_coordinates(2000, 100) is None

        # Second monitor
        app.current_monitor.x = 1920
        app.window_width = 1920
        app.window_height = 1080

        assert app.adjust_mouse_coordinates(2000, 100) == (80, 100)
        assert app.adjust_mouse_coordinates(100, 100) is None
