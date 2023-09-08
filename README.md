
To test:

Build dummy program
```
gcc -g src/dummy.c -o tests/dummy
```

Test:
```
$ python -m pytest tests/elf_patcher.py 
======================================= test session starts =======================================
platform linux -- Python 3.10.12, pytest-7.4.2, pluggy-1.3.0
rootdir: /home/abb/elfstub
collected 2 items                                                                                 

tests/elf_patcher.py ..                                                                     [100%]

======================================== 2 passed in 3.20s ========================================
```

Manual tests:
```
(venv) abb@fw6b:~/elfstub$ ./tests/dummy
(venv) abb@fw6b:~/elfstub$ ./tests/dummy.die 
Illegal instruction (core dumped)
(venv) abb@fw6b:~/elfstub$ ./tests/dummy.hang 
^C
```