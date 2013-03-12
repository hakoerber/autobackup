import getpass
import subprocess

import networkConnection

CONNECTION = networkConnection.SSHNetworkConnection
CONNECTION_PORT = 22
CONNECTION_TIMEOUT = 10 * 1000
CONNECTION_REMOTE_SHELL = "/bin/bash"
COMMAND_TIMEOUT = 10 * 1000


__connections = []

def execute(host, args, user=None):
    """
    Executes a command on a specific host as user. Will connect to the host and
    maintain the connection if the host is remote until you explicitly  
    disconnect to host with disconnect(). If the host is the localhost, the
    command will be executed locally.
    :param host: The host on which the command is to be executed.
    :type host: Host instance
    :param user: The user as whom to run the command. If no user is given, the 
    command will be executed as the current user. If you run the command on the 
    localhost, the username must mach the current user, otherwise an exception 
    will be raised.
    :type user: User instance
    :param args: A list of arguments of the command.
    :type args: list
    :returns: A tuple which contains the exit code of the command, the whole
    output to stdout and the whole output to stderr.
    :rtype: tuple
    :raises: ValueError when host is remote and no user is specified, or when
    host is not remote and user is not the current user.
    """
    if not host.is_localhost():
        # Connect to a remote host.
        if user == None:
            raise ValueError("A user must be specified for remote connection.")
        connection = _getConnection(host, user)
    
        if not connection.connected():
            connection.connect(CONNECTION_TIMEOUT, CONNECTION_REMOTE_SHELL)
        
            (exitCode, stdoutdata, stderrdata) = connection.execute(
                                                     args, 
                                                     COMMAND_TIMEOUT)
    
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
    """
    Terminates all connections to a host as a specific user. If no user is 
    given, all connection to the host will terminated.
    :param host: The host to terminate connections to.
    :type host: Host instance
    :param user: The remote username, if None, all connections to the host 
    regardless of the remote username will be terminated.
    :type user: string
    """
    for conn in __connections:
        if conn.host == host:
            if user == None or user == conn.user:
                conn.disconnect()
                __connections.remove(conn)
          
                
def disconnect_all():
    """
    Disconnects all connections to all hosts.
    """
    for conn in __connections:
        conn.disconnect()


def is_connected(host, user=None):
    """
    Determines whether there is an active connection to a host as a specific 
    user. If no user is given, determines whether there is any connection to 
    that host.
    :param host: The host to poll.
    :type host: Host instance
    :param user: The remote username, if None, all connections regardless of 
    username count as a connection to the host.
    :type user: string
    :returns: True if there is an active connection to the host as the specified
    user, False otherwise.
    :rtype: bool
    """
    for conn in __connections:
        if conn.host == host:
            if user == None or user == conn.user:
                return True
    return False        
    
    
def _getConnection(host, user):
    connection = None
    for conn in __connections:
        if conn.host == host and conn.user == user:
            connection = conn
            break
        
    if not connection:
        connection = CONNECTION(host, user, CONNECTION_PORT)
        
    return connection


class fileTypes(object):
    ANY="e"
    BLOCK_SPECIAL="b"
    DIRECTORY="d"
    REGULAR="f"


def func_file_exists(host, user, path, filetype):
    """
    Function that tests whether a file exists and is or the given type.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: User as whom to execute the command.
    :type user: string    
    :param path: The path of the file.
    :type path: string
    :param filetype: The type of the file.
    :type filetype: fileTypes enum member
    :returns: True if the file file exists, false otherwise.
    :rtype: bool
    """
    args = ["test", "-" + filetype , path]
    (exitCode, _, _) = execute(host, args, user)
    return exitCode == 0


def func_directory_empty(host, user, path):
    """
    Function that tests whether a given directory is empty.
    :param host: Host on which to execute the command.  
    :type host: Host instance
    :param user: User as whom to execute the command.
    :type user: string    
    :param path: The path of the directory.
    :type path: string
    :returns: True if the directory is empty, false otherwise.
    :rtype: bool
    """
    return len(func_directory_get_files(host, user, path)) == 0
    
    
def func_directory_get_files(host, user, path):
    """
    Function that returns all elements of a directory.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: User as whom to execute the command.
    :type user: string
    :param path: The path of the directory.
    :type path: string
    :returns: A tuple with the names of all files and subdirectory in the 
    directory. Directories can be identified by a succeeding slash.
    :rtype: tuple
    """
    args = ["ls", "-A", "-1", "-p", path]
    (exitCode, stdoutdata, _) = execute(host, args, user)
    if exitCode != 0:
        return None
    return stdoutdata.split('\n')


def func_create_directory(host, user, path, createParents):
    """
    Function to create a directory. 
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: User as whom to execute the command.
    :type user: string
    :param path: The path of the new directory.
    :type path: string
    :returns: A tuple with the exit code, the stdout and stderr data.
    :rtype: tuple
    """
    args = ["mkdir"]
    if createParents:
        args.append("-p")
    args.append[path]
    return execute(host, args, user)


def func_remove_directory(host, user, path):
    """
    Function to remove a directory.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: User as whom to execute the command.
    :type user: string
    :param path: The path of the directory that shall be deleted.
    :type path: string
    :returns: A tuple with the exit code, the stdout and stderr data.
    :rtype: tuple
    """
    args = ["rmdir", path]
    return execute(host, args, user)
    
