import networkConnection

CONNECTION = networkConnection.SSHNetworkConnection
CONNECTION_PORT = 22
CONNECTION_TIMEOUT = 10 * 1000
CONNECTION_REMOTE_SHELL = "/bin/bash"
COMMAND_TIMEOUT = 10 * 1000


__connections = []

def execute(host, user, args):
    '''
    Executes a command on a specific host as user. Will connect to the host
    and maintain the connection until you explicitly disconnect to 
    host with disconnect().
    :param host: The host on which the command is to be executed.
    :param user: The user as whom to run the command.
    :param args: A list of arguments of the command.
    :returns: A touple which contains the exit code of the command, the whole
    output to stdout and the whole output to stderr.
    '''
    connection = __getConnection(host, user)
    
    if not connection.connected():
        connection.connect(CONNECTION_TIMEOUT, CONNECTION_REMOTE_SHELL)
        
    (exitCode, stdoutdata, stderrdata) = connection.execute(args, COMMAND_TIMEOUT)
    
    return (exitCode, stdoutdata, stderrdata)
    

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

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
