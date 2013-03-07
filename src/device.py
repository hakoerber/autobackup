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
        self.__uuid = uuid
        self.__filesystem = filesystem
        self.__host = host
        
    def isAvailable(self):
        '''
        Determines whether the device is available.
        :returns: True if the device is available, otherwise false.
        '''
        return False
    
    
class Mountpoint(object):
    '''
    Represents a mountpoint on a specific host and provices methods to
    mount and unmount devices on this mountpoint, among others.
    '''
    def __init__(self, host, path, options, create):
        '''
        :param host: The host of the mountpoint.
        :param path: The absolute on the specified host.
        :param options: A list containing all mount points.
        :param create: A boolean that specifies whether the mountpoint
        is to be created automatically if it does not exist. You can always
        create the mountpoint manually with create()
        '''
        self.__host = host
        self.__path = path
        self.__options = options
        self.__create = create
        
    def create(self):
        '''
        Creates the mountpoint if it does not exist already.
        '''
        pass
    
    def remove(self):
        '''
        Removes the mountpoint if it exists, is empty and not active.
        '''

    
    def mount(self, device):
        '''
        Mounts a device on the mountpoint. If the mountpoint is active,
        mounting is refused, use unmount() beforehand.
        :param device: The device to mount.
        '''
    
    def bind(self, mountpoint, submounts=False):
        '''
        Binds this mountpoint to another mountpoint if the mountpoint is active,
        otherwise, does nothing.
        ATTENTION: Binding between different hosts is not supported.
        :param mountpoint: The binding mountpoint.
        :param submounts: If True, all submounts of this mountpoint will also be
        attached to the binding mountpoint. If False, they will not be available.
        '''
    
    def remount(self, newOptions=None):
        '''
        Remounts the device on this mountpoint with different options
        if any are given. If no device is mounted on the mountpoint, nothing
        happens.
        :param newOptions: The options for the remount, if none are given the
        old options will be used.
        '''
    
    def unmount(self):
        '''
        Unmounts the device if the mountpoint is active, otherwise, does nothing.
        '''
    

    def exists(self):
        '''
        Determines whether the mountpoint exists.
        :returns: True if the mountpoint exists, False otherwise.
        '''
        return False    
    
    def isEmpty(self):
        '''
        Determines whether the mountpoint is empty.
        :returns: True if the mountpoint is empty, False otherwise.
        '''
        return False
    
    def isActive(self):
        '''
        Determines whether the mountpoint is active.
        :returns: True if the mountpoint is active, False otherwise.
        '''
        return False
    