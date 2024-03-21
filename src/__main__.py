from src.chip8 import Chip8, Display, Console
def main():
    '''main function'''
    print('A chip-8 emulator is being made...')
    console = Console()
    console.load_rom("test", bytearray([0xA0, 0x5A, 0xD0, 0x05]))
    console.start() 

if __name__ == '__main__':
    main()