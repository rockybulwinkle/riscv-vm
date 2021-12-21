#!/usr/bin/env python3
import state
import ops
import conf
import sys
from datetime import datetime
now = datetime.now

class Machine:
    def __init__(self):
        self.cycles=0
        self.state = state.MachineState()
        with open(sys.argv[1], "rb") as prog:
            addr = 0
            b = prog.read(1)
            while b:
                b = b[0]
                if conf.DEBUG: print(hex(b))
                self.state.mem.poke(addr, b, 1)
                addr += 1
                b = prog.read(1)
        #using the ARM Cortex M1 standard for how we initialize PC and SP.
        self.state.regs.pc = self.state.mem.peek(4, 4)
        self.state.regs.set(2, self.state.mem.peek(0,4))
        if conf.DEBUG: print("PC is", hex(self.state.regs.pc))
        if conf.DEBUG: print("SP is", hex(self.state.regs.get(2)))
        self.hit_main=False

    def run(self):
        oldsp = self.state.regs.get(2)
        while True:
            if self.state.regs.pc == 0x250:
                self.hit_main=True

            if conf.DEBUG and self.hit_main:
                input("Hit main")
            instr = self.state.mem.peek(self.state.regs.pc, 4)
            if conf.DEBUG: print("PC is", hex(self.state.regs.pc))
            if conf.DEBUG: print("instr is", bin(instr), hex(instr))
            instr&=0b1111111
            newpc = ops.op_lookup[instr].call(self.state)
            if newpc == "exit":
                self.state.regs.pc += 4
                return
            elif newpc is not None:
                self.state.regs.pc = newpc
            else:
                self.state.regs.pc += 4
            newsp = self.state.regs.get(2)
            if conf.DEBUG and oldsp != newsp:
                print("New SP:", hex(newsp))
            
            oldsp=newsp
            if conf.DEBUG: print()
            self.cycles+=1

if __name__=="__main__":
    start = now()
    mach = Machine()
    try:
        mach.run()
    except KeyboardInterrupt:
        pass
    end = now()
    print()
    print("Cycle Count:", mach.cycles)
    waiting_time = mach.state.mem._time_spent_waiting.total_seconds()
    total_time = (end-start).total_seconds()
    print("Frequency:","%.2f"%((mach.cycles/1000)/(total_time-waiting_time)), "KHz")
    print("Total time:", total_time)
    print("Compute time:", total_time-waiting_time)
    print("User time:", waiting_time)
    print("Max SP:", hex(mach.state.regs._max_sp))
    print("Min SP:", hex(mach.state.regs._min_sp))
    print("Deepest Stack:", hex(mach.state.regs._max_sp - mach.state.regs._min_sp))
