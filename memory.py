import conf
import util
import datetime

from collections import defaultdict

#Just a simple read/write memory to start with.
#All addresses R/W for now. May start implemention MMU or memory regions later...



LITTLE="little"
ENDIAN=LITTLE


class UnalignedException(Exception):
    pass


class Memory:
    def __init__(self):
        self._mem = defaultdict(lambda: 0)
        self.allow_unaligned=True
        self._time_spent_waiting = datetime.timedelta()

    def check_alignment(self, addr, num_bytes):
        if not self.allow_unaligned:
            if addr%num_bytes:
                raise UnalignedException()

    def peek(self, addr, num_bytes):
        addr &= 0xFFFFFFFF
        self.check_alignment(addr, num_bytes)

        val = 0
        if addr == 0xA0001000:
            if conf.DEBUG: print("getch:", end="", flush=True)
            start=datetime.datetime.now()
            val = util.getch()
            end=datetime.datetime.now()
            self._time_spent_waiting+= end-start
            if conf.DEBUG: print(val)
            val = ord(val)

        else:
            if ENDIAN==LITTLE:
                for i in range(num_bytes):
                    val |= self._mem[i+addr] << (8*i)
            else:
                for i in range(num_bytes):
                    val |= self._mem[num_bytes-1-i+addr] << (8*i)
            if conf.DEBUG: print ("Read %d bytes at addr"%num_bytes, hex(addr), ", data=", hex(val))
        return val


    def poke(self, addr, val, num_bytes):
        addr &= 0xFFFFFFFF
        self.check_alignment(addr, num_bytes)

        if addr == 0xA0001000:
            if conf.DEBUG:
                print("******Printed char:", chr(val&0xFF))
            else:
                print(chr(val&0xFF), end="", flush=True)

        if ENDIAN==LITTLE:
            for i in range(num_bytes):
                self._mem[i+addr] = (val >> (8*i)) & 0xFF
        else:
            for i in range(num_bytes):
                self._mem[num_bytes-1-i+addr] = (val >> (8*i)) & 0xFF
        
        if conf.DEBUG: print ("Wrote %d bytes at addr"%num_bytes, hex(addr), ", data=", hex(val))
