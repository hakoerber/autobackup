#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2013 Hannes Körber <hannes.koerber@gmail.com>
#
# This file is part of autobackup.
#
# autobackup is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# autobackup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import getpass

import apscheduler.scheduler as scheduler #@UnresolvedImport

import configparser
import host
import filesystem
import cron
import backuprepository
import process
import path

def make_full_location(c_user, c_host, c_path, c_device):
    # extract user from c_user
    if c_user is None:
        user = getpass.getuser()
    else:
        user = c_user

    # construct Host object from c_host
    c_host = list(c_host.values())[0]
    if c_host is None:
        host = None
    else:
        if c_host[0] is not None:
            host = host.Host(ip=c_host[0])
        else:
            host = host.Host(hostname=c_host[1])

    # no changes necessary
    path = c_path

    # construct Device object from c_device
    c_device = list(c_device.values())[0]
    if c_device is None:
        device = None
    else:
        (uuid, fs, mountpoint) = c_device
        if host is None:
            device_host = host.get_localhost()
        else:
            device_host = host
        device = filesystem.Device(host=device_host, uuid=uuid,
                                    filesystem=fs, user=user,
                                    mountpoint=mountpoint)

    return path.FullLocation(user=user, host=host, path=path,
                             device=device)

def main():
    if len(sys.argv) != 2:
        print("Usage: {} <path to config file>".format(sys.argv[0]))
        sys.exit(1)

    try:
        parser.read()
    except IOError as error:
        print("{}: {}".format(config_path, error.message))
        sys.exit(1)

    config_structure = parser.parse()
    (c_backups, ) = config_structure

    backup_repos = []
    # construct a list of backuprepositories out of c_backups
    for c_backup in c_backups:
        c_name = list(c_backup.keys())[0]
        (c_sources, c_destination, c_tags) = list(c_backup.values())[0]
        sources = []
        destination = None
        tags = []

        for c_source in c_sources:
            (c_user, c_host, c_path, c_device) = c_source
            source = make_full_location(c_user, c_host, c_path, c_device)
            sources.append(source)
        (c_user, c_host, c_path, c_device) = c_source

        (c_user, c_host, c_path, c_device) = c_destination
        destination = make_full_location(c_user, c_host, c_path, c_device)

        destination_directories = process.func_directory_get_files(
                                      host=destination.host,
                                      user=destination.user,
                                      path=destination.path)


        for c_tag in c_tags:
            (c_cron, c_max_age, c_max_count) = c_tag
            tag = backuprepository.Tag(cron=c_cron, max_age=c_max_age,
                                       max_count=c_max_count)
            tags.append(tag)


        backup_repo = backuprepositoriy.BackupRepository(
            source_locations=sources,
            repository_location=destination,
            repository_directories=destination_directories,
            tags=tags)

        backup_repos.append(backup_repo)

    def check_all_backups():
        for backup_repo in backup_repos:
            backup_repo.check_backups()

    # subscribe to all events
    for backup_repo in backup_repos:
        backup_repo.backup_required += _backup_required_handler
        backup_repo.backup_expired += _backup_expired_handler

    # start scheduling
    backup_scheduler = scheduler.Scheduler()
    check_all_backups()
    backup_scheduler.add_cron_job(check_all_backups, minute="*")































def _backup_required_handler(repository_location, source_locations,
                             latest_backup):
    print("Creating new backup from {} to {}, hardlinking to {}.".
          format(source_locations.path, repository_location.path,
                 latest_backup))



def _backup_expired_handler(backup_location):
    print("Removing backup {}".format())




def _get_bool(boolstr):
    if boolstr.lower() in ["true", "1", "yes", "wouldbenice"]:
        return True
    elif boolstr.lower() in ["false", "0", "no", "idareyou"]:
        return False
    raise ValueError("{} is not a boolean value.".format(boolstr))


def func_create_backup(source_locations, target_location, hardlink_to):
    if not target_location.is_localhost() and  any([not loc.host.is_localhost() for loc in source_locations]):
        raise Exception("Either source or location must be local.")
    args = ["rsync"]
    if hardlink_to == None:
        link_dest = ""
    else:
        link_dest = ("--link-dest", hardlink_to.path)
    args.extend(link_dest)
    destination_string = target_location.get_ssh_string()
    # We have to rsync every source location on their own, as all source args
    # for rsync must come from the same machine
    # TODO determine host and user for execution
    host = None
    user = None
    for source in source_locations:
        source_string = source.get_ssh_string()
        (exit_code, _, stderrdata) = \
            execute(host, [args, source_string, destination_string], user)
        if exit_code != 0:
            print("Backup from {0} to {1} failed:\n{2}".format(
                source_string, destination_string, stderrdata))

if __name__ == '__main__':
    main()
