import sys
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")

import argparse
from elftools.elf.elffile import ELFFile

def is_function_symbol(symbol):
    """ Determine if the symbol is a function """
    return symbol['st_info']['type'] == 'STT_FUNC'

def is_within_text_section(symbol, elffile):
    """ Determine if the symbol is within the .text section """
    text_section = elffile.get_section_by_name('.text')
    start = text_section['sh_addr']
    end = start + text_section['sh_size']
    symbol_start = symbol['st_value']
    symbol_end = symbol_start + symbol['st_size']

    return start <= symbol_start and symbol_end <= end

def enumerate_symbols(elf_file_path, section_type, symbol_name=None, read_only=False):
    """
        This iterator yields tuples (f, symbol)
    """
    if read_only:
        mode = 'rb'
    else:
        mode = 'r+b'

    with open(elf_file_path, mode) as f:
        elffile = ELFFile(f)

        for section in elffile.iter_sections():
            if section.header['sh_type'] != section_type:
                logger.debug(f"skipping sh_type '{section.header['sh_type']}' != '{section_type}'")
                continue
            
            for symbol in section.iter_symbols():
                if symbol_name is not None and symbol_name != symbol.name:
                    continue
                if not is_function_symbol(symbol) or not is_within_text_section(symbol, elffile):
                    continue
                yield f, symbol

def patch_method(elf_file_path, section_type, method_name, patch_type):
    patch_count = 0

    for f, symbol in enumerate_symbols(elf_file_path, section_type, method_name):
        f.seek(symbol['st_value'])
        
        if patch_type == 'loop':
            # Infinite loop: EB FE
            f.write(b'\xEB\xFE')
        elif patch_type == 'crash':
            # Invalid instruction: UD2 (0F 0B)
            f.write(b'\x0F\x0B')
        
        logger.debug(f"patched {symbol.name} for {patch_type} seek {symbol['st_value']}")
        patch_count += 1
            
    logger.info(f"Patched {patch_count} methods")
    return patch_count

def main():
    parser = argparse.ArgumentParser(description='Patch or enumerate methods in ELF binaries.')
    parser.add_argument('--section', choices=['SHT_DYNSYM', 'SHT_SYMTAB'], required=True, \
                        help='Section to target (SHT_DYNSYM or SHT_SYMTAB)')

    parser.add_argument('--method', \
                        help='Method to target (if not specified - target all)')
    
    # Define a mutually exclusive group for --enumerate and --patch
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--enumerate', action='store_true', help='Enumerate methods without patching')
    group.add_argument('--patch', choices=['loop', 'crash'], help='Patch type (loop or crash)')

    parser.add_argument('ELF_PATH', type=str, help='Path to the ELF binary')
    args = parser.parse_args()

    if args.enumerate:
        for _, symbol in enumerate_symbols(args.ELF_PATH, args.section):
            print(symbol.name)
    else:
        patch_method(args.ELF_PATH, args.section, args.method, args.patch)

if __name__ == "__main__":
    main()
