import os
import process
import getpass

class Device(object):
    '''
    Represents a hardware storage device on a specific host,
    defined by its UUID.
    '''
    def __init__(self, host, uuid, filesystem):
        '''
        :param host: The host of the device.
        :param uuid: The UUID of the device.
        :param filesystem: The filesystem of the device. If you are not
        sure, try "auto" and mount will try to guess the filesystem.
        '''
        self.uuid = uuid
        self.filesystem = filesystem
        self.host = host
        
    def isAvailable(self, user=None):
        '''
        Determines whether the device is available.
        :param user: The user who is to own the process to check the availability.
        If the host is the localhost or None is given, the current user will be used
        regardless of the value of the parameter.
        :returns: True if the device is available, otherwise false.
        '''
        if user == None or self.host.isLocalhost():
            user = getpass.getuser()
            
        return process.func_fileExists(self.host, user, self.getDeviceFilePath,
                                       process.fileTypes.BLOCK_SPECIAL)  
        
    def getDeviceFilePath(self):
        return os.path.join("/dev/disk/by-uuid", self.uuid)
    
    
class Mountpoint(object):
    '''
    Represents a mountpoint on a specific host and provices methods to
    mount and unmount devices on this mountpoint, among others.
    '''
    def __init__(self, host, path, options, create, user=None):
        '''
        :param host: The host of the mountpoint.
        :param path: The absolute on the specified host.
        :param options: A tuple containing all mount options.
        :param create: A boolean that specifies whether the mountpoint
        is to be created automatically if it does not exist. You can always
        create the mountpoint manually with create()
        :param user: The user who is own all processes spawned by this class.
        If the host is the localhost or None is given, the current user will be used
        regardless of the value of the parameter, even for remote mountpoints.
        '''
        self.host = host
        self.path = path
        self.options = options
        self.create = create
        self.user = user
        if user == None or host.isLocalhost():
            self.user = getpass.getuser()
        
        
    def create(self, createParents):
        '''
        Creates the mountpoint if it does not exist already.
        :param createParents: Specifies whether parent directories of the mountpoint
        should be created if they do not exist. If False and the parent directories
        do not exist, an exception will be raised.
        '''
        (exitCode, _, stderrdata) = process.func_createDirectory(self.host, self.user, self.path, 
                                                                 createParents)
        if exitCode != 0:
            raise Exception("Creating the mountpoint failed: " + stderrdata)
    
    
    def remove(self):
        '''
        Removes the mountpoint if it exists, is empty and not active. If you
        try to remove a non-empty or active mountpoint, an exception will be
        raised.
        '''
        if self.isActive() or not self.isEmpty():
            raise MountpointBusyError(self)
        
        (exitCode, _, stderrdata) = process.func_createDirectory(self.host, self.user, self.path)
        if exitCode != 0:
            raise Exception("Removing the mountpoint failed: " + stderrdata)
    
    def mount(self, device):
        '''
        Mounts a device on the mountpoint. If the mountpoint is active or does
        not exist, an exception is raised. Mounting between hosts is not
        supported yet.
        :param device: The device to mount.
        '''
        if self.isEmpty():
            raise MountpointNotReadyError(self)
        if self.isActive():
            raise MountpointBusyError(self)
        if self.host != device.host:
            raise ValueError("Mounting between hosts is not supported.")
        
        args = ["mount", 
                "-o", ",".join(self.options).lstrip(','),
                "-t", device.filesystem,
                "-U", device.uuid,
                self.path]
        
        (exitCode, _, stderrdata) = process.execute(self.host, args, self.user)
        if exitCode != 0:
            raise Exception("Mounting failed: " + stderrdata)
        

    
    def bind(self, mountpoint, submounts=False):
        '''
        Binds this mountpoint to another mountpoint if the mountpoint is active.
        If the target mountpoint is active, non-empty or does not exist,
        or if this mountpoint is not active, an exception will be raised.
        ATTENTION: Binding between different hosts is not supported.
        :param mountpoint: The binding mountpoint.
        :param submounts: If True, all submounts of this mountpoint will also be
        attached to the binding mountpoint. If False, they will not be available.
        '''
        if self.host != mountpoint.host:
            raise ValueError("Binding mountpoints between hosts is not supported.")
        if not self.isActive():
            raise MountpointNotReadyError(self)
        if mountpoint.isActive() or not mountpoint.isEmpty():
            raise MountpointBusyError(mountpoint)
        if not mountpoint.exists():
            raise MountpointNotReadyError(mountpoint)
        
        args = ["mount", "--rbind" if submounts else "--bind", self.path, mountpoint.path]
        
        (exitCode, _, stderrdata) = process.execute(self.host, args, self.user)
        if exitCode != 0:
            raise Exception("Binding failed: " + stderrdata)
    
    
    def remount(self, newOptions=None):
        '''
        Remounts the device on this mountpoint with different options
        if any are given. If the mountpoint is not active, an exception is raised.
        :param newOptions: The options for the remount, if none are given the
        old options will be used.
        '''
        if not self.isActive():
            raise MountpointNotReadyError(self)

        if newOptions == None:
            newOptions = self.options
        args = ["mount", "-o", (",".join(newOptions)+ ",remount").lstrip(','), self.path]
        (exitCode, _, stderrdata) = process.execute(self.host, args, self.user)
        if exitCode != 0:
            raise Exception("Remounting failed: " + stderrdata)

    
    
    def unmount(self):
        '''
        Unmounts the device if the mountpoint is active, otherwise, raises an exception.
        If unmounting is not possible because the device is busy, an exception is raised.
        '''
        if not self.active():
            raise MountpointNotReadyError(self)
        args = ["umount", self.path]
        (exitCode, _, stderrdata) = process.execute(self.host, args, self.user)
        # An exitcode of 1 means that the device is busy.
        if exitCode == 1:
            raise MountpointBusyError(self)
        elif exitCode > 1:
            raise Exception("Unmounting failed: " + stderrdata)
        
    

    def exists(self):
        '''
        Determines whether the mountpoint exists.
        :returns: True if the mountpoint exists, False otherwise.
        '''
        return process.func_fileExists(self.host, self.user, self.path, process.fileTypes.DIRECTORY)    
    
    
    def isEmpty(self):
        '''
        Determines whether the mountpoint is empty. Empty does not mean
        inactive, an active mountpoint may be empty, too.
        :returns: True if the mountpoint is empty, False otherwise.
        '''
        return process.func_directoryEmpty(self.host, self.user, self.path)
    
    
    # Some caching could be implemented.
    def isActive(self):
        '''
        Determines whether the mountpoint is active.
        :returns: True if the mountpoint is active, False otherwise.
        '''
        args = ["mount"]
        (_, stdouterror, _) = process.execute(self.host, args, self.user)
        for line in stdouterror.split('\n'):
            # The output of mount has the following layout:
            # <device> on <mountpoint> type <fstype> (<options>)
            # We want to extract the mountpoint
            if line.split(' ')[2] == self.path:
                return True
        return False
    
    
    
class MountpointBusyError(Exception):
    '''
    Exception that is raised when you try to remove a non-empty or active
    mountpoint, try to mount a device to a non-empty or active mountpoint,
    or try to bind to an active or non-empty mountpoint.
    '''
    def __init__(self, mountpoint):
        self.mountpoint = mountpoint
        
        
        
class MountpointNotReadyError(Exception):
    '''
    Exception that is raised if you try to bind, remount or unmount an non-active
    mountpoint
    '''
    def __init__(self, mountpoint):
        self.mountpoint = mountpoint
    