import pytest
import subprocess
import time
from src.elf_patcher import patch_method
from src.cpu_util import get_process_cpu_usage

BINARY_PATH = "tests/usr-bin-id"
FUNCTION_TO_PATCH = "function_name_in_binary"

def test_hang():
    # Make a backup and patch the binary to hang
    BINARY_PATH_HANG = BINARY_PATH + '.hang'
    subprocess.run(['cp', BINARY_PATH, BINARY_PATH_HANG])
    patch_method(BINARY_PATH_HANG, FUNCTION_TO_PATCH, 'loop')

    # Run the binary in the background
    p = subprocess.Popen([BINARY_PATH_HANG])
    time.sleep(2)  # Allow some time for the function to be called

    # Check CPU utilization
    cpu_usage = get_process_cpu_usage(p.pid)
    p.terminate()  # Terminate the process

    assert cpu_usage > 90, "Expected high CPU usage, indicating a hang"

def test_die():
    # Make a backup and patch the binary to crash
    BINARY_PATH_DIE = BINARY_PATH + '.die'
    subprocess.run(['cp', BINARY_PATH, BINARY_PATH_DIE])
    patch_method(BINARY_PATH_DIE, FUNCTION_TO_PATCH, 'crash')

    # Run the binary and capture the exit code
    result = subprocess.run([BINARY_PATH_DIE])
    
    assert result.returncode != 0, "Expected non-zero exit code, indicating a crash"
