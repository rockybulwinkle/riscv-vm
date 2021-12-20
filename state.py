import regfile
import memory

class MachineState:
    def __init__(self):
        self.regs = regfile.RegisterFile()
        self.mem = memory.Memory()
