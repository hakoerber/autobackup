import fcntl
import os

def unblock_file_descriptor(path):
    file_descriptor = path.fileno()
    file_control = fcntl.fcntl(file_descriptor, fcntl.F_GETFL)
    fcntl.fcntl(file_descriptor, fcntl.F_SETFL, file_control | os.O_NONBLOCK)
    
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
