#import getpass


#import filesystem
#import host

#raiseit = False

#def try_method(call, *args, **kwargs):
    #rval = None
    #try:
        #rval = call(*args, **kwargs)
        #print("\tWent fine.")
    #except Exception as error:
        #print("\tException raised: ", error.message)
        #if raiseit: raise
    #return rval

#uuid = "c3a1cc6b-56f4-4822-a768-bd7d11ad0663"
#fs = "ext4"
#localhost = host.get_localhost()
#user = "root"

#device = filesystem.Device(uuid=uuid, filesystem=fs, host=localhost, user=user)
#device_nonexistent = filesystem.Device(uuid="lelly", filesystem="a",
                                       #host=localhost, user=user)

##print "device available:"
##print try_method(device.is_available)
##print try_method(device._get_device_file_path)
##print try_method(device._name_in_dev)
##print "device nonexistent available:"
##print try_method(device_nonexistent.is_available)
##print try_method(device_nonexistent._get_device_file_path)
##print try_method(device._name_in_dev)

##print "mount"
##try_method(device.mount)
##try_method(device_nonexistent.mount)

##print "unmount"
##try_method(device.unmount)
##try_method(device_nonexistent.unmount)

##print "remount"
##try_method(device.remount, ("lel"))
##try_method(device_nonexistent.remount, ("lel"))


#mountpoint = filesystem.Mountpoint(host=localhost,
                                   #path="/home/hannes/test/mount/testmount/",
                                   #options=("noatime","ro"),
                                   #create_if_not_existent=False,
                                   #user=user)

#bindpoint = filesystem.Mountpoint(host=localhost,
                                  #path="/home/hannes/test/mount/bindmount/",
                                  #options=("atime","rw"),
                                  #create_if_not_existent=True,
                                  #user=user)

##print "creating"
##try_method(mountpoint.create, create_parents=False)
##print "exists"
##print try_method(mountpoint.exists)
##print "active"
##print try_method(mountpoint.is_active)



#device.mount(mountpoint=mountpoint)

#device.remount(new_options=("rw","noatime"))

#mountpoint.bind(bindpoint)

#device.unmount()
