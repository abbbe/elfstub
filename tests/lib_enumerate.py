import pytest
from src.elf_patcher import enumerate_symbols
from src.config import LIB_PATH

def test_enumerate_dynsym():
    method_list = map(lambda x: x[1].name, \
                      enumerate_symbols(LIB_PATH, 'SHT_DYNSYM', None, read_only=True))
    assert 'puts' in method_list, "Expected to find 'puts' method in libc"

