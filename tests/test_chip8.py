import pytest
from src.chip8 import Chip8, Display, Chip8Error
from unittest.mock import Mock

@pytest.fixture
def mock_display():
    return Mock(spec=Display)

@pytest.fixture
def chip8(mock_display):
    return Chip8(mock_display)

def test_initialization(chip8):
    ...

def test_cls(chip8):
    chip8.execute(0xE0)
    chip8.display.clear.assert_called_once()

def test_ret(chip8):
    with pytest.raises(Chip8Error) as error:
        chip8.execute(0x00EE)
    assert "position 0" in str(error)