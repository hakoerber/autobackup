import socket

def get_localhost():
    return Host(ip="127.0.0.1")

class Host(object):
    """A host in a network, identified by his hostname or an ip address"""
    
    def __init__(self, ip=None, hostname=None):
        if ip == None and hostname == None:
            raise ValueError("Either ip or hostname must be specified.")
        try:
            self._ip = ip if ip != None else socket.gethostbyname(hostname)
        except socket.gaierror:
            raise ValueError("Unknown hostname.")
        
        
    def is_localhost(self):
        return self.ip.startswith("127.")


    def _get_ip(self):
        return self._ip
    ip = property(_get_ip)
    
    
    def get_real_ip(self):
        """
        Returns the ip useable by all hosts in the network, not the localhost
        ip for the local host.
        """
        if not self.is_localhost():
            return self.ip
        else:
            raise NotImplementedError()

    
    # Needs to be overloaded, as a simple comparison of the ips is not 
    # sufficient. All ips in 127.*.*.* refer to the localhost, so for instance 
    # 127.0.0.1 and 27.42.13.37 are the same machine.
    def __eq__(self, other):
        if self.is_localhost() and other.is_localhost():
            return True
        return self.ip == other.ip
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
