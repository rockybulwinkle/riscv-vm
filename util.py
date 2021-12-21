import functools

@functools.lru_cache(maxsize=None)
def generate_mask(msb, lsb):
    bitlen = msb-lsb+1
    mask = "1"*bitlen + "0" * lsb
    return int(mask, 2)

def extract_bitfield(val, msb, lsb):
    val &= generate_mask(msb,lsb)
    val >>= lsb
    return val


def sign_extend(val, signbit):
    if val & (1<<signbit):
        val &= generate_mask(signbit-1, 0)
        val -= 1 << signbit

    return val

#Credit for getch impl: https://code.activestate.com/recipes/134892-getch-like-unbuffered-character-reading-from-stdin/
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
