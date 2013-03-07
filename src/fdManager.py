import fcntl
import os
import errno

def unblockFileDescriptor(path):
    fd = path.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
def readAll(path):
    output = []
    while True:
        line = nonBlockingRead(path)
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
    
def nonBlockingRead(path):
    try:
        return path.read()
    except IOError:
        return ""
