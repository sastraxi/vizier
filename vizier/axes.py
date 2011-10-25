from helpers import *
from cairohelpers import *
import math
import datetime

STANDARD_EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0)

def labelstr(x):
    s = str(x)
    return s[:-2] if s.endswith('.0') else s

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
        
        Axis.__init__(self, title, major, minor)
    
    def as_number(self, val):
        return (val - DateTimeAxis.EPOCH).total_seconds()

    def markers(self, lower, upper):

        for (interval, MarkerType) in self._marker_intervals:
            start = math.floor(lower / interval) * interval
            #for n in frange(start, upper + EPSILON, interval):


class AutoDatetimeAxis(Axis):

    def __init__(self, title, epoch=STANDARD_EPOCH):
        Axis.__init__(self, title)

    def as_number(self, val):
        return (val - DateTimeAxis.EPOCH).total_seconds()

    
    