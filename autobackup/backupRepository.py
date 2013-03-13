import event
import datetime

import apscheduler.scheduler as scheduler # @UnresolvedImport

SUFFIX     = 'bak'
# Timeformat used by the datetime.strptime() method of 
TIMEFORMAT = '%Y-%m-%dT%H:%M:%S'
FORMAT     = "{0}.{1}".format(TIMEFORMAT, SUFFIX)

class BackupManager(object):
    """
    Represents a collection of backup repositories. Provides methods to poll
    whether new backups are needed or old backups are expired. Can also poll
    automatically in certain intervals.
    """
    
    def __init__(self, backupRepositories):
        """
        :param backupRepositories: A list of backupRepositories to 
        manage.
        :type backupRepositories: list of BackupRepository instances
        """
        self.backupRepositories = backupRepositories
        
        # We will just handle all events raised by the backupRepositories and
        # re-raise them with the same information.
        self.backup_required = event.Event()
        self.backup_expired = event.Event()
        for backupRepository in backupRepositories:
            backupRepository.backup_required += self._backup_required_handler
            backupRepository.backup_expired  += self._backup_expired_handler

        self._scheduler = scheduler.Scheduler()
        self._scheduler.add_cron_job(self._minute_elapsed, minute='*')
        self._scheduler.start()
        
        
    def _minute_elapsed(self):
        for backupRepository in self.backupRepositories:
            backupRepository.check_backups()
        
        
    def _backup_required_handler(self, *args):
        self._on_backup_required(*args)
    
    def _backup_expired_handler(self, *args):
        self._on_backup_expired(*args)
                    
                    
    on_backup_required = BackupRepository._on_backup_required    
    on_backup_expired = BackupRepository._on_backup_expired



class BackupRepository(object):
    """
    Represents a backup repository, where a number of backups can be stored. 
    Requires information about the expiration of backups and the interval in 
    which backups are to be created. Will raise events accordingly.
    """
    
    def __init__(self, host, path, directories, sourceHost, sources, interval,
                 maxCount, maxAge):
        """
        :param sourceHost:
        The host of the source directories.
        :param sources:
        A list with absolute pathes to all source directories.
        :param host:
        The host of the repository.
        :param path:
        The absolute path to the repository.
        :param directories:
        The subdirectories of the repository.
        :param interval:
        An timedelta object describing the desired interval between two 
        backups.
        :param maxCount:
        The maximum amount of backups to retain. If this number is exceeded, 
        the oldest backups are to be deleted first.
        :param maxAge:
        The maximum age of all backups. Older backups are to be deleted.
        """
        
        self.__sourceHost = sourceHost
        self.__sources = sources
        
        self.host = host
        self.path = path
        self.__directories = directories
        
        self.__interval = interval
        self.__maxCount = maxCount
        self.__maxAge = maxAge
        
        self.backup_required = event.Event()
        self.backup_expired = event.Event()
            
        maxCountAge = maxCount * interval
        self.__maxAge = maxCountAge if maxCountAge > maxAge else maxAge
        
    
    def check_backups(self):
        maxBirth = datetime.datetime.now() - self.__maxAge
        minBirth = datetime.datetime.now() - self.__interval
        
        backupNeeded = True
        
        for backup in self.__backups:
            if backup.birth < maxBirth:
                self._on_backup_expired(self.host, backup.directoryName)
            if backup.birth >= minBirth:
                backupNeeded = False
                
        if backupNeeded:
            self._on_backup_required(self.host, 
                                     self._generate_new_backup_name(),
                                     self.__sourceHost,
                                     self.__sources)
            
    
    def _initialize_backups(self):
        for directory in self.__directories:
            self.__backups.append(Backup(directory))
            
            
    def _on_backup_required(self, host, newBackupDirectoryName, sourceHost,
                            sources):
        if len(self.backupRequired):
            self.backupRequired(host, newBackupDirectoryName, sourceHost,
                                sources)
          
          
    def _on_backup_expired(self, host, expiredBackupDirectoryName):
        if len(self.backupExpired):
            self.backupExpired(host, expiredBackupDirectoryName)
            
    
    
class Backup(object):
    
    def __init__(self, directoryName):
        self.directoryName = directoryName
        (self.birth,) = self._parse_name(directoryName)

    def _parse_name(self, name):
        if not name.endswith(".{}".format(SUFFIX)):
            raise ValueError("Invalid extension.")
        return (datetime.datetime.strptime(name.split('.')[0], TIMEFORMAT),)
        
