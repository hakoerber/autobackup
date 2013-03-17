import datetime
import os

import apscheduler.scheduler as scheduler #@UnresolvedImport

import event

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
    
    def __init__(self, backup_repositories):
        """
        :param backup_repositories: A list of BackupRepositories to manage.
        :type backup_repositories: list of BackupRepository instances
        """
        self.backup_repositories = backup_repositories
        
        # We will just handle all events raised by the backup_repositories and
        # re-raise them with the same information.
        self.backup_required = event.Event()
        self.backup_expired = event.Event()
        for repository in backup_repositories:
            repository.backup_required += self._backup_required_handler
            repository.backup_expired  += self._backup_expired_handler

        self._scheduler = scheduler.Scheduler()
        self._scheduler.add_cron_job(self._minute_elapsed, minute='*')
        self._scheduler.start()
        
        # Quite shitty, have to figure out how to assign the methods on a class
        # level without reordering the classes.
        self._on_backup_required = BackupRepository._on_backup_required    
        self._on_backup_expired = BackupRepository._on_backup_expired

        
        
    def _minute_elapsed(self):
        for repository in self.backup_repositories:
            repository.check_backups()
        
        
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
                 interval, max_count, max_age):
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
        self.max_count = max_count
        self.max_age = max_age
        
        self.backup_required = event.Event()
        self.backup_expired = event.Event()
            
        max_cout_age = max_count * interval
        self.max_age = max_cout_age if max_cout_age > max_age else max_age
        
        self.backups = []
        for directory in self.source_locations:
            self.backups.append(Backup(directory))
        
    
    def check_backups(self):
        max_birth = datetime.datetime.now() - self.max_age
        min_birth = datetime.datetime.now() - self.interval
        
        backup_needed = True
        
        for backup in self.backups:
            if backup.birth < max_birth:
                self._on_backup_expired(backup.location)
            if backup.birth >= min_birth:
                backup_needed = False
                
        if backup_needed:
            self._on_backup_required(self.repository_location, 
                                     self.source_locations,
                                     self._get_latest_backup)
            
    
            
    def _on_backup_required(self, repository_location, source_locations,
                            latest_backup):
        if len(self.backup_required):
            self.backup_required(repository_location, source_locations,
                                 latest_backup)
          
          
    def _on_backup_expired(self, location):
        if len(self.backup_expired):
            self.backup_expired(location)
            
    def _get_latest_backup(self):
        if len(self.backups) == 0:
            return None
        latest = self.backups[0]
        for backup in self.backups:
            if backup.birth > latest.birth:
                latest = backup
        return latest
            
    
    
class Backup(object):
    
    def __init__(self, location):
        self.location = location
        (self.birth,) = _parse_name(location.path)


def _parse_name(self, path):
    if not path.endswith(".{}".format(SUFFIX)):
        raise ValueError("Invalid extension.")
    name = os.path.basename(path)
    return (datetime.datetime.strptime(split('.')[0], TIMEFORMAT),)
        
