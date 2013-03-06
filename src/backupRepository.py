import event
import apscheduler.scheduler as scheduler # @UnresolvedImport
import datetime

SUFFIX     = 'bak'
# Timeformat used by the datetime.strptime() method of 
TIMEFORMAT = '%Y-%m-%dT%H:%M:%S'

FORMAT     = "{0}.{1}".format(TIMEFORMAT, SUFFIX)

class BackupRepository(object):
    def __init__(self, directories, interval, maxCount, maxAge):
        self.__directories = directories
        self.__backups = None
        self.__interval = interval
        self.__maxCount = maxCount
        self.__maxAge = maxAge
        
        self.backupExpired = event.Event()
        self.backupRequired = event.Event()
        
        self.__scheduler = scheduler.Scheduler()
        self.__scheduler.add_cron_job(self.__minuteElapsed, minute='*')
        self.__scheduler.start()
        
        maxCountAge = maxCount * interval
        self.__maxAge = maxCountAge if maxCountAge > maxAge else maxAge
        

    
    def __minuteElapsed(self):
        self.__checkBackups()
    
    
    def __checkBackups(self):
        maxBirth = datetime.datetime.now() - self.__maxAge
        minBirth = datetime.datetime.now() - self.__interval
        
        backupNeeded = True
        
        for backup in self.__backups:
            if backup.birth < maxBirth:
                self.backupExpired(self, backup)
            if backup.birth >= minBirth:
                backupNeeded = False
                
        if backupNeeded:
            self.backupRequired(self)
            
    
   
    def __initializeBackups(self):
        self.__backups = None
    
    
class Backup(object):
    
    def __init__(self, directoryName):
        self.__directoryName = directoryName
        self.birth = self.__getDate(self.__directoryName)

    def __getDate(self, name):
        self.birth = datetime.datetime.strptime(name.split('.')[0])
        