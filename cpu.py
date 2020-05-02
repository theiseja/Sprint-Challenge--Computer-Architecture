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

    def JEQ(self):
        """Jumps to address stored in given register if equal flag is set to true"""

        address = self.reg[self.operand_a]

        if self.FL & 0b0000000 == 1:
            self.PC = address

        else:
            self.PC += 2

    def JNE(self):
        """jumps to the address stored in given register if e flag is clear (false, 0)"""
        address = self.reg[self.operand_a]

        if self.FL & 0b00000001 == 0:
            self.PC = address
        else:
            self.PC += 2

    def HALT(self):
        """exits the program"""
        sys.exit()

    def LOAD(self):
        """Loads value to register"""
        self.reg[self.operand_a] = self.oeprand_b

    def PRINT(self):
        """Prints the value that is currently stored in a register"""
        print(self.reg[self.operand_a])

    def PUSH(self):
        """Pushes the value in the given register to the top of the stack"""
        # decrement the SP
        global SP

        self.reg[SP] -= 1

        # copies the value in the given register to the SP address
        value = self.reg[self.operand_a]

        self.ram[self.reg[SP]] = value

    def POP(self):
        """Pops the value at the top of the stack into the register"""
        global SP
        # copies value of address pointed to by SP to the register"""
        value = self.ram[self.reg[SP]]

        # given register from argument
        register = self.operand_a

        self.reg[register] = value

        # increment SP
        self.reg[SP] += 1

    def ram_read(self, address):
        """Accepts an address to read and return the value that it has stored"""
        self.MAR = address
        self.MDR = self.ram[address]
        return self.ram[address]

    def ram_write(self, value, address):
        """Accepts a value to write and what address to write the value to"""
        self.MAR = address
        self.MDR = value
        self.ram[address] = value

    def load(self):
        """Loads a program into memory"""
        if len(sys.argv) != 2:
            print("ERROR: Must input file name")
            sys.exit(1)
        filename = sys.argv[1]

        try:
            address = 0
            # opens the file
            with open(filename) as program:
                # reads all the lines in the file
                for instruction in program:
                    # parses out comments
                    comment_split = instruction.strip().split("#")
                    # casts the number from strings to ints
                    value = comment_split[0].strip()

                    # ignore blank lines
                    if value == "":
                        continue
                    num = int(value, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def ALU(self, op, reg_a, reg_b):
        """ALU operations"""
        if op == math_op["ADD"]:
            print("ADDING: ")
            self.reg[reg_a] += self.reg[reg_b]

        elif op == math_op["SUB"]:
            print("SUBTRACTING: ")
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == math_op["MUL"]:
            print("MULTIPLYING: ")
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == math_op["CMP"]:
            valueA = self.reg[self.operand_a]
            valueB = self.reg[self.operand_b]

            if valueA == valueB:
                self.FL = 0b00000001

            if valueA < valueB:
                self.FL = 0b00000100

            if valueA > valueB:
                self.FL = 0b00000010
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

    def move_PC(self, IR):
        if (IR << 3) % 255 >> 7 != 1:
            self.PC += (IR >> 6) + 1

    def run(self):
        """Run the CPU."""
        while True:
            IR = self.ram_read(self.PC)
            self.operand_a = self.ram_read(self.PC + 1)
            self.operand_b = self.ram_read(self.PC + 2)
            if (IR << 2) % 255 >> 7 == 1:
                self.ALU(IR, self.operand_a, self.operand_b)
                self.move_PC(IR)
            elif (IR << 2) % 255 >> 7 == 0:
                self.instructions[binary_op[IR]]()
                self.move_PC(IR)
            else:
                print(f"Space dog did not understand that command: {IR}")
                print(self.trace())
                sys.exit(1)