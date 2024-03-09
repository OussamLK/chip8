import pytest
from src.chip8 import Chip8, Display
from unittest.mock import Mock

@pytest.fixture
def mock_display():
    return Mock(spec=Display)

@pytest.fixture
def chip8(mock_display):
    return Chip8(mock_display)

def test_chip8_cls(chip8):
    chip8.CLS()
    chip8.display.clear.assert_called_once()

