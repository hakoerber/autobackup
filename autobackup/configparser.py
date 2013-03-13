import os

class Parser(object):

    COMMENT_CHAR  = '#'
    SECTION_START = '['
    SECTION_END   = ']'
    ELEMENT_START = '<'
    ELEMENT_END   = '>'
    KEY_VALUE_SEPARATOR = '="
    
    def __init__(self, path):
        self.path = path
        self.text = None
        # dictionary of (string, dictionary of (string, dictionary of (string, string))):
        # outer list: sections name and elements
        # inner list: element names and sections
        # dictionary: key-value pairs of the element
        self.structure = dict()
    

    def read(self):
        if not os.path.isfile(self.path):
            raise IOError("File not found.")
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
            if line.startswith(COMMENT_CHAR):
                continue
            
            # omit comments starting in the middle of the line
            line = line.split(COMMENT_CHAR)[0]

            
            if line.startswith(SECTION_START) and line.endswith(SECTION_END):
                current_section = line
                self.structure[line] = {}
                continue
            if line.startswith(ELEMENT_START) and line.endswith(ELEMENT_END):
                if not current_section:
                    raise ParseError(lineno, line, "Element without associated section.")
                current_element = line
                self.structure[current_section][line] = {}
                continue
            if '=' in line[1:-1]:
                if not current_section:
                    raise ParseError(lineno, line, "Key without associated section.")
                if not current_element or not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line, "Key without associated element.")
                key_value = line.split(KEY_VALUE_SEPARATOR)
                if len(key_value) != 2:
                    raise ParseError(line, "Invalid line")
                key, value = key_value
                key = key.strip()
                value = value.strip()
                if not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line, "Element without associated section")                    
                self.structure[current_section][current_element][key] = valuepr
            else:
                raise ParseError(lineno, line, "Invalid line")


            
class ParseError(Exception):
    def __init__(self, line_number, line, message):
        self.line_number = line_number
        self.line = line
        self.message = message
        
            
