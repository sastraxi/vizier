from helpers import *
from cairohelpers import *
import math
import datetime

STANDARD_EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0)

# supports intervals of 1 year to 1 second
DT_INTERVALS = [(datetime.timedelta(days=365), '%d %b %Y'),
                (datetime.timedelta(days=28), '%d %b %Y'),  # XXX: add true month support
                (datetime.timedelta(days=7), '%d %b'),
                (datetime.timedelta(days=1), '%d %b'),
                (datetime.timedelta(hours=3), '%H:%M'),
                (datetime.timedelta(hours=1), '%H:%M'),
                (datetime.timedelta(minutes=10), '%H:%M'),
                (datetime.timedelta(minutes=1), '%M:%S'),
                (datetime.timedelta(seconds=10), '%M:%S'),
                (datetime.timedelta(seconds=1), '%M:%S')]

# supports intervals less than 10^9 (one billion)
def n_intervals():
    n = 9
    while True:
        yield 10 ** n
        yield 0.5 * (10 ** n)
        n -= 1

def labelstr(x):
    s = str(x)
    return s[:-2] if s.endswith('.0') else s

def dtstr(x, fmt, epoch=STANDARD_EPOCH):
    dt = epoch + datetime.timedelta(seconds=x)
    return dt.strftime(fmt)

class Always(object):
    def __init__(self, n):
        self.n = n
        
        
class PerMajor(Always):
    pass


MarkerType = enum('INNER_TICKS', 'OUTER_TICKS', 'LINES')

class Marker(object):
    def __init__(self, number, label):
        self.number = number
        self.label = label

    def __iter__(self):
        """ 
        Allow expansion as if this were a (number, label) tuple, e.g.
        number, label = marker
        """
        return iter([self.number, self.label])

class MajorMarker(Marker):
    pass

class MinorMarker(Marker):
    pass
 
class Axis(object):

    def __init__(self, title, major=Always(5), minor=PerMajor(4)):
        """
        None/Always(x)/x
        """
        self.title = title
        self.major = major
        self.minor = minor

    def as_number(self, obj):
        """ Converts axis data to data that vizier can work with--numbers, brah! """
        raise NotImplementedError

    def markers(self, lower, upper):
        """ Generator function, yield all MajorMarkers then all MinorMarkers. """
        raise NotImplementedError


class NumberAxis(Axis):

    def __init__(self, title, major=Always(5), minor=PerMajor(4)):
        Axis.__init__(self, title, major, minor)

    def as_number(self, obj):
        return obj

    def markers(self, lower, upper):

        size = upper - lower

        if isinstance(self.major, Always):
            major = size / float(self.major.n - 1)
        else:
            major = self.major

        if isinstance(self.minor, PerMajor):
            if major is not None:
                minor = major / float(self.minor.n + 1)
            else:
                minor = None
        else:
            minor = self.minor

        marker_intervals = []
        if major: marker_intervals.append([major, MajorMarker])        
        if minor: marker_intervals.append([minor, MinorMarker])

        for (interval, MarkerType) in marker_intervals:
            start = math.floor(lower / interval) * interval
            for n in frange(start, upper + EPSILON, interval):
                if n >= lower:
                    yield MarkerType(n, labelstr(n))
    

class AutoNumberAxis(NumberAxis):
    
    def __init__(self, title, major=None, minor=None):
        NumberAxis.__init__(self, title, major=None, minor=None)
        
        if isinstance(self.major, Always):
            raise ValueError("Exact number of major markers does not make sense for an AutoNumberAxis")
        if isinstance(self.minor, PerMajor):
            raise ValueError("Exact number of minor markers does not make sense for a AutoNumberAxis")        
    
    def find_intervals(self, size):
        for interval in n_intervals():  # go through acceptable intervals from largest to smallest
            if size // interval >= 4:  # once we find one that fits in the data range at least twice
                return interval, (interval / 5.0)  # we take that one as the major interval, and divide by 5 to get the minor                   

    def markers(self, lower, upper):
        
        size = upper - lower
        
        major = self.find_intervals(size)[0]
        minor = self.find_intervals(size)[1]
        
        marker_intervals = []
        marker_intervals.append([major, MajorMarker])
        marker_intervals.append([minor, MinorMarker])

        for (interval, MarkerType) in marker_intervals:
            start = math.floor(lower / interval) * interval
            for n in frange(start, upper + EPSILON, interval):
                if n >= lower:
                    yield MarkerType(n, labelstr(n))                
            
class DatetimeAxis(Axis):
    
    def __init__(self, title, major=None, minor=None, epoch=STANDARD_EPOCH):
        if isinstance(major, datetime.timedelta):
            major = major.total_seconds()
        if isinstance(minor, datetime.timedelta):
            minor = minor.total_seconds()   
            
        if isinstance(major, Always):
            raise ValueError("Exact number of major markers does not make sense for a DatetimeAxis")
        if isinstance(minor, PerMajor):
            raise ValueError("Exact number of minor markers does not make sense for a DatetimeAxis")
        
        self.epoch = epoch
        Axis.__init__(self, title, major, minor)
    
    def as_number(self, val):
        return (val - self.epoch).total_seconds()
    
    #def markers(self, lower, upper):
        
        #for (interval, MarkerType) in self._marker_intervals:
            #start = math.floor(lower / interval) * interval
            #for n in frange(start, upper + EPSILON, interval):
    

class AutoDatetimeAxis(DatetimeAxis):

    def __init__(self, title, epoch=STANDARD_EPOCH):
        DatetimeAxis.__init__(self, title)

    def find_intervals(self, size):
        for i, interval in enumerate(DT_INTERVALS):  # go through acceptable intervals from largest to smallest
            if size // interval[0].total_seconds() >= 2:  # once we find one that fits in the data range at least twice
                return DT_INTERVALS[i], DT_INTERVALS[i+1]  # we take that one as the major interval, and the next smallest as the minor

    def markers(self, lower, upper):
        
        size = upper - lower
        
        if self.major is None:
            major = self.find_intervals(size)[0][0].total_seconds()
            x_fmt = self.find_intervals(size)[0][1]
        else:
            major = self.major
            
        if self.minor is None:
            minor = self.find_intervals(size)[1][0].total_seconds()
        else:
            minor = self.minor
        
        marker_intervals = []
        if major: marker_intervals.append([major, MajorMarker])
        if minor: marker_intervals.append([minor, MinorMarker])

        for (interval, MarkerType) in marker_intervals:
            start = math.floor(lower / interval) * interval
            for n in frange(start, upper + EPSILON, interval):
                if n >= lower:
                    yield MarkerType(n, dtstr(n, x_fmt))    
    