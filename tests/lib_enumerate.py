import pytest
from src.elf_patcher import enumerate_symbols

LIB_PATH = "/lib/x86_64-linux-gnu/libc.so.6"

def test_enumerate_dynsym():
    method_list = map(lambda x: x[1].name, \
                      enumerate_symbols(LIB_PATH, 'SHT_DYNSYM', None, read_only=True))
    assert 'puts' in method_list, "Expected to find 'puts' method in libc"

