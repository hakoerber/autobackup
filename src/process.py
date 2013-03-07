import networkConnection
import getpass
import subprocess

CONNECTION = networkConnection.SSHNetworkConnection
CONNECTION_PORT = 22
CONNECTION_TIMEOUT = 10 * 1000
CONNECTION_REMOTE_SHELL = "/bin/bash"
COMMAND_TIMEOUT = 10 * 1000


__connections = []

def execute(host, args, user=None):
    '''
    Executes a command on a specific host as user. Will connect to the host
    and maintain the connection if the host is remote until you explicitly 
    disconnect to host with disconnect(). If the host is the localhost, the
    command will be executed locally.
    :param host: The host on which the command is to be executed.
    :param user: The user as whom to run the command. If no user is given, the command
    will be executed as the current user. If you run the command on the localhost, the
    username must mach the current user, otherwise an exception will be raised.
    :param args: A list of arguments of the command.
    :returns: A touple which contains the exit code of the command, the whole
    output to stdout and the whole output to stderr.
    '''
    if not host.isLocalhost():
        # Connect to a remote host.
        if user == None:
            raise ValueError("A user must be specified for remote connection.")
        connection = __getConnection(host, user)
    
        if not connection.connected():
            connection.connect(CONNECTION_TIMEOUT, CONNECTION_REMOTE_SHELL)
        
            (exitCode, stdoutdata, stderrdata) = connection.execute(args, COMMAND_TIMEOUT)
    
            return (exitCode, stdoutdata, stderrdata)
    else:
        # Just execute the command locally.
        if user != getpass.getuser():
            raise ValueError("Cannot change the user on localhost.")
        process = subprocess.Popen(args, stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, bufsize=-1)
        (stdoutdata, stderrdata) = process.communicate()
        return (process.returncode, stdoutdata, stderrdata)
        
    

def disconnect(host, user=None):
    '''
    Terminates all connections to a host as a specific user. If no user is given,
    all connection to the host will terminated.
    :param host: The host to terminate connections to.
    :param user: The remote username, if None, all connections to the host regardless
    of the remote username will be terminated.
    '''
    for conn in __connections:
        if conn.host == host:
            if user == None or user == conn.user:
                conn.disconnect()
                __connections.remove(conn)
                
def disconnectAll():
    '''
    Disconnects all connection to all hosts.
    '''
    for conn in __connections:
        conn.disconnect()

def isConnected(host, user=None):
    '''
    Determines whether there is an active connection to a host as a specific user. If
    no user is given, determines whether there is any connection to that host.
    :param host: The host to poll.
    :param user: The remote username, if None, all connections regardless of username
    count as a connection to the host.
    :returns: True if there is an active connection to the host as the specified user,
    False otherwise.
    '''
    for conn in __connections:
        if conn.host == host:
            if user == None or user == conn.user:
                return True
    return False        
    
    
def __getConnection(host, user):
    connection = None
    for conn in __connections:
        if conn.host == host and conn.user == user:
            connection = conn
            break
        
    if not connection:
        connection = CONNECTION(host, user, CONNECTION_PORT)
        
    return connection

class fileTypes(object):
    BLOCK_SPECIAL="b"
    DIRECTORY="d"
    REGULAR="f"


def func_fileExists(host, user, path, filetype):
    '''
    
    :param host: Host on which to execute the command.
    :param user: User as whom to execute the command.
    :param path:
    :param filetype:
    :returns: True if the file file exists, false otherwise.
    '''
    args = ["test", "-" + filetype , path]
    (exitCode, _, _) = execute(host, args, user)
    return exitCode == 0


def func_directoryEmpty(host, user, path):
    '''
    
    :param host: Host on which to execute the command.
    :param user: User as whom to execute the command.
    :param path: The path of the directory.
    :returns: True if the directory is empty, false otherwise.
    '''
    return len(func_directoryGetFiles(host, user, path)) == 0
    
    
def func_directoryGetFiles(host, user, path):
    '''
    
    :param host: Host on which to execute the command.
    :param user: User as whom to execute the command.
    :param path: The path of the directory.
    :returns: A touple with the names of all files and subdirectory
    in the directory. Directories can be identified by a succeeding
    slash.
    '''
    args = ["ls", "-A", "-1", "-p", path]
    (exitCode, stdoutdata, _) = execute(host, args, user)
    if exitCode != 0:
        return None
    return stdoutdata.split('\n')


def func_createDirectory(host, user, path, createParents):
    '''
    
    :param host: Host on which to execute the command.
    :param user: User as whom to execute the command.
    :param path: The path of the new directory.
    :returns: A tuple with the exit code, the stdout and stderr data.
    '''
    args = ["mkdir"]
    if createParents:
        args.append("-p")
    args.append[path]
    return execute(host, args, user)

def func_removeDirectory(host, user, path):
    '''
    
    :param host: Host on which to execute the command.
    :param user: User as whom to execute the command.
    :param path: The path of the directory that shall be deleted.
    :returns: A tuple with the exit code, the stdout and stderr data.
    '''
    args = ["rmdir", path]
    return execute(host, args, user)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
