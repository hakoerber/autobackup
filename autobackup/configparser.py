import os

class Parser(object):

    COMMENT_CHARS = ('#', ';')
    SECTION_PAIRS = [('[', ']')]
    ELEMENT_PAIRS = [('<', '>')]
    KEY_VALUE_SEPARATORS = ('=', ':')
    
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
            for char in COMMENT_CHARS:
                line = line.split(char)[0]
            if not line:
                continue
            if any([(line[0], line[-1]) == pair for pair in SECTION_PAIRS])
                current_section = line
                self.structure[line] = {}
                continue
            elif any([(line[0], line[-1]) == pair for pair in ELEMENT_PAIRS])
                if not current_section:
                    raise ParseError(lineno, line, "Element without associated section.")
                current_element = line
                self.structure[current_section][current_element] = {}
                continue
            elif any(sep in line for sep in KEY_VALUE_SEPARATORS):
                if any([line.startswith(sep[0] for sep in KEY_VALUE_SEPARATORS]):
                    raise ParseError(lineno, line, "Missing key."
                if sum([line.count(sub) for sub in KEY_VALUE_SEPARATORS]) > 1:
                    raise ParseError(lineno, line, "Ambiguous line.")
                if not current_section:
                    raise ParseError(lineno, line, "Key without associated section.")
                if not current_element or not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line, "Key without associated element.")
                key, value = line.split(filter(lambda sep: sep in line, KEY_VALUE_SEPARATORS)[0])
                if not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line, "Element without associated section")                    
                self.structure[current_section][current_element][key.strip()] = value.strip()
            else:
                raise ParseError(lineno, line, "Invalid line")


            
class ParseError(Exception):
    def __init__(self, line_number, line, message):
        self.line_number = line_number
        self.line = line
        self.message = message

