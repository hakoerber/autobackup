import datetime

class Cronjob(object):

    def __init__(self, schedule_string):
        self.schedule_string = schedule_string


    def get_latest_occurence(self):
        return datetime.datetime.now()

