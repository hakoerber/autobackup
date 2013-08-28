import datetime
import os


import event
import cron

SUFFIX     = 'bak'
# Timeformat used by the datetime.strptime() method of
TIMEFORMAT = '%Y-%m-%dT%H:%M:%S'
FORMAT     = "{0}.{1}".format(TIMEFORMAT, SUFFIX)

class Tag(object):
    def __init__(self, cron, max_age, max_count):
        self.cron = cron
        self.max_age = max_age
        self.max_count = max_count


class BackupRepository(object):
    """
    Represents a backup repository, where a number of backups can be stored.
    Requires information about the expiration of backups and the interval in
    which backups are to be created. Will raise events accordingly.
    """

    def __init__(self,
                 source_locations,
                 repository_location,
                 repository_directories,
                 tags):
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

        self.backup_required = event.Event()
        self.backup_expired = event.Event()

        # tag-name -> backup[]
        self.backups = {}
        for directory in self.source_locations:
            backup = Backup(directory, tags)
            self.backups[backup.tag] = backup


    def check_backups(self):
        now = datetime.datetime.now()
        for tag in self.tags:
            # "tag" looks like: cron, max_age, max_count
            max_age = tag[1]
            max_count = tag[2]
            while len(self.backups[tag]) > max_count:
                latest_backup = self._get_latest_backup(tag)
                self._on_backup_expired(latest_backup)
                del latest_backup
            for backup in self.backups[tag]:
                if backup.birth < max_age:
                    self._on_backup_expired(backup.location)
                    del backup
            if tag[0].matches(now):
                self._on_backup_required(self.repository_location,
                                         self.source_locations,
                                         self._get_latest_backup(),
                                         tag)




    def _on_backup_required(self, repository_location, source_locations,
                            latest_backup, tag):
        if len(self.backup_required):
            self.backup_required(repository_location, source_locations,
                                 latest_backup, new_backup_dirname)

            self.backups.append(Backup(os.path.join(
                                                  self.repository_location.path,
                                                  new_backup_dirname)))


    def _on_backup_expired(self, location):
        if len(self.backup_expired):
            self.backup_expired(location)
            del([backup for backup in self.backups \
                        if backup.location == location][0])


    def _get_latest_backup(self, tag=None):
        if tag is None:
            backups = []
            for tag in self.backups:
                backups.extend(self.backups[tag])
        else:
            backups = self.backups[tag]
        if len(backups) == 0:
            return None
        latest = backups[0]
        for backup in backups:
            if backup.birth > latest.birth:
                latest = backup
        return latest

    def _get_oldest_backup(self, tag):
        if tag is None:
            backups = []
            for tag in self.backups:
                backups.extend(self.backups[tag])
        else:
            backups = self.backups[tag]

        if len(backups) == 0:
            return None
        oldest = backups[0]
        for backup in backups:
            if backup.birth < oldest.birth:
                oldest = backup
        return oldest



class Backup(object):

    def __init__(self, dirname, tags):
        self.dirname = dirname
        self.tags = tags
        (self.tag, self.birth) = _parse_name(location.path)

def _parse_name(path):
    if not dirname.endswith(".{}".format(SUFFIX)):
        raise ValueError("Invalid extension.")
    return ("taggy", datetime.datetime.strptime(dirname.split('.')[0], TIMEFORMAT))

