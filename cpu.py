"""CPU Functionality"""

import sys

# Operation tables
binary_op = {
    0b00000001: 'HLT',
    0b10000010: 'LDI',
    0b01000111: 'PRN',
    0b01000101: 'PUSH',
    0b01000110: 'POP',
    0b01010000: 'CALL',
    0b00010001: 'RET',
    0b01010100: 'JMP',
    0b01010101: 'JEQ',
    0b01010110: 'JNE'
}

math_op = {
    "ADD": 0b10100000,
    "SUB": 0b10100001,
    "MUL": 0B10100010,
    "CMP": 0b10100111
}

# Global constants
SP = 7 

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU"""
        self.ram = [0] * 256
        # Registers
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.operand_a = None
        self.oeprand_b = None

        # Internal registers
        self.PC = 0 # Program counter
        self.MAR = None # Memory address register
        self.MDR = None # Memory data register
        self.FL = 0b00000000 # Flags

        # Branch table
        self.instructions = {}
        self.instructions['HLT'] = self.HALT
        self.instructions['LDI'] = self.LOAD
        self.instructions['PRN'] = self.PRINT
        self.instructions['PUSH'] = self.PUSH
        self.instructions['POP'] = self.POP
        self.instructions['CALL'] = self.CALL
        self.instructions['RET'] = self.RET
        self.instructions['JMP'] = self.JMP
        self.instructions['JEQ'] = self.JEQ
        self.instructions['JNE'] = self.JNE

    def CALL(self):
        """subroutine(function) call at the address stored in register"""
        self.reg[SP] -= 1

        # instruction address
        instruction_address = self.PC + 2

        # pushes address of instruction onto the stack
        self.ram[self.reg[SP]] = instruction_address

        # PC has address stored in register
        register = self.operand_a

        self.PC = self.reg[register]

    def RET(self):
        self.PC = self.ram[self.reg[SP]]

        self.reg[SP] += 1

    def JMP(self):
        address = self.reg[self.operand_a]

        print("JUMPING")
        self.PC = address