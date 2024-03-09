from src.chip8 import Chip8, Display
def main():
    '''main function'''
    print('A chip-8 emulator is being made...')
    chip8 = Chip8(Display())
    print(chip8)

if __name__ == '__main__':
    main()