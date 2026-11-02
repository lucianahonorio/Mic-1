def mask32(x):
    return x & 0xFFFFFFFF


def com_sinal(x, bits=32):
    x &= (1 << bits) - 1
    if x >> (bits - 1):
        return x - (1 << bits)
    return x


def estende_sinal8(x):
    x &= 0xFF
    if x & 0x80:
        return x | 0xFFFFFF00
    return x


def bin32(x):
    return format(mask32(x), "032b")
