import fcntl
import os
import errno

def unblock_file_descriptor(path):
    fd = path.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
def read_all(path):
    output = []
    while True:
        line = non_blocking_read(path)
        if not line:
            break
        else:
            output.append(line)
    return "".join(output)


def non_blocking_readline(path):
    try:
        return path.readline()
    except IOError:
        return ""
    
def non_blocking_read(path):
    try:
        return path.read()
    except IOError:
        return ""
