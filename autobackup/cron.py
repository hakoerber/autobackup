import datetime

ranges = (range(60), range(24), range(1,32), range(1,13), range(1,8), 
          range(1900,3000)) # Creating year 3000 problem

class Crontab(object):
    """
    Crontab format:
    minute hour day month weekday year
    """
    def __init__(self, schedule_string):
        self.schedule = (0, 0, 0, 0, 0, 0)
        self.schedule = _parse_schedule_string(schedule_string)
        for i in range(6):  
            self.schedule[i] = _get_values(self.schedule[i], i)
        

    def matches(self, datetime):
        (d_year, d_month, d_day, d_hour, d_minute, _, d_weekday, _, _) = \
            datetime.timetuple()
        d_schedule = (d_minute, d_hour, d_day, d_month, d_weekday, d_year)
        for i in range(6):
            if not d_schedule[i] in self.schedule[i]:
                return False
        return True


    def get_latest_occurence(self):
        now = datetime.datetime.now()

        
    def update(self):
        now = datetime.datetime.now()
        (self.year, self.month, self.day, self.hour, self.minute, _, 
            self.weekday, _, _) = now.timetuple()
        
       
    
def _get_values(string, index):
    if string.strip() == '*':
        return ranges[index]
    if ',' in string:
        parts = [int(val) for val in string.split(',')]
        return parts
    if '-' in string:
        parts = [int(val) for val in string.split('-')]
        if len(parts) != 2:
            Exception("Invalid value.")
        return range(parts[0], parts[1] + 1)
    return [int(string)]
    
    
def _parse_schedule_string(schedule_string):
    #schedules = []
    #for schedule in schedule_string.split(';'):
    #    schedules.append(schedule.split())
    #return schedules
    return schedule_string.split()[:6]
