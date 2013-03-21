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

"""Module to handle devices and mountpoints, even on remote machines."""

import os

import process


class Device(object):
    """
    Represents a hardware storage device on a specific host, identified by its
    UUID.
    """
    def __init__(self, host, uuid, filesystem, user):
        """
        :param host: The host of the device.
        :type host: Host instance
        :param uuid: The UUID of the device.
        :type uuid: string
        :param filesystem: The filesystem of the device. If you are not sure,
        try "auto" and mount() will try to guess the filesystem.
        :type filesystem: string
        :param user: The user who shall own all relevant processes spawned by
        to operate on the device.
        :type user: string
        """
        self.uuid = uuid
        self.filesystem = filesystem
        self.host = host
        self.user = user

        self._mountpoint = None
        self._temp_mountpoint = None

    def is_mounted(self):
        """
        Determines whether the device is already mounted.
        :returns: True if the device is already mounted, False otherwise.
        :rtype: bool
        :raises: ProcessError if a process spwaned by this method fails.
        """
        args = ["mount"]
        try:
            stdoutdata = process.execute_success(self.host, args, self.user)
            name = os.path.basename(self.get_device_file_path())
        except process.ProcessError:
            raise
        for line in str(stdoutdata).splitlines():
            if not line:
                # The last line of the output is empty.
                continue
            # The output of mount has the following layout:
            # <device> on <mountpoint> type <fstype> (<options>)
            # We want to extract the device.
            if line.split(' ')[0] == name:
                return True
        return False

    def is_available(self):
        """
        Determines whether the device is available. "Available" means that it
        is recognized by the operating system and a device file exists.
        :returns: True if the device is available, otherwise false.
        :rtype: bool
        :raises: ProcessError if a process spawned by this method fails.
        """
        try:
            exists = process.func_file_exists(
                self.host,
                self.user,
                self.get_device_file_path(),
                process.FileTypes.BLOCK_SPECIAL)
        except process.ProcessError:
            raise
        return exists

    def get_device_file_paths(self):
        """
        Returns a list of paths that point to the device file.
        :returns: A list of paths to the device file.
        :rtype: list of strings
        :raises: ProcessError if a process spwaned by this method fails.
        """
        paths = []
        paths.append(self.get_device_file_path())
        args = ["readlink", "--no-newline", paths[0]]
        try:
            stdoutdata = process.execute_success(self.host,
                                                 args,
                                                 self.user)
        except process.ProcessError:
            raise
        file_name = os.path.basename(stdoutdata)
        file_path = os.path.join("/dev/", file_name)
        paths.append(file_path)
        return paths

    def get_device_file_path(self):
        """
        Returns a path that points the the device file. It will be a symbolic
        link.
        :returns: A path to the device file.
        :rtype: string
        """
        return os.path.join("/dev/disk/by-uuid", self.uuid)

    def mount(self, mountpoint):
        """
        Mounts the device on a mountpoint. If the mountpoint is active or does
        not exist, an exception is raised. Mounting between a remote host and
        the localhost is supported, mounting between two remote hosts is not.
        When mounting between two different hosts, a temporary mountpoint will
        be created on the machine where the device resides. It will
        automatically be removed when unmounting the device again with
        unmount().
        :param mountpoint: The mountpoint where the device shall be mounted
        at.
        :type mountpoint: Mountpoint instance
        :raises: ProcessError if the any process spawned by this method fails.
        :raises: ValueError when trying to mount between two remote hosts.
        :raises: MountError under the following circumstances:
        - The device is not available or already mounted.
        - The mountpoint is active, not empty or does not exists although it
          shall not be created (i.e. "create_if_non_existent" is False).
        - Any temporary mountpoint that are needed when mounting between two
          different machines is already active of not empty.
        """
        if not self.is_available():
            raise MountError("Device is not available, cannot be mounted.")
        if self.is_mounted():
            raise MountError("The device is already mounted.")
        if mountpoint.is_active():
            raise MountError(
                "Cannot mount, as the target mountpoint is active.")
        if not mountpoint.is_empty():
            raise MountError(
                "Cannot mount, as the target mountpoint is not empty.")

        if not mountpoint.exists():
            if mountpoint.create_if_not_existent:
                mountpoint.create(create_parents=True)
            else:
                raise MountError(
                    "Mountpoint does not exist, but shall not be created.")

        # The mount procedure depends on the relation between the host of the
        # device and the host of the mountpoint:
        #
        # o---o------------o--------o-------------------------------------o
        # |   | mountpoint | device | action                              |
        # o---o------------o--------o-------------------------------------o
        # | 1 | local      | local  | mount locally on same machine       |
        # | 2 | local      | remote | mount remote device on remote       |
        # |   |            |        | machine, mount remote directory on  |
        # |   |            |        | same machine with sshfs             |
        # | 3 | remote     | local  | mount local device on local machine |
        # |   |            |        | and mount local directory on remote |
        # |   |            |        | machine with sshfs                  |
        # | 4 | remote     | remote | 1) it is the same host:             |
        # | 4 |            |        |    mount locally on remote machine  |
        # | 4 |            |        | 2) they are different hosts:        |
        # | 4 |            |        |    raise an exception, as this is   |
        # | 4 |            |        |    not supported                    |
        # o---o------------o--------o-------------------------------------o
        #
        # sshfs cannot be used to directly mount a device from/to a remote
        # host, but to mount a directory, smiliar to mount's bind option. So
        # we first have to mount the device on the same host, and then use
        # sshfs to mount that directory on the target host.

        # The paths to the temporary mountpoints created in cases 2 and 3
        # Whenever we have to use them, we will mount the device there, so
        # we can use the self.user's home directory for example.
        local_temp_mountpoint_path = "/home/{}/mnt/tmp/".format(self.user)
        remote_temp_mountpoint_path = local_temp_mountpoint_path

        if (self.host == mountpoint.host):
            # case 1 and 4/1
            # We do not have to care about whether they are both local or
            # both remote, as the process module abstracts the operations
            args = ["mount",
                    "-o", ",".join(mountpoint.options).lstrip(','),
                    "-t", self.filesystem,
                    "-U", self.uuid,
                    mountpoint.path]
        elif not self.host.is_localhost() and mountpoint.host.is_localhost():
            # case 2
            remote_temp_mountpoint = Mountpoint(
                host=self.host,
                path=remote_temp_mountpoint_path,
                options=",".join(mountpoint.options).lstrip(','),
                create_if_not_existent=True,
                user=self.user)
            self._temp_mountpoint = remote_temp_mountpoint
            if remote_temp_mountpoint.is_active():
                raise MountError("The temporary mountpoint is active.")
            if not remote_temp_mountpoint.is_empty():
                raise MountError("The temporary mountpoint is not empty.")

            self.mount(mountpoint)
            args = ["sshfs",
                    "{0}@{1}:{2}".format(
                        remote_temp_mountpoint.user,
                        remote_temp_mountpoint.host.get_real_ip(),
                        remote_temp_mountpoint.path),
                    mountpoint.path,
                    "-o", "idmap=user"]
            try:
                process.execute_success(
                    mountpoint.host,
                    args,
                    mountpoint.user)
            except process.ProcessError:
                raise
        elif self.host.is_localhost() and not mountpoint.host.is_localhost():
            # case 3
            local_temp_mountpoint = Mountpoint(
                host=self.host,
                path=local_temp_mountpoint_path,
                options=",".join(mountpoint.options).lstrip(','),
                create_if_not_existent=True,
                user=mountpoint.user)
            self._temp_mountpoint = local_temp_mountpoint
            if local_temp_mountpoint.is_active():
                raise MountError("The temporary mountpoint is active.")
            if not local_temp_mountpoint.is_empty():
                raise MountError("The temporary mountpoint is not empty.")

            self.mount(mountpoint=local_temp_mountpoint)
            args = ["sshfs",
                    mountpoint.path,
                    "{0}@{1}:{2}".format(
                        local_temp_mountpoint.user,
                        local_temp_mountpoint.host.get_real_ip(),
                        local_temp_mountpoint.path),
                    "-o", "idmap=user"]
            try:
                process.execute_success(
                    mountpoint.host,
                    args,
                    mountpoint.user)
            except process.ProcessError:
                raise
        else:
            # case 4/2
            raise ValueError("Mounting between two remote hosts is not "
                             "supported.")

        # Remember the mountpoint for later unmounting.
        self._mountpoint = mountpoint

    def unmount(self):
        """
        Unmounts the device from its mountpoint if it is mounted.
        :raises: Exception if the unmounting failed because the device is
        busy.
        :raises: ProcessError if the any process spawned by this method fails.
        :raises: MountError if the device is not mounted or busy.
        """
        # If we mounted "conventionally", we just unmount with "umount".
        # But if we used sshfs, we will have to unmount the sshfs mountpoint
        # using "fusermount -u" and then we can unmount the temporary
        # mountpoint in the usual way.
        if not self.is_mounted():
            raise MountError("The device is not mounted, cannot be unmounted.")

        unmount_mountpoint = None

        if self._temp_mountpoint:
            args = ["fusermount", "-u", self._mountpoint.path]
            try:
                process.execute_success(host=self._mountpoint.host,
                                        args=args,
                                        user=self._mountpoint.user)
            except process.ProcessError:
                raise

            unmount_mountpoint = self._temp_mountpoint
        else:
            unmount_mountpoint = self._mountpoint

        args = ["umount", unmount_mountpoint.path]
        try:
            process.execute_success(
                host=unmount_mountpoint.host,
                args=args,
                user=unmount_mountpoint.user)
        except process.ProcessError as error:
            # An exitcode of 1 means that the device is busy.
            if error.exit_code == 1:
                raise MountError(
                    "Unmounting failed because mountpoint is busy.")
            else:
                raise

        # Remove the mountpoint if it was a temporary one.
        if unmount_mountpoint is self._temp_mountpoint:
            self._temp_mountpoint.remove()


class Mountpoint(object):
    """
    Represents a mountpoint on a specific host and provices methods to mount
    and unmount devices on this mountpoint, among others.
    """
    def __init__(self, host, path, options, create_if_not_existent, user):
        """
        :param host: The host of the mountpoint.
        :type host: Host instance
        :param path: The absolute path on the specified host.
        :type path: string
        :param options: A tuple containing all mount options.
        :type options: tuple
        :param create_if_not_existent: A boolean that specifies whether the
        mountpoint is to be created automatically if it does not exist and you
        try to mount a device on it. You can always create the mountpoint
        manually with create(). Note: When the mountpoint it implicitly
        created, all parent directories will be created too if they do not
        exist, identical to the behaviour of create(create_parents=True).
        :type create_if_not_existent: bool
        :param user: The user who is own all processes spawned by this class.
        :type user: string
        """
        self.host = host
        self.path = path
        self.options = options
        self.create_if_not_existent = create_if_not_existent
        self.user = user

    def create(self, create_parents):
        """
        Creates the mountpoint if it does not exist already.
        :param create_parents: Specifies whether parent directories of the
        mountpoint should be created if they do not exist. If False and the
        parent directories do not exist, an exception will be raised.
        :type create_parents: bool
        :raises: ProcessError if the any process spawned by this method fails.
        """
        if not self.exists():
            try:
                process.func_create_directory(
                    host=self.host,
                    user=self.user,
                    path=self.path,
                    create_parents=create_parents)
            except process.ProcessError:
                raise

    def remove(self):
        """
        Removes the mountpoint if it exists, is empty and not active. If you
        try to remove a non-empty or active mountpoint, an exception will be
        raised.
        :raises: MountError if the mountpoint is still active or not empty.
        :raises: ProcessError if the any process spawned by this method fails.
        """
        if self.is_active():
            raise MountError(
                "Mountpoint cannot be removed, as it it still active.")
        if not self.is_empty():
            raise MountError("Cannot remove non-empty mountpoint.")

        try:
            process.func_remove_directory(
                self.host,
                self.user,
                self.path,
                recursive=False)
        except process.ProcessError:
            raise

    def remount(self, new_options=None):
        """
        Remounts the device on this mountpoint with different options if any
        are given. If the mountpoint is not active, an exception is raised.
        :param newOptions: The options for the remount, if none are given the
        old options will be used.
        :type newOptions: tuple
        :raises: MountError if the mountpoint does not exists or is not
        active.
        :raises: ProcessError if the any process spawned by this method fails.
        """
        if not self.exists():
            raise MountError(
                "Trying to remout a non-existent mountpoint.")
        if not self.is_active():
            raise MountError(
                "The mountpoint is not active, cannot be remounted.")
        if new_options is None:
            new_options = self.options
        args = ["mount", "-o",
                (','.join(new_options) + ",remount").lstrip(','),
                self.path]
        try:
            process.execute_success(self.host,
                                    args,
                                    self.user)
        except process.ProcessError as error:
            if error.exit_code != 0:
                raise MountError("Remounting failed: " + error.stderrdata)
            else:
                raise

    def bind(self, target_mountpoint, submounts=False):
        """
        Binds this mountpoint to another mountpoint if the mountpoint is
        active. If the target mountpoint is active, non-empty or does not
        exist, or if this mountpoint is not active, an exception will be
        raised.
        ATTENTION: Binding between different hosts is not supported.
        :param target_mountpoint: The binding mountpoint.
        :type target_mountpoint: Mountpoint instance
        :param submounts: If True, all submounts of this mountpoint will also be
        attached to the binding mountpoint. If False, they will not be
        available.
        :type submounts: bool
        :raises: ValueError if trying to bind between different hosts.
        :raises: ProcessError if the any process spawned by this method fails.
        :raises MountError if the mountpoint is not active, if the target
        mountpoint is active or not empty, or if the target mountpoint does not
        exists and shall not be created (i.e. "create_if_not_existent" is
        False).
        """
        if self.host != target_mountpoint.host:
            raise ValueError(
                "Binding mountpoints between hosts is not supported.")
        if not self.is_active():
            raise MountError(
                "The mountpoint cannot be bound to another one as it is not "
                "active.")
        if not target_mountpoint.exists():
            if target_mountpoint.create_if_not_existent:
                target_mountpoint.create(create_parents=True)
            else:
                raise MountError(
                    "Binding not possible, as the target mountpoint does not "
                    "exist and shall not be created.")
        if not target_mountpoint.is_empty():
            raise MountError(
                "Binding not possible, as the target mountpoint is not empty.")
        if target_mountpoint.is_active():
            raise MountError(
                "Binding not possible, as the target mountpoint is active.")

        args = ["mount", "--rbind" if submounts else "--bind",
                self.path, target_mountpoint.path]

        try:
            process.execute_success(self.host, args, self.user)
        except process.ProcessError:
            raise

    def exists(self):
        """
        Determines whether the mountpoint exists.
        :returns: True if the mountpoint exists, False otherwise.
        :rtype: bool
        :raises: ProcessError if the any process spawned by this method fails.
        """
        try:
            exists = process.func_file_exists(self.host,
                                              self.user,
                                              self.path,
                                              process.FileTypes.DIRECTORY)
        except process.ProcessError:
            raise
        return exists

    def is_empty(self):
        """
        Determines whether the mountpoint is empty. Empty does not mean
        inactive, an active mountpoint may be empty, too.
        :returns: True if the mountpoint is empty, False otherwise.
        :rtype: bool
        :raises: ProcessError if the any process spawned by this method fails.
        """
        try:
            empty = process.func_directory_empty(self.host,
                                                 self.user,
                                                 self.path)
        except process.ProcessError:
            raise
        return empty

    def is_active(self):
        """
        Determines whether the mountpoint is active.
        :returns: True if the mountpoint is active, False otherwise.
        :rtype: bool
        :raises: ProcessError if the any process spawned by this method fails.
        """
        # Some caching could be implemented.
        args = ["mount"]
        try:
            (stdouterr, _) = process.execute_success(self.host,
                                                     args,
                                                     self.user)
        except process.ProcessError:
            raise
        for line in str(stdouterr).splitlines():
            if not line:
                # The last line of the output is empty.
                continue
            # The output of mount has the following layout:
            # <device> on <mountpoint> type <fstype> (<options>)
            # We want to extract the mountpoint.
            # attention: the path of the mountpoint might contain a trailing
            # slash, but the output of "mount" never does, so we have to
            # remove the potential slash
            if line.split()[2] == self.path.rstrip('/'):
                return True
        return False


class MountError(Exception):
    """An exception that is raised when a mounting operation fails."""
    def __init__(self, message):
        Exception.__init__()
        self.message = message
