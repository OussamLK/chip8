import pytest
from src.chip8 import RAM

@pytest.fixture
def ram():
    return RAM()

def test_ram(ram):
    ram[0] = 3
    assert ram[0] == 3
    assert ram[1] == 0