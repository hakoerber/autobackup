class Location(object):
    def __init__(self, user, host, path):
        self.user = user
        self.path = path
        self.host = host
        
        
    def get_ssh_string(self):
        if self.host.is_localhost():
            return self.path
        else:
            return "{0}@{1}:{2}".format(self.user, self.host.ip, self.path)



class FullLocation(Location):
    def __init__(self, user, host, path, device):
        super(FullLocation, self).__init__(user, host, path)
        self.device = device
