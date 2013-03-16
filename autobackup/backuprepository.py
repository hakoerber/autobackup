import event
import datetime
import filesystem

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
        
        # Quite shitty, have to figure out how to assign the methods on a class
        # level without reordering the classes.
        self.on_backup_required = BackupRepository._on_backup_required    
        self.on_backup_expired = BackupRepository._on_backup_expired

        
        
    def _minute_elapsed(self):
        for backupRepository in self.backupRepositories:
            backupRepository.check_backups()
        
        
    def _backup_required_handler(self, *args):
        self._on_backup_required(*args)
    
    def _backup_expired_handler(self, *args):
        self._on_backup_expired(*args)
                    




class BackupRepository(object):
    """
    Represents a backup repository, where a number of backups can be stored. 
    Requires information about the expiration of backups and the interval in 
    which backups are to be created. Will raise events accordingly.
    """
    
    def __init__(self, 
                 repository_location, repository_directories,
                 source_locations,
                 interval, maxCount, maxAge):
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
        self.repository_location = repository_location
        self.repository_directories = repository_directories
        
        self.source_locations = source_locations        
        
        self.interval = interval
        self.maxCount = maxCount
        self.maxAge = maxAge
        
        self.backup_required = event.Event()
        self.backup_expired = event.Event()
            
        maxCountAge = maxCount * interval
        self.maxAge = maxCountAge if maxCountAge > maxAge else maxAge
        
        self.backups = []
        for directory in self.source_locations:
            self.backups.append(Backup(directory))
        
    
    def check_backups(self):
        maxBirth = datetime.datetime.now() - self.maxAge
        minBirth = datetime.datetime.now() - self.interval
        
        backupNeeded = True
        
        for backup in self.backups:
            if backup.birth < maxBirth:
                self._on_backup_expired(backup.location)
            if backup.birth >= minBirth:
                backupNeeded = False
                
        if backupNeeded:
            self._on_backup_required(self.repository_location, 
                                     self.source_locations,
                                     self._get_latest_backup)
            
    
            
    def _on_backup_required(self, repository_location, source_locations,
                            latest_backup):
        if len(self.backupRequired):
            self.backupRequired(host, repository_location, source_locations,
                                latest_backup)
          
          
    def _on_backup_expired(self, location):
        if len(self.backupExpired):
            self.backupExpired(host, expiredBackupDirectoryName)
            
    
    
class Backup(object):
    
    def __init__(self, location):
        self.directoryName = location
        (self.birth,) = self._parse_name(location.path)

    def _parse_name(self, name):
        if not name.endswith(".{}".format(SUFFIX)):
            raise ValueError("Invalid extension.")
        return (datetime.datetime.strptime(name.split('.')[0], TIMEFORMAT),)
        
