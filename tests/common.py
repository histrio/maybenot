import os
import shlex
import sys
from contextlib import contextmanager
from io import StringIO
from os import chdir, getcwd

from maybenot.maybe import main as maybe_main


def maybe(arguments):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = string_io = StringIO()
    maybe_main(shlex.split(arguments))
    assert sys.stdout == sys.stderr == string_io
    sys.stdout, sys.stderr = old_stdout, old_stderr
    return string_io.getvalue().rstrip("\n")


# Source: http://stackoverflow.com/a/431747
@contextmanager
def working_directory(directory):
    original_directory = getcwd()
    try:
        chdir(str(directory))
        yield
    finally:
        chdir(original_directory)


@contextmanager
def umask(mask):
    original_mask = os.umask(mask)
    try:
        yield
    finally:
        os.umask(original_mask)


@contextmanager
def remove(f):
    try:
        yield f
    finally:
        if f.check():
            f.remove()
            assert not f.check()


def tf(directory, command, output, operation, test):
    def t_file(f, f_arg):
        # File does not yet exist (will be created when written to)
        assert not f.check()
        f.write("abc")
        assert f.check()
        assert test(f)
        cmd = command.format(f=f_arg)
        # Test for expected output and provided test condition
        assert maybe("-l -- " + cmd) == output.format(f=f)
        assert test(f)
        # Test for negation of the above if operation is explicitly allowed
        assert maybe(("-l -a %s -- " % operation) + cmd).startswith("maybenot has not detected")
        assert not test(f)

    def t_name(name):
        # Absolute path
        with remove(directory.join(name)) as f:
            t_file(f, str(f))
        # Relative path
        with remove(directory.join(name)) as f:
            t_file(f, name)
        with remove(directory.mkdir("dirname")) as subdirectory:
            # Relative path in subdirectory
            with remove(subdirectory.join(name)) as f:
                t_file(f, "dirname/" + name)
            with working_directory(subdirectory):
                # Relative path in parent directory
                with remove(directory.join(name)) as f:
                    t_file(f, "../" + name)

    with working_directory(directory):
        t_name("filename")
        # Whitespace in filename
        t_name("file name")
        # Unicode in filename
        t_name(u"file name \u2713")
