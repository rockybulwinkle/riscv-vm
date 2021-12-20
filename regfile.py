import conf
import util
import math

class RegisterFile:
    def __init__(self):
        self._regs = [0]*32
        self._pc = 0
        self._max_sp = 0
        self._min_sp = math.inf

    def set(self, num, val):
        if num != 0:
            self._regs[num] = val & 0xFFFFFFFF
        if num == 2 and val > self._max_sp:
            self._max_sp = val
        if num == 2 and val < self._min_sp:
            self._min_sp = val

        if conf.DEBUG: print("Set register %d to"%num, hex(val))

    def get(self, num):
        val = self._regs[num]
        if conf.DEBUG: print("Read register %d as"%num, hex(val))
        return val

    def get_signed(self, num):
        val = util.sign_extend(self.get(num), 31)
        if conf.DEBUG: print("Read register %d as (signed)"%num, hex(val))
        return val

    @property
    def pc(self):
        return self._pc

    @pc.setter
    def pc(self, value):
        self._pc = value & 0xFFFFFFFF

