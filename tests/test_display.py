from src.chip8 import Display
import pytest

@pytest.fixture
def display():
    return Display(12,24)

@pytest.fixture
def sprites():
    _1 = '''00100000
            01100000
            00100000
            00100000
            01110000'''
    _1 = [int(line, base=2) for line in _1.split('\n')]
    return dict(one=bytearray(_1))

def test_display(display, sprites):
    x, y = 2, 2
    col = display.draw_sprite((x, y), sprites['one'])
    assert not col
    col = display.draw_sprite((x,y+1), sprites['one'])
    assert col
    assert display.bitmap[x,y+2]
    assert display.bitmap[x+1,y+1]
    assert not display.bitmap[x+1, y+2]
    assert not display.bitmap[x+1, y]
