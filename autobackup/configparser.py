class Parser(object):
    
    def __init__(self, path):
        self.path = path
        self.text = None
        # list of tuples: (name, ip, user)
        self.hosts = []
    
    def read(self):
        self.text = open(self.path).read()
    
    def parse(self):
        if self.text is None:
            self.read()
            
        for line in self.text:
            line = line.strip()
            # skip empty lines
            if not line:
                continue
            # skip comments
            if line.startswith('#'):
                continue
            
            # omit comments starting in the middle of the line
            line = line.split('#')[0]
            
            if not line == "[Hosts]":
                raise ParseError()
            
            
            
            
            
            
            
class ParseError(Exception):
    def __init__(self, message):
        self.message = message
            