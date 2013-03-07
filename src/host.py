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

    def __getIP(self):
        return self.__ip
    ip = property(__getIP)
    
