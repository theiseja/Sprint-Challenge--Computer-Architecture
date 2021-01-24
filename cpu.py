"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8 
        self.SP = 7
        self.reg[self.SP] = 0xF4 # Stack pointer starts at F4 or 244 in RAM
        self.PC = 0 # Program Counter, address of the currently executing instruction
        self.IR = 0 # Instruction Register, contains a copy of the currently executing instruction
        self.FL = 6 # Flag Register 
        self.op_table = {
                        0b10000010 : self.LDI, 
                        0b01000111 : self.PRN, 
                        0b10100010 : self.MUL,
                        0b00000001 : self.HLT,
                        0b01000101 : self.PUSH,
                        0b01000110 : self.POP,
                        0b01010000 : self.CALL, 
                        0b00010001 : self.RET,
                        0b10100000 : self.ADD, 
                        0b01010110 : self.JNE,
                        0b01010100 : self.JMP,
                        0b01010101 : self.JEQ, 
                        0b10100111 : self.CMP}

    def load(self):
        """Load a program into memory."""

        address = 0

        file = open('sctest.ls8',  "r")
        for line in file.readlines():
            #load a line into memory
            try:
                x = line[:line.index("#")]
            except ValueError:
                x = line
            try: 
                #convert binary to decimal
                y = int(x, 2)
                self.ram[address] = y
            except ValueError:
                continue
            address+=1
    
    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def MUL(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
    
    # Push the value in the given register on the stack.
    def PUSH(self, operand_a, operand_b):        
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[operand_a]
    
    # Pop the value at the top of the stack into the given register.
    def POP(self, operand_a, operand_b):
        self.reg[operand_a] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    # Sets the PC to the register value
    def CALL(self, operand_a, operand_b):
        # address of instruction after call is pushed on to the stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.PC + 2
        # set PC to value stored in given register
        self.PC = self.reg[operand_a]
        return True
    
    def RET(self, operand_a, operand_b):
        self.pop(operand_a, 0)
        self.PC = self.reg[operand_a]
        return True

    def ADD(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] + self.reg[operand_b]
    
    def CMP(self, operand_a, operand_b):
        value_a = self.reg[operand_a]
        value_b = self.reg[operand_b]

        if value_a == value_b:
            self.reg[self.FL] = 1
        elif value_a > value_b:
            self.reg[self.FL] = 2
        else:
            self.reg[self.FL] = 4


    def JNE(self, operand_a, operand_b):
        value = self.reg[self.FL]
        if value == 2 or value == 4: #not equal
            return self.JMP(operand_a, 0)

    def JMP(self, operand_a, operand_b):
        self.PC = self.reg[operand_a]
        return True

    def JEQ(self, operand_a, operand_b):
        if self.reg[self.FL] == 1:
            return self.JMP(operand_a, 0)
    def ram_read(self, address):
        return self.ram[address]
    
    def ram_write(self, value, address):
        self.ram[address] = value
    
    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def HLT(self, operand_a, operand_b):
        sys.exit()

    def ALU(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            self.IR = self.ram[self.PC]
            operand_a = self.ram[self.PC + 1]
            operand_b = self.ram[self.PC + 2]

            willJump = self.op_table[self.IR](operand_a, operand_b)

            if not willJump:
                self.PC += (self.IR >> 6) + 1;