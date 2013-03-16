"""
Module to handle devices and mountpoints, even on remote machines.
"""
import os

import process

class Device(object):
    """
    Represents a hardware storage device on a specific host, defined by its 
    UUID.
    """
    def __init__(self, host, uuid, filesystem, user):
        """
        :param host: The host of the device.
        :type host: Host instance
        :param uuid: The UUID of the device.
        :type uuid: string
        :param filesystem: The filesystem of the device. If you are not sure, 
        try "auto" and mount will try to guess the filesystem.
        :type filesystem: string
        """
        self.uuid = uuid
        self.filesystem = filesystem
        self.host = host
        self.user = user
        
        
    def is_available(self):
        """
        Determines whether the device is available.
        :param user: The user who is to own the process to check the 
        availability. If the host is the localhost or None is given, the current
        user will be  used regardless of the value of this parameter.
        :type user: string
        :returns: True if the device is available, otherwise false.
        :rtype: bool
        """
        return process.func_file_exists(self.host, self.user, 
                                        self.get_device_file_path,
                                        process.FileTypes.BLOCK_SPECIAL)  
        
        
    def get_device_file_path(self):
        """
        Returns a path pointing to the file representing the device
        :returns: The path to the device file.
        :rypte: string
        """
        return os.path.join("/dev/disk/by-uuid", self.uuid)
    
    
class Mountpoint(object):
    """
    Represents a mountpoint on a specific host and provices methods to mount 
    and unmount devices on this mountpoint, among others.
    """
    def __init__(self, host, path, options, create_if_not_existent, user):
        """
        :param host: The host of the mountpoint.
        :type host: Host instance
        :param path: The absolute on the specified host.
        :type path: string
        :param options: A tuple containing all mount options.
        :type options: tuple
        :param create: A boolean that specifies whether the mountpoint is to be
        created automatically if it does not exist. You can always create the 
        mountpoint manually with create().
        :type create: bool
        :param user: The user who is own all processes spawned by this class. If
        the host is the localhost or None is given, the current user will be 
        used regardless of the value of the parameter, even for remote 
        mountpoints.
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
        :raises: Exception if creating the mountpoint failed.
        """
        if not self.exists():
            (exit_code, _, stderrdata) = process.func_create_directory(
                self.host,
                self.user,
                self.path, 
                create_parents)
            
            if exit_code != 0:
                raise Exception("Creating the mountpoint failed: " + stderrdata)
    
    
    def remove(self):
        """
        Removes the mountpoint if it exists, is empty and not active. If you try
        to remove a non-empty or active mountpoint, an exception will be raised.
        :raises: Exception if removing the mountpoint failed.
        """
        if self.is_active() or not self.is_empty():
            raise MountpointBusyError(self)
        
        (exit_code, _, stderrdata) = process.func_remove_directory(self.host,
                                                                  self.user,
                                                                  self.path)
        if exit_code != 0:
            raise Exception("Removing the mountpoint failed: " + stderrdata)
    
    
    def mount(self, device):
        """
        Mounts a device on the mountpoint. If the mountpoint is active or does
        not exist, an exception is raised. Mounting between hosts is supported.
        :param device: The device to mount.
        :type device: Device instance
        :raises: MountpointNotReadyError if the mountpoint is not empty.
        :raises: MountpointBusyError if the mountpoint is active.
        :raises: Exception if the mounting failed.
        """
        if not self.is_empty():
            raise MountpointNotReadyError(self)
        if self.is_active():
            raise MountpointBusyError(self)

        # The mount procedure depends on the relation between the host of the 
        # device and the host of the mountpoint:
        #
        # o---o-----------o--------------o-------------------------------------o
        # |   | self.host |  device.host | action                              |
        # o---o-----------o--------------o-------------------------------------o
        # | 1 | local     | local        | mount locally on same machine       |
        # | 2 | local     | remote       | mount remote device on remote       |
        # |   |           |              | machine, mount remote directory on  |
        # |   |           |              | same machine with sshfs             |
        # | 3 | remote    | local        | mount local device on local machine |
        # |   |           |              | and mount local directory on remote |
        # |   |           |              | machine with sshfs                  |
        # | 4 | remote    | remote       | mount locally on remote machine     |
        # o---o-----------o--------------o-------------------------------------o
        #
        # sshfs cannot be used to directly mount a device from/to a remote host,
        # but to mount a directory, smiliar to mount's bind option. So we first
        # have to mount the device on the same host, and then use sshfs to mount
        # that directory on the target host.
        
        # The paths to the temporary mountpoints:
        TEMP_MOUNTPOINT_LOCAL  = "/tmp/mount/temp/"
        TEMP_MOUNTPOINT_REMOTE = TEMP_MOUNTPOINT_LOCAL
        
        if self.host == device.host:
            # case 1 and 4
            args = ["mount", 
                    "-o", ",".join(self.options).lstrip(','),
                    "-t", device.filesystem,
                    "-U", device.uuid,
                    self.path]
        elif self.host.isLocal() and not device.host.isLocal():
            # case 2
            remote_tmp_mountpoint = Mountpoint(device.host, 
                                               TEMP_MOUNTPOINT_REMOTE,
                                               self.options, 
                                               False, 
                                               self.user)
            remote_tmp_mountpoint.create(create_parents=True)
            remote_tmp_mountpoint.mount(device)
            args = ["sshfs",
                    "{0}@{1}:{2}".format(self.user, 
                                         remote_tmp_mountpoint.host.ip,
                                         remote_tmp_mountpoint.path),
                    self.path,
                    "-o", "idmap=user"]
        elif not self.host.isLocal() and device.host.isLocal(): 
            # case 3
            local_tmp_mountpoint = Mountpoint(device.host, 
                                              TEMP_MOUNTPOINT_REMOTE,
                                              self.options, 
                                              False, 
                                              self.user)
            local_tmp_mountpoint.create(create_parents=True)
            local_tmp_mountpoint.mount(device)
            args = ["sshfs",
                    self.path,
                    "{0}@{1}:{2}".format(self.user, 
                                         device.host.get_real_ip(), 
                                         local_tmp_mountpoint.path),
                    "-o", "idmap=user"]
             
        (exit_code, _, stderrdata) = process.execute(self.host, args, self.user)
        if exit_code != 0:
            raise Exception("Mounting failed: " + stderrdata)

    
    def bind(self, target_mountpoint, submounts=False):
        """
        Binds this mountpoint to another mountpoint if the mountpoint is active.
        If the target mountpoint is active, non-empty or does not exist, or if 
        this mountpoint is not active, an exception will be raised.
        ATTENTION: Binding between different hosts is not supported.
        :param mountpoint: The binding mountpoint.
        :type mountpoint: Mountpoint instance
        :param submounts: If True, all submounts of this mountpoint will also be
        attached to the binding mountpoint. If False, they will not be 
        available.
        :type submounts: bool
        :raises: ValueError if trying to bind between hosts.
        :raises: MountpointNotReadyError if this mountpoint is active or the
        target mountpoint does not already exist.
        :raises: MountpointBusyError if the target mountpoint is active or not
        empty.
        :raises: Exception if binding failed.
        """
        if self.host != target_mountpoint.host:
            raise ValueError(
                "Binding mountpoints between hosts is not supported.")
        if not self.is_active():
            raise MountpointNotReadyError(self)
        if target_mountpoint.is_active() or not target_mountpoint.is_empty():
            raise MountpointBusyError(target_mountpoint)
        if not target_mountpoint.exists():
            raise MountpointNotReadyError(target_mountpoint)
        
        args = ["mount", "--rbind" if submounts else "--bind", 
                self.path, target_mountpoint.path]
        
        (exit_code, _, stderrdata) = process.execute(self.host, args, self.user)
        if exit_code != 0:
            raise Exception("Binding failed: " + stderrdata)
    
    
    def remount(self, new_options=None):
        """
        Remounts the device on this mountpoint with different options if any are
        given. If the mountpoint is not active, an exception is raised.
        :param newOptions: The options for the remount, if none are given the
        old options will be used.
        :type newOptions: tuple
        :raises: Exception if remounting failed.
        """
        if not self.is_active():
            raise MountpointNotReadyError(self)

        if new_options == None:
            new_options = self.options
        args = ["mount", "-o", (",".join(new_options)+ ",remount").lstrip(','),
                self.path]
        (exit_code, _, stderrdata) = process.execute(self.host, args, self.user)
        if exit_code != 0:
            raise Exception("Remounting failed: " + stderrdata)

    
    def unmount(self):
        """
        Unmounts the device if the mountpoint is active, otherwise, raises an 
        exception. If unmounting is not possible because the device is busy, an 
        exception is raised.
        :raises: Exception if unmounting failed.
        :raises: MountpointNotReadyError if the mountpoint is active.
        """
        if not self.is_active():
            raise MountpointNotReadyError(self)
        args = ["umount", self.path]
        (exit_code, _, stderrdata) = process.execute(self.host, args, self.user)
        # An exitcode of 1 means that the device is busy.
        if exit_code == 1:
            raise MountpointBusyError(self)
        elif exit_code > 1:
            raise Exception("Unmounting failed: " + stderrdata)
        

    def exists(self):
        """
        Determines whether the mountpoint exists.
        :returns: True if the mountpoint exists, False otherwise.
        :rtype: bool
        """
        return process.func_file_exists(self.host, self.user, self.path, 
                                        process.FileTypes.DIRECTORY)    
    
    
    def is_empty(self):
        """
        Determines whether the mountpoint is empty. Empty does not mean
        inactive, an active mountpoint may be empty, too.
        :returns: True if the mountpoint is empty, False otherwise.
        :rtype: bool
        """
        return process.func_directory_empty(self.host, self.user, self.path)
    
    
    # Some caching could be implemented.
    def is_active(self):
        """
        Determines whether the mountpoint is active.
        :returns: True if the mountpoint is active, False otherwise.
        :rtype: bool
        """
        args = ["mount"]
        (_, stdouterr, _) = process.execute(self.host, args, self.user)
        for line in str(stdouterr).split('\n'):
            # The output of mount has the following layout:
            # <device> on <mountpoint> type <fstype> (<options>)
            # We want to extract the mountpoint.
            if line.split(' ')[2] == self.path:
                return True
        return False
            

class FullLocation(object):
    def __init__(self, user, host, path, device, mountpoint):
        self.user = user
        self.host = host
        self.path = path
        self.device = device
        self.mountpoint = mountpoint
        
        
    def mount(self):
        if self.device is not None:
            self.mountpoint.mount()
        
            
    def unmount(self):
        if self.device is not None:
            self.mountpoint.unmount()
            
    def get_ssh_string(self):
        if self.host.is_localhost():
            return self.path
        else:
            return "{0}@{1}:{2}".format(self.user, self.host, self.path)
        
            
    def _get_path(self):
        if self.device is None:
            return self.path
        else:
            return os.path.join(self.mountpoint.path, self.path)
    path = property(_get_path)

        
        
    
class MountpointBusyError(Exception):
    """
    Exception that is raised when you try to remove a non-empty or active
    mountpoint, try to mount a device to a non-empty or active mountpoint,
    or try to bind to an active or non-empty mountpoint.
    """
    def __init__(self, mountpoint):
        super(MountpointBusyError, self).__init__()
        self.mountpoint = mountpoint
        
        
class MountpointNotReadyError(Exception):
    """
    Exception that is raised if you try to bind, remount or unmount an 
    non-active mountpoint
    """
    def __init__(self, mountpoint):
        super(MountpointNotReadyError, self).__init__()
        self.mountpoint = mountpoint
    
