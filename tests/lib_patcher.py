import pytest
import subprocess
import time
import os
import shutil
from src.elf_patcher import enumerate_symbols, patch_method
from src.cpu_util import get_process_cpu_usage
from src.config import LIB_PATH, LIBC_FILENAME

DUMMY_PROGRAM_PATH = "tests/dummy"

@pytest.fixture
def setup_temp_dir():
    temp_dir = "/tmp/patched_lib"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    shutil.copy(LIB_PATH, temp_dir)
    yield temp_dir
    #shutil.rmtree(temp_dir)

def test_all_loop(setup_temp_dir):
    temp_dir = setup_temp_dir
    patch_method(os.path.join(temp_dir, LIBC_FILENAME), 'SHT_DYNSYM', None, 'loop')

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = temp_dir

    # Run the dummy program in the background with patched libc
    p = subprocess.Popen([DUMMY_PROGRAM_PATH], env=env)
    time.sleep(2)  # Allow some time for the functions to be called

    # Check CPU utilization
    cpu_usage = get_process_cpu_usage(p.pid)
    p.terminate()  # Terminate the process

    assert cpu_usage > 90, "Expected high CPU usage, indicating a loop"

def test_all_crash(setup_temp_dir):
    temp_dir = setup_temp_dir
    patch_method(os.path.join(temp_dir, LIBC_FILENAME), 'SHT_DYNSYM', None, 'crash')

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = temp_dir

    # Run the dummy program and capture the exit code
    result = subprocess.run([DUMMY_PROGRAM_PATH], env=env)

    assert result.returncode != 0, "Expected non-zero exit code, indicating a crash"


def test_unused_nocrash(setup_temp_dir):
    temp_dir = setup_temp_dir
    n = patch_method(os.path.join(temp_dir, LIBC_FILENAME), 'SHT_DYNSYM', 'ioctl', 'crash')
    assert n == 1, "Expected to patch one and only one function"

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = temp_dir

    # Run the dummy program and capture the exit code
    result = subprocess.run([DUMMY_PROGRAM_PATH], env=env)

    assert result.returncode == 0, "Expected zero exit code, indicating normal execution"

def test_used_crash(setup_temp_dir):
    temp_dir = setup_temp_dir
    n = patch_method(os.path.join(temp_dir, LIBC_FILENAME), 'SHT_DYNSYM', 'malloc', 'crash')
    assert n == 1, "Expected to patch one and only one function"

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = temp_dir

    # Run the dummy program and capture the exit code
    result = subprocess.run([DUMMY_PROGRAM_PATH], env=env)

    assert result.returncode != 0, "Expected non-zero exit code, indicating a crash"
