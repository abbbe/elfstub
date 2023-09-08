import sys
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection

def enumerate_methods(elf_file_path):
    with open(elf_file_path, 'rb') as f:
        elffile = ELFFile(f)
        symbol_tables = [s for s in elffile.iter_sections() if s.header['sh_type'] == 'SHT_SYMTAB']
        for section in symbol_tables:
            for symbol in section.iter_symbols():
                print(symbol.name)

def patch_method(elf_file_path, method_name, patch_type):
    assert patch_type in ['loop', 'crash'], "Unsupported patch type"

    with open(elf_file_path, 'r+b') as f:
        elffile = ELFFile(f)
        section = elffile.get_section_by_name('.text')
        symbols = {sym.name: sym for sym in elffile.get_section_by_name('.symtab').iter_symbols()}
        
        if method_name not in symbols:
            print(f"Method {method_name} not found!")
            return

        symbol = symbols[method_name]
        f.seek(symbol['st_value'])
        
        if patch_type == 'loop':
            # Infinite loop: EB FE
            f.write(b'\xEB\xFE')
        elif patch_type == 'crash':
            # Invalid instruction: UD2 (0F 0B)
            f.write(b'\x0F\x0B')

if __name__ == "__main__":
    action = sys.argv[1]
    elf_file_path = sys.argv[2]

    if action == "enumerate":
        enumerate_methods(elf_file_path)
    elif action == "patch":
        method_name = sys.argv[3]
        patch_type = sys.argv[4]
        patch_method(elf_file_path, method_name, patch_type)
