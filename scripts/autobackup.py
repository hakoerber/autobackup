#!/usr/bin/env python
import sys

import configparser
import host



def main():
    
    config_path = "../config/txt/config.example.cfg"
    parser = configparser.Parser(config_path, 
                                 comment_chars = ('#',),
                                 section_pairs = (('[', ']'),),
                                 element_pairs = (('<', '>'),),
                                 key_value_separators = ('=',)
                                 )
    try:
        parser.read()
    except IOError as e:
        print("{}: {}".format(config_path, e.message))
        sys.exit(1)
    
    try:
        config_structure = parser.parse()
    except configparser.ParseError as e:
        print("The configuration file is invalid:\n{}: {} - {}".
              format(e.line_number, e.line, e.message))
                
    # Some validation needed.

    hosts = {}
    for element in config_structure["[hosts]"]:
        hosts[element] = host.Host(ip=config_structure["[hosts]"][element]["ip"])
    for name, hostobj in hosts.iteritems():
        print("Host with name {} has ip {}".format(name, hostobj.ip))
    
        
    
    
    
    
        
    

    






    
if __name__ == '__main__':
    main()
