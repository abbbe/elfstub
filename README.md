
To test:

Build dummy program
```
gcc -g src/dummy.c -o tests/dummy
```

Test:
```
$ python -m pytest tests/*.py 
```

Manual tests:

```
# create temp dir, copy libc there, confirm victim program loads it
$ D=$(mktemp -d)
$ ldd `which id`
	linux-vdso.so.1 (0x00007ffef376e000)
	libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (0x00007f0de5761000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f0de5539000)
	libpcre2-8.so.0 => /lib/x86_64-linux-gnu/libpcre2-8.so.0 (0x00007f0de54a2000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f0de57ad000)
$ cp /lib/x86_64-linux-gnu/libc.so.6 $D/
$ LD_LIBRARY_PATH=$D ldd `which id`
	linux-vdso.so.1 (0x00007fff085e0000)
	libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (0x00007f5549495000)
	libc.so.6 => /tmp/tmp.k4qL5HLcOM/libc.so.6 (0x00007f554926d000)
	libpcre2-8.so.0 => /lib/x86_64-linux-gnu/libpcre2-8.so.0 (0x00007f55491d6000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f55494e1000)
```

```
# test looping
$ python src/elf_patcher.py --section SHT_DYNSYM --patch loop $D/libc.so.6
2023-09-08 18:53:05.685 | INFO     | __main__:patch_method:64 - Patched 2746 methods
$ LD_LIBRARY_PATH=$D id
^C
```

```
# test crashing
$ cp /lib/x86_64-linux-gnu/libc.so.6 $D/
$ python src/elf_patcher.py --section SHT_DYNSYM --patch crash $D/libc.so.6
2023-09-08 18:53:55.404 | INFO     | __main__:patch_method:64 - Patched 2746 methods
$ LD_LIBRARY_PATH=$D id
Illegal instruction (core dumped)
```

```
# test patching an unused function - no effect
$ cp /lib/x86_64-linux-gnu/libc.so.6 $D/
$ python src/elf_patcher.py --section SHT_DYNSYM --patch crash --method ioctl $D/libc.so.6 
2023-09-08 18:57:01.055 | INFO     | __main__:patch_method:64 - Patched 1 methods
$ LD_LIBRARY_PATH=$D id
uid=1000(abb) gid=1000(abb) groups=1000(abb),4(adm),20(dialout),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd),120(libvirt)
```

```
# test patching a used function
$ python src/elf_patcher.py --section SHT_DYNSYM --patch crash --method malloc $D/libc.so.6 
2023-09-08 18:57:11.365 | INFO     | __main__:patch_method:64 - Patched 1 methods
$ LD_LIBRARY_PATH=$D id
Illegal instruction (core dumped)
```