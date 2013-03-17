#!/usr/bin/env python
import sys

import configparser
import host
import filesystem
import cron
import backuprepository
import process


def main():
    script_name = sys.argv[0]
    config_path = sys.argv[1]
    if not config_path:
        print "Usage: {} <path to config file>".format(script_name)
    parser = configparser.Parser(config_path,
                                 comment_chars = ('#',),
                                 section_pairs = (('[', ']'),),
                                 element_pairs = (('<', '>'),),
                                 key_value_separators = ('=',),
                                 multiple_keys = True
                                 )
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


    # mapping: name -> (device instance, mountpoint instance)
    # TODO determine user
    devices = {}
    for key, value in config_structure["[devices]"].iteritems():
        device_host = hosts['<' + value["host"] + '>']
        devices[key] = [filesystem.Device(host=device_host,
                                          uuid=value["uuid"],
                                          filesystem=value["filesystem"],
                                          user=None),
                        filesystem.Mountpoint(host=device_host,
                                              path=value["mountpoint"],
                                              options=value["mount_options"].
                                                  split(','),
                                              create_if_not_existent=_get_bool(
                                                  value["create_mountpoint"]),
                                              user=None)]

    # mapping: name -> (repo_location, source_locations[], cronjobs[], max_age,
    # max_count)
    backups = {}
    for key, value in config_structure["[backups]"].iteritems():
        repo_location = _parse_full_location(hosts, devices, value["to"])
        source_locations = [_get_path_info(hosts, devices, source_string) for
            source_string in value["from"]]
        cronjobs = [cron.Cronjob(cronstr) for 
            cronstr in value["create_at"].split(';')]

        backups[key] = (repo_location,
                        source_locations,
                        cronjobs,
                        value["max_age"],
                        value["max_count"])


    # mount the appropriate devices if they are devices where backup
    # repositories are stored at
    repo_mountpoints = []
    for backup in backups.itervalues():
        repo_location = backup[0]
        if repo_location.device is not None:
            repo_location.mount()
                        
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

    # unmount the devices with backup repositories again
    for mountpoint in repo_mountpoints:
        mountpoint.unmount()

    # wait ...

    # if backup needs to be created or deleted:
    # mount appropriate devices if necessary
    # create backup
    # unmount devices

def _backup_required_handler(repository_location, source_locations, 
                             latest_backup):
    # We just need to copy the sources to the new directory.
    process.func_create_backup(source_locations, repository_location, 
                               latest_backup)


def _backup_expired_handler(backup_location):
    process.func_remote_directory(
        user=backup_location.user, 
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


def _parse_full_location(string, hosts, devices):#
    # when no user, use current one!
    # TODO implement
    return None


if __name__ == '__main__':
    main()




