class NetworkConnection(object):
    """Abstract base class representing a network connection."""
    
    def __init__(self, Host, port):
        raise NotImplementedError()
    
    def connect(self, user, timeout, remoteShell):
        """Connects to the host as <user> and starts a shell specified by <remoteShell>.
        Raises a timeout error if <timeout> (in milliseconds) exceeded."""
        raise NotImplementedError()
    
    def disconnect(self):
        """Disconnects the connection immediately."""
        raise NotImplementedError()
    
    def execute(self, command, timeout):
        """Executes a <command> on the remote host as user <user>. Raises a timeout error
        if the command did not finish after <timeout> milliseconds."""
        raise NotImplementedError()
    
    def isConnected(self):
        """Returns a bool that specifies whether the connection is established."""
        raise NotImplementedError()
        