import datetime

ranges = (range(60), range(24), range(1,32), range(1,13), range(1900,3000),
          range(1,8)) # Creating year 3000 problem

class Cronjob(object):
    """
    Crontab format:
    minute hour day month year weekday
    """
    def __init__(self, schedule_string):
        self.cronstring = schedule_string
        self.schedule = _get_single_positions(schedule_string)
        for i in range(6):  
            self.schedule[i] = _parse_string_to_range(self.schedule[i], i)
        

    def matches(self, d):
        d_schedule = _datetime_to_tuple(d)
        for i in range(6):
            if not d_schedule[i] in self.schedule[i]:
                return False
        return True
        
    def has_occured_between(self, d1, d2):
        if not d1 <= d2:
            raise ValueError("d1 has to be older than or equal to d2.")
        min_val = self.get_min_time()
        max_val = self.get_max_time()
        if d1 < min_val:
            d1 = min_val
        if d2 > max_val:
            d2 = max_val
        if d2 < min_val:
            return False
        if d1 > max_val:
            return False
        if (d1 < min_val and d2 < min_val) or (d1 > max_val and d2 > max_val):
            return False
        most_recent_occurence = self.get_most_recent_occurence(d2)
        return most_recent_occurence >= d1
        
    def has_occured_since(self, d):
        return self.has_occured_between(d, datetime.datetime.now())


    def get_most_recent_occurence(self, d=None):
        if not d:
            d = datetime.datetime.now()
        d_schedule = _datetime_to_tuple(d)
        latest_schedule = [0,0,0,0,0, None]

        # we go from the most significant to the least significant position,
        # from year to minute
        # for each position we compare the d_schedule value with all possible
        # values in self.schedule:
        #
        # we choose the hightest value in self.schedule that is lower or equal
        # than the value of d_schedule
        #
        # if we choose a lower value than d_schedule, we have change the
        # procedure: in all following lower significant positions, instead of
        # comparing, we always choose the hightest value from self.schedule[i]
        #
        # if we choose the equal value, we just continue with our procedure
        #
        # if we cannot choose a lower or equal value that means that there is no
        # matching for the current i+1 position. so we have to choose the next 
        # lower possible value for the i+1 position. if this is not possible,
        # either because i+1 does not exist (we are currently at the year 
        # position) or there already is the lowest possible value at position
        # i+1, that means that d_schedule is older than every possible value in 
        # self.schedule, so we raise an error
        #
        # this is shittier than everything, but it somehow passes the tests
        max_only_now = False
        i = 5
        while i > 0:
            i -= 1
            if not max_only_now:
                lower_equal_range = [val for val in self.schedule[i] \
                                     if val <= d_schedule[i]]

                if len(lower_equal_range) == 0:
                    self._set_lower_value(latest_schedule, i)
                    latest_schedule[i] = max(self.schedule[i])
                    max_only_now = True
                    continue
                    
                lower_equal_value = max(lower_equal_range)
                is_equal_value = (lower_equal_value == d_schedule[i])
                
                latest_schedule[i] += lower_equal_value
            else:
                latest_schedule[i] += max(self.schedule[i])
                
            if not is_equal_value:
                max_only_now = True
                    
        return _tuple_to_datetime(latest_schedule)
            
            
    def _set_lower_value(self, latest_schedule, i):
        if i == 4:
            raise ValueError("d is older than every possible value in "
                             "this crontab")
        # not using indices, as that would rely on self.schedule to
        # be sorted
        # lets revert to the last postion
        i += 1
        # lower it to the next possible value and continue
        last_value = latest_schedule[i]
        lower_values = [val for val in self.schedule[i] \
                        if val < last_value]
        if len(lower_values) == 0:
            _set_lower_value(self, latest_schedule, i)
        latest_schedule[i] = max(lower_values) 
            
    def get_max_time(self):
        return _tuple_to_datetime([max(val) for val in self.schedule])
        
    
    def get_min_time(self):
        return _tuple_to_datetime([min(val) for val in self.schedule])

       
def _datetime_to_tuple(d):
    (d_year, d_month, d_day, d_hour, d_minute, _, d_weekday, _, _) = \
        d.timetuple()    
    return (d_minute, d_hour, d_day, d_month, d_year, d_weekday)
    
    
def _tuple_to_datetime(t):
    return datetime.datetime(year=t[4], month=t[3], day=t[2], hour=t[1],
        minute=t[0])


def _get_single_positions(schedule_string):
    return schedule_string.split()[:6]

    
# parses a given single field of a crontab line, such as 5-59/6
# supported are:
#     * to match all possible values of a field, for example matches a * in a
#       month field range(1,13)
#     - to match a certain range, for example matches 4-20 in a day of month
#       field range(4,21)
#     , to match a set of values, all separated by commas. can be used together
#       with hyphens and *, although the latter is redundant
#     / to specify a certain step. can be used either with * or a specific 
#       range given by a hyphen expression, for example matches */5 in the hour
#       field range(0,24,5) and 13-29/4 in the day of month field 
#       range(13x,30,4). Cannot be used with comma separated values, except the
#       step is 1, which is of course redundant.
#       
def _parse_string_to_range(string, index):
    rest = string.strip()
    
    # first, let's look for a step value:
    parts = rest.split('/')
    step = int(parts[1]) if len(parts) == 2 else 1
    rest = parts[0]
    
    possible_range = []
    
    # now, everything else might be "*", "x-y" or "z" separated by commas:
    parts = rest.split(',')
    if len(parts) > 1 and step != 1:
        raise Exception( "Step specifiers are not allowed when using comma "
            "expressions.")

    for part in parts:
        part = part.strip()
        if part == '*':
            possible_range += ranges[index]
        elif part.isdigit():
            possible_range += [int(part)]
        elif '-' in part:
            start_end = part.split('-')
            if len(start_end) != 2 or \
                    not start_end[0].isdigit() or \
                    not start_end[1].isdigit():
                raise Exception("Invalid field.")
            possible_range += range(int(start_end[0]), int(start_end[1]) + 1)
        else:
            raise Exception("Invalid field.")
    
    # now we have some list containing all possible values, maybe multiple 
    # times, and a step value. If the step is not 1, the list must be a
    # cohesive list, so we can use range() with min() and max() to generate
    # the finished lists
    # otherwise, we will just remove double values from the list
    output_list = []
    if step == 1:
        # look here
        # http://www.peterbe.com/plog/uniqifiers-benchmark
        # for different approaches to uniqifying. This one does not preserve the
        # order of the elements, but they are not sorted anyway, so we have to
        # sort afterwards
        output_list = list(set(possible_range))
        output_list.sort()
    else:
        output_list = range(min(possible_range), max(possible_range)+1, step)
        
    return output_list
    
    
