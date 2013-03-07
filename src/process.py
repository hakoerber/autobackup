import networkConnection

def execute(host, args):
    '''
    Executes a command on a specific host. Will connect to the host
    and maintain the connection until you explicitly disconnect to 
    host with disconnect().
    :param host: The host on which the command is to be executed.
    :param args: A list of arguments of the command.
    '''
    pass

def disconnect(host):
    '''
    Terminates the connection to a host. If there is no connection to the
    specified host, does nothing.
    :param host: The host to terminate the connection to.
    '''

def isConnected(host):
    '''
    Determines whether there is an active connection to a host.
    :param host: The host to poll.
    :returns: True if there is an active connection to the host, False otherwise.
    '''