#!/usr/bin/env python
import sys

import configparser
import host
import device
import cron
import backupRepository



def main():
    script_name = sys.argv[0]
    config_path = sys.argv[1]
    if not config_path:
        print "Usage: {} <path to config file>".format(script_name)
    parser = configparser.Parser(config_path,
                                 comment_chars = ('#',),
                                 section_pairs = (('[', ']'),),
                                 element_pairs = (('<', '>'),),
                                 key_value_separators = ('=',)
                                 )
    try:
        parser.read()
    except IOError as e:
        _exit_with(1, "{}: {}".format(config_path, e.message))

    try:
        config_structure = parser.parse()
    except configparser.ParseError as e:
        _exit_with(1, "The configuration file is invalid:\n{}: {} - {}".
                   format(e.line_number, e.line, e.message))

    # TODO Some validation needed.

    hosts = {}
    for key, value in config_structure["[hosts]"].iteritems():
        hosts[key] = host.Host(ip=value["ip"])


    # mapping: name -> (device instance, mountpoint instance)
    devices = {}
    for key, value in config_structure["[devices]"].iteritems():
        device_host = hosts['<' + value["host"] + '>']
        devices[key] = [device.Device(host=device_host,
                                      uuid=value["uuid"],
                                      filesystem=value["filesystem"]
                                      ),
                        device.Mountpoint(host=device_host,
                                          path=value["mountpoint"],
                                          options=value["mount_options"].
                                              split(','),
                                          create=_get_bool(
                                              value["create_mountpoint"])
                                          )
                        ]

    # mapping: name -> (user, from_path, from_device, from_host, to_path,
    # to_device, to_host, crontabs[], max_age, max_count)
    backups = {}
    for key, value in config_structure["[backups]"].iteritems():
        (from_device, from_path, from_host) = _get_path_info(hosts, devices,
                                                             value["from"])
        (to_device,   to_path,   to_host  ) = _get_path_info(hosts, devices,
                                                             value["to"])
        cronstrings = value["create_at"]
        cronjobs = [cron.Cronjob(cronstr) for cronstr in cronstrings.split(';')]

        backups[key] = (value["user"],
                        from_path,
                        from_device,
                        from_host,
                        to_path,
                        to_device,
                        to_host,
                        cronjobs,
                        value["max_age"],
                        value["max_count"]
                        )



    # mount the appropriate devices if they are devices where backup
    # repositories are stored at
    repo_mountpoints = []
    for backup in backups.itervalues():
        backup_device = backup[5][0]
        mountpoint = backup[5][1]
        repo_mountpoints.append(mountpoint)
        if not mountpoint.exists() and not mountpoint.mountpoint_create:
            _exit_with(1,
                "Mountpoint {} does not exist, but shall no be crated".
                format(mountpoint.path))
        if not mountpoint.exists():
            mountpoint.create()
        mountpoint.mount(device=backup_device)

    # read backup repositories and handle their events

    manager = backupRepository.BackupManager()
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

def _backup_required_handler(host, newBackupDirectoryName, sourceHost, sources):
    pass


def _backup_expired_handler(host, expiredBackupDirectoryName):
    pass



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


def _exit_with(exit_code, message):
    print message
    sys.exit(exit_code)


def _get_bool(boolstr):
    if boolstr.lower() in ["true", "1", "yes"]:
        return True
    elif boolstr.lower() in ["false", "0", "no"]:
        return False
    raise ValueError("{} is not a boolean value.".format(boolstr))


if __name__ == '__main__':
    main()
