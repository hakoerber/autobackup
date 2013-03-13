class Parser(object):
    
    def __init__(self, path):
        self.path = path
        self.text = None
        # dictionary of (string, dictionary of (string, dictionary of (string, string))):
        # outer list: sections name and elements
        # inner list: element names and sections
        # dictionary: key-value pairs of the element
        self.structure = dict()
    

    def read(self):
        self.text = open(self.path).read()
    

    def parse(self):
        if self.text is None:
            self.read()

        current_section = ""
        current_element = ""

        lineno = 0
            
        for line in self.text.split('\n'):
            lineno += 1
            line = line.strip()
            # skip empty lines
            if not line:
                continue
            # skip comments
            if line.startswith('#'):
                continue
            
            # omit comments starting in the middle of the line
            line = line.split('#')[0]

            
            if line.startswith('[') and line.endswith(']'):
                current_section = line
                print "adding new section: " + line
                self.structure[line] = {}
                print self.structure
                continue
            if line.startswith('<') and line.endswith('>'):
                if not current_section:
                    raise ParseError(lineno, line, "Element without associated section.")
                current_element = line
                print "adding new element {} in section {}".format(line, current_section)
                self.structure[current_section][line] = {}
                print self.structure
                continue
            if '=' in line[1:-1]:
                if not current_section:
                    raise ParseError(lineno, line, "Key without associated section.")
                if not current_element or not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line, "Key without associated element.")
                key_value = line.split('=')
                if len(key_value) != 2:
                    raise ParseError(line, "Invalid line")
                key, value = key_value
                key = key.strip()
                value = value.strip()
                if not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line, "Element without associated section")                    
                print "adding new key {} with value {} in element {} in section {}".format(
                    key, value, current_element, current_section)
                self.structure[current_section][current_element][key] = value
                print self.structure
            else:
                raise ParseError(lineno, line, "Invalid line")


            
class ParseError(Exception):
    def __init__(self, line_number, line, message):
        self.line_number = line_number
        self.line = line
        self.message = message
        
            
