#!/usr/bin/env python
import sys

import configparser
import host
import device



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
    for key, value in config_structure["[hosts]"].iteritems():
        hosts[key] = host.Host(ip=value["ip"])


    devices = {}
    for key, value in config_structure["[devices]"].iteritems():
        devices[key] = device.Device(host=hosts['<' + value["host"] + '>'],
                                     uuid=value["uuid"],
                                     filesystem=value["filesystem"])

    # mapping: name -> (user, from_path, from_device, from_host, to_path, to_device, to_host)
    backups = {}
    for key, value in config_structure["[backups]"].iteritems():
        (from_path, from_device, from_host) = _get_path_info(hosts, devices, value["from"])
        (to_path,   to_device,   to_host  ) = _get_path_info(hosts, devices, value["to"])
        backups[key] = (value["user"],
                        from_path,
                        from_device,
                        from_host,
                        to_path,
                        to_device,
                        to_host)

    # mount the appropriate devices if they are devices where backup repositories are stored at,
    # get the needed information and unmount again

    # read backup repositories

    # wait ...

    # if backup needs to be created or deleted:
    # mount appropriate devices if necessary
    # create backup
    # unmount devices





def _get_path_info(hosts, devices, path):
    temp = []
    rest = path
    if ":" in rest:
        temp.append(path.split(":")[0])
        rest = rest.split(":")[1]
    else:
        temp.append(None)
    if not "@" in rest:
        temp.extend([rest, None])
    else:
        temp.extend([rest.split("@")[0], rest.split("@")[1]])
    try:
        temp[0] = devices['<' + temp[0] + '>'] if temp[0] else None
    except KeyError as e:
        print "Unknown device {}.".format(path_device)
        sys.exit(1)
    try:
        temp[2] = hosts['<' + temp[2] + '>'] if temp[2] else host.get_localhost()
    except KeyError as e:
        print "Unknown host {}.".format(path_host)
        sys.exit(1)
    return temp
                        
    
        
    
    
    
    
        
    

    






    
if __name__ == '__main__':
    main()
