from __future__ import annotations
from collections import defaultdict
import random
class Chip8:
    display:Display
    pc: int #program counter
    sp: int #stack pointer
    ram: RAM
    registers: defaultdict[int, int]
    dt:int #timer register
    st:int #sound register
    i:int #the I register, generally used for storing address is 16-bits

    def execute(self, instruction:str):
        ...

    def clock_tick(self):
        ...

    def CLS(self):
        self.display.clear()

    def RET(self):
        self.pc = self.ram[self.sp]
        self.sp -= 1

    def JP(self, address):
        self.pc = address

    def CALL(self, address):
        self.sp += 1
        self.ram[self.sp] = self.pc
        self.pc = address

    def SE(self, register_id, value):
        if self.registers[register_id] == value:
            self.pc += 2

    def SNE(self, register_id, value):
        if self.registers[register_id] != value:
            self.pc += 2
    
    def SER(self, register_id1, register_id2):
        if self.registers[register_id1] == self.registers[register_id2]:
            self.pc += 2
    
    def LD(self, register_id, value):
        self.registers[register_id] = value

    def ADD(self, register_id, value):
        self.registers[register_id] = (self.registers[register_id] + value) % 2**8    

    def LDR(self, register_id1, register_id2):
        self.registers[register_id1] = self.registers[register_id2]
    
    def OR(self, register_id1, register_id2):
        self.registers[register_id1] |= self.registers[register_id2]
    
    def AND(self, register_id1, register_id2):
        self.registers[register_id1] &= self.registers[register_id2]
    
    def XOR(self, register_id1, register_id2):
        self.registers[register_id1] ^= self.registers[register_id2]
    
    def ADDR(self, register_id1, register_id2):
        sum = self.registers[register_id1] + self.registers[register_id2]
        self.registers[register_id1] = sum % 2**8
        if sum >= 2**8:
            self.registers[0xF] = 1
    def SUB(self, register_id1, register_id2):
        val = self.registers[register_id1] - self.registers[register_id2]
        if val < 0:
            self.registers[0xF] = 1
            val = val % 2**8 
        self.registers[register_id1] = val
    
    def SHR(self, register_id):
        self.registers[0xF] = self.registers[register_id] % 2
        self.registers[register_id] //= 2
    
    def SUBN(self, register_id1, register_id2):
        val = self.registers[register_id2] - self.registers[register_id1]
        if val < 0:
            self.registers[0xF] = 1
            val = val % 2**8 
        self.registers[register_id1] = val
    
    def SHL(self, register_id):
        if self.registers[register_id] % 2**7 > 0:
            self.registers[0xF] = 1
        self.registers[register_id] = (self.registers[register_id] * 2) % 2**8
    
    def SNER(self, register_id1, register_id2):
        if self.registers[register_id1] != self.registers[register_id2]:
            self.pc += 2
    
    def LDI(self, address):
        self.i = address
    
    def JP(self, address, offset):
        self.pc = address + offset
    
    def RND(self, register_id, mask):
        r = random.randrange(2**8) & mask
        self.registers[register_id] = r

    def DRW(self):
        raise NotImplementedError 

    def SKP(self, register_id, keys_pressed):

        if self.registers[register_id] in keys_pressed:
            self.pc += 2    
    
    def SKNP(self, register_id, keys_pressed):
        if self.registers[register_id] not in keys_pressed:
            self.pc += 2
    
    def LDDT(self, register_id):
        self.registers[register_id] = self.dt

    def LDK(self, register_id):
        raise NotImplementedError
    
    def LDRT(self, register_id):
        self.dt = self.registers[register_id]

    def LDST(self, register_id):
        self.st = self.registers[register_id]
    
    def ADDI(self, register_id):
        self.i += self.registers[register_id]
    
    def LDS(self, register_id):
        '''load the location of the sprite represented in register x'''
        raise NotImplementedError
    
    def LDB(self, register_id):
        '''store register in ram at I, I+1, I+2 in decimal representation'''
        n = self.registers[register_id]
        hundreds = n%100; n -= hundreds
        tens = n%10; n-=tens
        units = n
        self.ram[self.i] = hundreds
        self.ram[self.i+1] = tens
        self.ram[self.i+1] = units
    
    def LDI(self, last_register_id):
        '''make sure last_register_id is inclusive'''
        for register_id in range(last_register_id+1):
            self.ram[self.i+register_id] = self.registers[register_id]
    
    def LDM(self, last_register_id):
        for register_id in range(last_register_id):
            self.registers[register_id] = self.ram[self.i+register_id]



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