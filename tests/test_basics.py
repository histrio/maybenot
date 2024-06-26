from common import maybe
from ptrace.syscall import SYSCALL_PROTOTYPES

from maybenot import SYSCALL_FILTERS


def test_syscall_filters():
    # Verify that every filtered syscall is known to python-ptrace
    for filter_scope in SYSCALL_FILTERS:
        for syscall in SYSCALL_FILTERS[filter_scope]:
            assert syscall in SYSCALL_PROTOTYPES


def test_no_operations():
    assert maybe("true") == "maybenot has not detected any file system operations from true."
