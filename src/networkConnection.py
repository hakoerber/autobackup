class NetworkConnection(object):
    """Abstract base class representing a network connection."""
    
    def __init__(self, Host, port):
        raise NotImplementedError()
    
    def connect(self, timeout):
        """Connects to the host and raises a timeout error if <timeout> (in ms) exceeded."""
        raise NotImplementedError()
    
    def disconnect(self):
        """Disconnects the connection immediately."""
        raise NotImplementedError()
    
    def execute(self, user, command):
        """Executes a <command> on the remote host as user <user>."""
        raise NotImplementedError()
        