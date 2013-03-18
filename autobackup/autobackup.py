#!/usr/bin/env python
import sys
import getpass

import configparser
import host
import filesystem
import cron
import backuprepository
import process
import path


def main():
    if len(sys.argv) != 2:
        print "Usage: {} <path to config file>".format(sys.argv[0])
        sys.exit(1)

    script_name = sys.argv[0]
    config_path = sys.argv[1]
    parser = configparser.Parser(config_path,
                                 comment_chars = ('#',),
                                 section_pairs = (('[', ']'),),
                                 element_pairs = (('<', '>'),),
                                 key_value_separators = ('=',),
                                 multiple_keys = True)
                                 
    try:
        parser.read()
    except IOError as error:
        _exit_with(1, "{}: {}".format(config_path, error.message))

    try:
        config_structure = parser.parse()
    except configparser.ParseError as error:
        _exit_with(1, "The configuration file is invalid:\n{}: {} - {}".
                   format(error.line_number, error.line, error.message))

    # TODO Some validation needed.

    hosts = {}
    for key, value in config_structure["[hosts]"].iteritems():
        hosts[key] = host.Host(ip=value["ip"])


    # mapping: name -> device instance
    # TODO determine user
    devices = {}
    for key, value in config_structure["[devices]"].iteritems():
        device_host = hosts['<' + value["host"] + '>']
        device_user = value["user"]
        device_mountpoint = filesystem.Mountpoint(
            host=device_host,
            path=value["mountpoint"],
            options=value["mount_options"].split(','),
            create_if_not_existent=_get_bool(value["create_mountpoint"]),
            user=device_user)
        device = filesystem.Device(host=device_host,
            uuid=value["uuid"],
            filesystem=value["filesystem"],
            user=device_user,
            mountpoint=device_mountpoint)
            
        devices[key] = device
        
    # mapping: name -> (repo_location, source_locations[], cronjobs[], max_age,
    # max_count)
    backups = {}
    for key, value in config_structure["[backups]"].iteritems():
        repo_location = _parse_full_location(value["to"], hosts, devices)
        source_locations = [_parse_full_location(source_string, hosts, devices)
            for source_string in value["from"]]
        cronjobs = [cron.Cronjob(cronstr) for 
            cronstr in value["create_at"]]

        backups[key] = (repo_location,
                        source_locations,
                        cronjobs,
                        value["max_age"],
                        value["max_count"])


    # get all devices where backup repositories are stored at
    repo_devices = []
    for backup in backups.itervalues():
        repo_location = backup[0]
        if repo_location.device is not None:
            repo_devices.append(repo_location.device)


    # mount all these devices
    for repo_device in repo_devices:
        repo_devices.mount()
        
        
    # read backup repositories and handle their events
    backup_repositories = []
    for backup in backups.itervalues():
        repository_location = backup[0]
        directories = process.func_directory_get_files(
            host=repository_location.host,
            user=repository_location.user,
            path=repository_location.path)
        backup_repositories.append(
            backuprepository.BackupRepository(
                    repository_location=repository_location,
                    directories=directories,
                    source_locations=backup[1],
                    interval=cronjobs,
                    max_age=backup[3],
                    max_count=backup[4]))
                    
    manager = backuprepository.BackupManager(backup_repositories)
    manager.backup_required += _backup_required_handler
    manager.backup_expired  += _backup_expired_handler

    # Now we have to handle all backups that were required or expired while the
    # programm was not running
    manager.check_all_backups()
    
    # Now let's start scheduling and waiting for events
    manager.start_scheduling()

    # unmount the devices with backup repositories again
    for repo_device in repo_devices:
        repo_device.unmount()


def _backup_required_handler(repository_location, source_locations, 
                             latest_backup):
    # Mount the appropriate. devices if necessary ...
    if repository_location.device != None:
        repository_location.device.mount()
    for source_location in source_locations:
        if source_location.device != None:
            source_location.device.mount()
        
    # Now we just need to copy the sources to the new directory.
    process.func_create_backup(source_locations, repository_location, 
                               latest_backup)
    
    # And unmount all devices again.          
    if repository_location.device != None:
        repository_location.device.unmount()
    for source_location in source_locations:
        if source_location.device != None:
            source_location.device.unmount()

                               
def _backup_expired_handler(backup_location):
    process.func_remote_directory(
        host=backup_location.host, 
        path=backup_location.path,
        user=backup_location.user,
        recursive=False)#True # I am afraid.


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
    except KeyError as error:
        print "Unknown device {}.".format(temp[0])
        sys.exit(1)
    if temp[2]:
        try:
            temp[2] = hosts['<' + temp[2] + '>']
        except KeyError as error:
            print "Unknown host {}.".format(temp[2])
            sys.exit(1)
    else:
        temp[2] = host.get_localhost()

    return temp


def _exit_with(exit_code, message):
    print message
    sys.exit(exit_code)


def _get_bool(boolstr):
    if boolstr.lower() in ["true", "1", "yes", "wouldbenice"]:
        return True
    elif boolstr.lower() in ["false", "0", "no", "idareyou"]:
        return False
    raise ValueError("{} is not a boolean value.".format(boolstr))


def _parse_full_location(string, hosts, devices):
    rest = string
    # when no user, use current one!
    # the location string has the following format:
    # [[<user>]@<host>:]<path|subdir>[$<device>]
    
    # get the device:
    parts = rest.split('$')
    (rest, device) = (parts[0], devices["<" + parts[1] + '>'] 
                                if len(parts) == 2 else None)

    # get the "user@host" part and parse it
    parts = rest.split(':')
    (rest, user_host) = (parts[1] if len(parts) == 2 else parts[0],
                         parts[0] if len(parts) == 2 else "")
    parts = user_host.split('@')
    (l_user, l_host) = (parts[0] if len(parts) == 2 else getpass.getuser(),
                        hosts['<' + parts[1] + '>'] if len(parts) == 2 
                            else host.get_localhost())
                    
    # so the rest must be the path
    full_path = rest
                             
    return path.FullLocation(l_user, l_host, full_path, device)

    
if __name__ == '__main__':
    main()
