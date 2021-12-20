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
