import pytest
import subprocess
import time
from src.elf_patcher import patch_method
from src.cpu_util import get_process_cpu_usage

BINARY_PATH = "tests/dummy"
LOOP_TIMEOUT = 3

@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield  # this is where the test function will execute
    return
    # Cleanup after test
    for suffix in ['.loop', '.crash']:
        try:
            subprocess.run(['rm', BINARY_PATH + suffix])
        except Exception as e:
            print(f"Error removing {BINARY_PATH + suffix}: {e}")

def _test_loop(func_name):
    # Make a backup and patch the binary to loop
    BINARY_PATH_LOOP = BINARY_PATH + '.loop'
    subprocess.run(['cp', BINARY_PATH, BINARY_PATH_LOOP])
    patch_method(BINARY_PATH_LOOP, 'SHT_SYMTAB', func_name, 'loop')

    # Run the binary in the background
    p = subprocess.Popen([BINARY_PATH_LOOP])
    time.sleep(LOOP_TIMEOUT)  # Allow some time for the function to be called

    # Check CPU utilization
    cpu_usage = get_process_cpu_usage(p.pid)
    p.terminate()  # Terminate the process

    assert cpu_usage > 90, "Expected high CPU usage, indicating a loop"

def _test_crash(func_name):
    # Make a backup and patch the binary to crash
    BINARY_PATH_CRASH = BINARY_PATH + '.crash'
    subprocess.run(['cp', BINARY_PATH, BINARY_PATH_CRASH])
    patch_method(BINARY_PATH_CRASH, 'SHT_SYMTAB', func_name, 'crash')

    # Run the binary and capture the exit code
    result = subprocess.run([BINARY_PATH_CRASH])
    
    assert result.returncode != 0, "Expected non-zero exit code, indicating a crash"

def test_main_crash():
    _test_crash('main')

def test_main_loop():
    _test_loop('main')


def test_all_crash():
    _test_crash(None)

def test_all_loop():
    _test_loop(None)
