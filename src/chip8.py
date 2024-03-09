from __future__ import annotations
from collections import defaultdict
import random

CLOCK_FREQUENCY = 500

class Chip8Error(Exception):
    def __init__(self, message):
        super().__init__(message)


class Chip8:
    display:Display
    pc: int #program counter
    sp: int #stack pointer
    ram: RAM
    registers: defaultdict[int, int]
    dt:int #timer register
    st:int #sound register
    i:int #the I register, generally used for storing address is 16-bits
    _clock_counter: int

    def __init__(self, display:Display):
        self.ram=RAM()
        self.registers = defaultdict(int)
        self.display = display
        self.initialize()

    def initialize(self, pc_position=512):
        self.pc=pc_position
        self.sp=0
        self.i=0
        self.dt=0
        self.st=0
        self._clock_counter = 0

    def execute(self, inst:int):
        d4, d3, d2, d1 = (inst&0xF000)>>3*4, (inst&0x0F00)>>2*4, (inst&0x00F0)>>4, inst&0x000F
        match d4, d3, d2, d1:    
            case 0, 0, 0xE, 0:
                self.CLS()
            case 0, 0, 0xE, 0xE:
                self.RET()
            case 1, _, _, _:
                self.JP(inst & 0xFFF)
            case 2, _, _, _:
                self.CALL(inst & 0xFFF)
            case 3, reg_id, _, _:
                self.SE(reg_id, inst & 0xFF)
            case 4, reg_id, _, _:
                self.SNE(reg_id, inst & 0xFF)
            case 5, x, y, 0:
                self.SER(x, y)
            case 6, x, _, _:
                self.LD(x, inst&0xFF)
            case 7, x, _, _:
                self.ADD(x, inst&0xFF)
            case 8, x, y, 0:
                self.LDR(x,y)
            case 8, x, y, 1:
                self.OR(x,y)
            case 8, x, y, 2:
                self.AND
            case 8, x, y, 3:
                self.XOR(x, y)
            case 8, x, y, 4:
                self.ADDR(x, y)
            case 8, x, y, 5:
                self.SUB(x, y)
            case 8, x, y, 6:
                self.SHR(x)
            case 8, x, y, 7:
                self.SUBN(x,y)
            case 8, x, y, 0xE:
                self.SHL(x)
            case 9, x, y, 0:
                self.SNER(x,y)
            case 0xA, _, _, _:
                self.LDI(inst&0xFFF)
            case 0xB, _, _, _:
                self.JPO(inst&0xFFF)
            case 0xC, x, _, _:
                self.RND(x, inst&0xFF)
            case 0xD, x, y, n:
                self.DRW()
            case 0xE, x, 9, 0xE:
                raise NotImplementedError
            case 0xE, x, 0xA, 1:
                raise NotADirectoryError
            case 0xF, x, 0, 7:
                self.LDDT(x)
            case 0xF, x, 0, 0xA:
                raise NotImplementedError
            case 0xF, x, 1, 5:
                self.LDRT(x)
            case 0xF, x, 1, 8:
                self.LDST(x)
            case 0xF, x, 1, 0xE:
                self.ADDI(x)
            case 0xF, x, 2, 9:
                raise NotImplementedError
            case 0xF, x, 3, 3:
                self.LDB(x)
            case 0xF, x, 5, 5:
                self.LDIA(x)
            case 0xF, x, 6, 5:
                self.LDM(x)

            


    def clock_tick(self):
        current_instruction = self.ram[self.pc]<<8 + self.ram[self.pc+1]
        self.execute(current_instruction)
        self.pc += 2
        self._clock_counter += 1
        if self._clock_counter % (CLOCK_FREQUENCY//60):
            if self.dt > 0:
                self.dt -= 1
            if self.st > 0:
                self.st -= 1

    def load_rom(self,rom:bytearray, starting_address=512):
        for index, byte in enumerate(rom):
            self.ram[starting_address+index] = byte
        self.initialize(starting_address)


    def CLS(self):
        '''00E0'''
        self.display.clear()

    def RET(self):
        '''00EE'''
        if self.sp == 0:
            raise Chip8Error("Stack Pointer at position 0 can not return")
        self.pc = self.ram[self.sp]
        self.sp -= 1

    def JP(self, address):
        '''1nnn'''
        self.pc = address

    def CALL(self, address):
        '''2nnn'''
        self.sp += 1
        self.ram[self.sp] = self.pc
        self.pc = address

    def SE(self, register_id, value):
        '''3xkk'''
        if self.registers[register_id] == value:
            self.pc += 2

    def SNE(self, register_id, value):
        '''4xkk'''
        if self.registers[register_id] != value:
            self.pc += 2
    
    def SER(self, register_id1, register_id2):
        '''5xy0'''
        if self.registers[register_id1] == self.registers[register_id2]:
            self.pc += 2
    
    def LD(self, register_id, value):
        '''6xkk'''
        self.registers[register_id] = value

    def ADD(self, register_id, value):
        '''7xkk'''
        self.registers[register_id] = (self.registers[register_id] + value) % 2**8    

    def LDR(self, register_id1, register_id2):
        '''8xy0'''
        self.registers[register_id1] = self.registers[register_id2]
    
    def OR(self, register_id1, register_id2):
        '''8xy1'''
        self.registers[register_id1] |= self.registers[register_id2]
    
    def AND(self, register_id1, register_id2):
        '''8xy2'''
        self.registers[register_id1] &= self.registers[register_id2]
    
    def XOR(self, register_id1, register_id2):
        '''8xy3'''
        self.registers[register_id1] ^= self.registers[register_id2]
    
    def ADDR(self, register_id1, register_id2):
        '''8xy4'''
        sum = self.registers[register_id1] + self.registers[register_id2]
        self.registers[register_id1] = sum % 2**8
        if sum >= 2**8:
            self.registers[0xF] = 1
    
    def SUB(self, register_id1, register_id2):
        '''8xy5'''
        val = self.registers[register_id1] - self.registers[register_id2]
        if val < 0:
            self.registers[0xF] = 1
            val = val % 2**8 
        self.registers[register_id1] = val
    
    def SHR(self, register_id):
        '''8xy6'''
        self.registers[0xF] = self.registers[register_id] % 2
        self.registers[register_id] //= 2
    
    def SUBN(self, register_id1, register_id2):
        '''8xy7'''
        val = self.registers[register_id2] - self.registers[register_id1]
        if val < 0:
            self.registers[0xF] = 1
            val = val % 2**8 
        self.registers[register_id1] = val
    
    def SHL(self, register_id):
        '''8xyE'''
        if self.registers[register_id] % 2**7 > 0:
            self.registers[0xF] = 1
        self.registers[register_id] = (self.registers[register_id] * 2) % 2**8
    
    def SNER(self, register_id1, register_id2):
        '''9xy0'''
        if self.registers[register_id1] != self.registers[register_id2]:
            self.pc += 2
    
    def LDI(self, address):
        '''Annn'''    
        self.i = address
    
    def JPO(self, address):
        '''Bnnn'''
        self.pc = address + self.registers[0]
    
    def RND(self, register_id, mask):
        '''Cxkk'''
        r = random.randrange(2**8) & mask
        self.registers[register_id] = r

    def DRW(self):
        '''Dxyn'''
        raise NotImplementedError 

    def SKP(self, register_id, keys_pressed):
        '''Ex9E'''
        if self.registers[register_id] in keys_pressed:
            self.pc += 2    
    
    def SKNP(self, register_id, keys_pressed):
        '''ExA1'''
        if self.registers[register_id] not in keys_pressed:
            self.pc += 2
    
    def LDDT(self, register_id):
        '''fx07'''
        self.registers[register_id] = self.dt

    def LDK(self, register_id):
        '''fx0A'''
        raise NotImplementedError
    
    def LDRT(self, register_id):
        '''fx15'''
        self.dt = self.registers[register_id]

    def LDST(self, register_id):
        '''fx18'''
        self.st = self.registers[register_id]
    
    def ADDI(self, register_id):
        '''fx1E'''
        self.i += self.registers[register_id]
    
    def LDS(self, register_id):
        '''fx29, load the location of the sprite represented in register x'''
        raise NotImplementedError
    
    def LDB(self, register_id):
        '''Fx33, store register in ram at I, I+1, I+2 in decimal representation'''
        n = self.registers[register_id]
        hundreds = n%100; n -= hundreds*100
        tens = n%10; n-=tens*10
        units = n
        self.ram[self.i] = hundreds
        self.ram[self.i+1] = tens
        self.ram[self.i+1] = units
    
    def LDIA(self, last_register_id):
        '''Fx55, make sure last_register_id is inclusive'''
        for register_id in range(last_register_id+1):
            self.ram[self.i+register_id] = self.registers[register_id]
    
    def LDM(self, last_register_id):
        '''Fx65'''
        for register_id in range(last_register_id):
            self.registers[register_id] = self.ram[self.i+register_id]
    
    def __str__(self)->str:
        def ram(offset): return hex(self.ram[self.pc+offset])
        return\
        f"Chip8:-------\n\
        pc: {hex(self.pc)} --> [ {ram(0)} | {ram(1)} ] || [ {ram(2)} | {ram(2)} ] || ..."




class RAM:
    values: defaultdict
    def __init__(self):
        self.values = defaultdict(int)
    def __getitem__(self, index:int)->int:
        return self.values[index]
    def __setitem__(self, index: int, value:int):
        self.values[index] = value

class Display:
    def clear(self):
        ...