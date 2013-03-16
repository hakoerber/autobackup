import os

class Parser(object):

    #COMMENT_CHARS = ('#', ';')
    #SECTION_PAIRS = [('[', ']')]
    #ELEMENT_PAIRS = [('<', '>')]
    #KEY_VALUE_SEPARATORS = ('=', ':')
    
    def __init__(self, path, comment_chars, section_pairs, element_pairs, 
                 key_value_separators, multiple_keys):
        self.path = path
        self.comment_chars = comment_chars
        self.section_pairs = section_pairs
        self.element_pairs = element_pairs
        self.key_value_separators = key_value_separators
        self.multiple_keys = multiple_keys

        self.text = None
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
            for char in self.comment_chars:
                line = line.split(char)[0]
            if not line:
                continue
            if any([(line[0], line[-1]) == pair for pair in self.section_pairs]):
                current_section = line
                self.structure[line] = {}
                continue
            elif any([(line[0], line[-1]) == pair for pair in self.element_pairs]):
                if not current_section:
                    raise ParseError(lineno, line, "Element without associated section.")
                current_element = line
                self.structure[current_section][current_element] = {}
                continue
            elif any(sep in line for sep in self.key_value_separators):
                if any([line.startswith(sep[0]) for sep in self.key_value_separators]):
                    raise ParseError(lineno, line, "Missing key.")
                if sum([line.count(sub) for sub in self.key_value_separators]) > 1:
                    raise ParseError(lineno, line, "Ambiguous line.")
                if not current_section:
                    raise ParseError(lineno, line, "Key without associated section.")
                if not current_element or not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line, "Key without associated element.")
                key, value = line.split(filter(lambda sep: sep in line, self.key_value_separators)[0])
                if not key.strip():
                    raise ParseError(lineno, line, "Empty key.")
                if key.strip() in self.structure[current_section][current_element]:
                    if self.multiple_keys:
                        values = self.structure[current_section][current_element][key.strip()]
                        if type(values) is str:
                            values = [values]
                        values.append(value.strip())
                        self.structure[current_secion][current_element][key.strip()] = values
                    else:
                        raise ParseError(lineno, line, "Found key twice in the same element.")
                else:
                    if not current_element in self.structure[current_section]:
                        raise ParseError(lineno, line, "Element without associated section")                    
                    self.structure[current_section][current_element][key.strip()] = value.strip()
            else:
                raise ParseError(lineno, line, "Invalid line")
            
        return self.structure


            
class ParseError(Exception):
    def __init__(self, line_number, line, message):
        self.line_number = line_number
        self.line = line
        self.message = message

