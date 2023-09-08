import pytest
from src.elf_patcher import enumerate_symbols

DUMMY_PROGRAM_PATH = "tests/dummy"

def test_enumerate_symtab():
    method_list = map(lambda x: x[1].name, enumerate_symbols(DUMMY_PROGRAM_PATH, 'SHT_SYMTAB', None))
    assert 'main' in method_list, "Expected to find 'main' method in dummy program"
