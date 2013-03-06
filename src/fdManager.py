import fcntl
import os

def unblockFileDescriptor(path):
    fd = path.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
def readAll(path):
    output = []
    while True:
        line = nonBlockingReadline(path)
        if not line:
            break
        else:
            output.append(line)
    return "".join(output)


def nonBlockingReadline(path):
    try:
        return path.readline()
    except IOError:
        return ""