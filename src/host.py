import socket

class Host(object):
    """A host in a network, identified by his hostname or an ip address"""
    
    def __init__(self, ip=None, hostname=None):
        if ip == None and hostname == None:
            raise TypeError("Either ip or hostname must be specified.")
        try:
            self.__ip = ip if ip != None else socket.gethostbyname(hostname)
        except socket.gaierror:
            raise ValueError("Unknown hostname.")
        
    def isLocalhost(self):
        return self.ip.startswith("127.")

    def __getIP(self):
        return self.__ip
    ip = property(__getIP)
    
    # Needs to be overloaded, as a simple comparison of the ips is not sufficient.
    # All ips in 127.*.*.* refer to the localhost, so for instance 127.0.0.1 and
    # 127.42.13.37 are the same machine.
    def __eq__(self, other):
        if self.isLocalhost() and other.isLocalhost():
            return True
        return self.ip == other.ip
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
