from loguru import logger
import argparse
from elftools.elf.elffile import ELFFile

def enumerate_symbols(elf_file_path, section_type, symbol_name):
    """
        This iterator yields tuples (f, symbol)
    """
    with open(elf_file_path, 'r+b') as f:
        elffile = ELFFile(f)

        for section in elffile.iter_sections():
            if section.header['sh_type'] != section_type:
                logger.debug(f"skipping sh_type '{section.header['sh_type']}' != '{section_type}'")
                continue
            
            for symbol in section.iter_symbols():
                if symbol_name is not None and symbol_name != symbol.name:
                    continue
                yield f, symbol

def patch_method(elf_file_path, section_type, method_name, patch_type):
    patch_count = 0

    for f, symbol in enumerate_symbols(elf_file_path, section_type, method_name):
        if not symbol['st_value']:
            continue # WTF?

        f.seek(symbol['st_value'])
        
        if patch_type == 'loop':
            # Infinite loop: EB FE
            f.write(b'\xEB\xFE')
        elif patch_type == 'crash':
            # Invalid instruction: UD2 (0F 0B)
            f.write(b'\x0F\x0B')
        
        logger.info(f"patched {symbol.name} for {patch_type} seek {symbol['st_value']}")
        patch_count += 1
            
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
