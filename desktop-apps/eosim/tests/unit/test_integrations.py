# SPDX-License-Identifier: MIT
"""Tests for external tool integrations — XPlane, Gazebo, OpenFOAM."""
import pytest
from unittest.mock import patch, MagicMock


class TestXPlaneConnection:
    """Test XPlane connection with mocked sockets."""

    def test_init_defaults(self):
        from eosim.integrations.xplane import XPlaneConnection
        conn = XPlaneConnection()
        assert conn.host == '127.0.0.1'
        assert conn.port == 49000
        assert conn.connected is False

    def test_init_custom(self):
        from eosim.integrations.xplane import XPlaneConnection
        conn = XPlaneConnection(host='192.168.1.1', port=50000)
        assert conn.host == '192.168.1.1'
        assert conn.port == 50000

    @patch('socket.socket')
    def test_connect_success(self, mock_socket_cls):
        from eosim.integrations.xplane import XPlaneConnection
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        conn = XPlaneConnection()
        result = conn.connect()
        assert result is True
        assert conn.connected is True

    @patch('socket.socket')
    def test_connect_failure(self, mock_socket_cls):
        import socket
        from eosim.integrations.xplane import XPlaneConnection
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = socket.error("Connection refused")
        mock_socket_cls.return_value = mock_sock
        conn = XPlaneConnection()
        result = conn.connect()
        assert result is False
        assert conn.connected is False

    def test_disconnect(self):
        from eosim.integrations.xplane import XPlaneConnection
        conn = XPlaneConnection()
        conn._sock = MagicMock()
        conn.connected = True
        conn.disconnect()
        assert conn.connected is False
        assert conn._sock is None

    def test_get_status(self):
        from eosim.integrations.xplane import XPlaneConnection
        conn = XPlaneConnection()
        status = conn.get_status()
        assert 'connected' in status
        assert 'host' in status
        assert 'port' in status
        assert status['connected'] is False

    def test_set_dataref_when_disconnected(self):
        from eosim.integrations.xplane import XPlaneConnection
        conn = XPlaneConnection()
        conn.set_dataref('sim/test', 1.0)  # should not raise

    def test_receive_data_when_no_socket(self):
        from eosim.integrations.xplane import XPlaneConnection
        conn = XPlaneConnection()
        data = conn.receive_data()
        assert data == {}


class TestGazeboConnection:
    """Test Gazebo connection with mocked subprocess."""

    def test_init_defaults(self):
        from eosim.integrations.gazebo import GazeboConnection
        conn = GazeboConnection()
        assert conn.host == '127.0.0.1'
        assert conn.port == 11345
        assert conn.connected is False

    @patch('shutil.which', return_value=None)
    def test_not_available(self, mock_which):
        from eosim.integrations.gazebo import GazeboConnection
        assert GazeboConnection.available() is False

    @patch('shutil.which', return_value='/usr/bin/gz')
    def test_available(self, mock_which):
        from eosim.integrations.gazebo import GazeboConnection
        assert GazeboConnection.available() is True

    @patch('shutil.which', return_value=None)
    def test_connect_when_not_available(self, mock_which):
        from eosim.integrations.gazebo import GazeboConnection
        conn = GazeboConnection()
        result = conn.connect()
        assert result is False

    def test_disconnect(self):
        from eosim.integrations.gazebo import GazeboConnection
        conn = GazeboConnection()
        conn.connected = True
        conn.disconnect()
        assert conn.connected is False

    def test_get_status(self):
        from eosim.integrations.gazebo import GazeboConnection
        conn = GazeboConnection()
        status = conn.get_status()
        assert 'connected' in status
        assert 'models' in status
        assert isinstance(status['models'], list)


class TestOpenFOAMRunner:
    """Test OpenFOAM runner with mocked subprocess."""

    def test_init_defaults(self):
        from eosim.integrations.openfoam import OpenFOAMRunner
        runner = OpenFOAMRunner()
        assert runner.case_dir == ''
        assert runner.solver == 'simpleFoam'

    @patch('shutil.which', return_value=None)
    def test_not_available(self, mock_which):
        from eosim.integrations.openfoam import OpenFOAMRunner
        assert OpenFOAMRunner.available() is False

    @patch('shutil.which', return_value='/usr/bin/simpleFoam')
    def test_available(self, mock_which):
        from eosim.integrations.openfoam import OpenFOAMRunner
        assert OpenFOAMRunner.available() is True

    def test_set_solver(self):
        from eosim.integrations.openfoam import OpenFOAMRunner
        runner = OpenFOAMRunner()
        runner.set_solver('icoFoam')
        assert runner.solver == 'icoFoam'

    def test_set_solver_invalid(self):
        from eosim.integrations.openfoam import OpenFOAMRunner
        runner = OpenFOAMRunner()
        runner.set_solver('fakeSolver')
        assert runner.solver == 'simpleFoam'  # unchanged

    def test_validate_case_no_dir(self):
        from eosim.integrations.openfoam import OpenFOAMRunner
        runner = OpenFOAMRunner(case_dir='/nonexistent/path')
        errors = runner.validate_case()
        assert len(errors) > 0
        assert any('does not exist' in e for e in errors)

    @patch('shutil.which', return_value=None)
    def test_run_not_available(self, mock_which):
        from eosim.integrations.openfoam import OpenFOAMRunner
        runner = OpenFOAMRunner(case_dir='/tmp')
        result = runner.run()
        assert result['success'] is False
        assert 'not installed' in result['log']

    def test_get_status(self):
        from eosim.integrations.openfoam import OpenFOAMRunner
        runner = OpenFOAMRunner()
        status = runner.get_status()
        assert 'available' in status
        assert 'solver' in status
        assert 'converged' in status

    def test_parse_residuals_empty(self):
        from eosim.integrations.openfoam import OpenFOAMRunner
        runner = OpenFOAMRunner()
        residuals = runner.parse_residuals()
        assert isinstance(residuals, dict)
        assert len(residuals) == 0


class TestEngineDispatch:
    """Test get_engine dispatches correctly for new engine types."""

    def test_xplane_engine_dispatch(self):
        from eosim.engine.backend import get_engine, XPlaneEngine
        from unittest.mock import MagicMock
        platform = MagicMock()
        platform.engine = 'xplane'
        engine = get_engine(platform)
        assert isinstance(engine, XPlaneEngine)

    def test_gazebo_engine_dispatch(self):
        from eosim.engine.backend import get_engine, GazeboEngine
        from unittest.mock import MagicMock
        platform = MagicMock()
        platform.engine = 'gazebo'
        engine = get_engine(platform)
        assert isinstance(engine, GazeboEngine)

    def test_openfoam_engine_dispatch(self):
        from eosim.engine.backend import get_engine, OpenFOAMEngine
        from unittest.mock import MagicMock
        platform = MagicMock()
        platform.engine = 'openfoam'
        engine = get_engine(platform)
        assert isinstance(engine, OpenFOAMEngine)

    def test_xplane_available_returns_bool(self):
        from eosim.engine.backend import XPlaneEngine
        result = XPlaneEngine.available()
        assert isinstance(result, bool)

    def test_gazebo_available_returns_bool(self):
        from eosim.engine.backend import GazeboEngine
        result = GazeboEngine.available()
        assert isinstance(result, bool)

    def test_openfoam_available_returns_bool(self):
        from eosim.engine.backend import OpenFOAMEngine
        result = OpenFOAMEngine.available()
        assert isinstance(result, bool)
