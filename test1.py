#!/usr/bin/env python

from vizier.book import PDFBook, SimplePage, GridPage, Inch, LEFT, BOTTOM#, TextSpace
from vizier.plot import ContinuousPlot, X
from vizier.series import LineSeries, AreaSeries, Threshold
#from vizier.plot.series import SmoothedLineSeries, BarSeries
#from vizier.plot.axis import DateAxis, NumberAxis
#from vizier.themes import CrispTheme
book = PDFBook()

import datetime
import random

ranges = []
midpoints = []
data = []
errors = []
for x in range(24):
    ranges.append((x, x+1))
    midpoints.append(x + 0.5)
    #ranges.append((datetime.datetime(2011, 10, 9, x, 0, 0), datetime.datetime(2011, 10, 9, x+1, 0, 0)))
    #midpoints.append(ranges[-1][0] + datetime.timedelta(minutes=30))
    data.append(data[-1] + 110 + random.random() * 40 if x != 0 else 0)
    errors.append(random.random() * 400)

complex_graph = ContinuousPlot(title="Continuous Effluent Flow", subtitle="These words sound scientific", legend=True, y_grid=(0, 1500))
complex_graph.grid[X] = (0, 3) #times[0][0], datetime.timedelta(hours=3))
complex_graph.add(

    # each tuple in the data is (x, y, y-error)
    LineSeries("+500", zip(midpoints, [d + 400 + random.random() * 1800 for d in data]), curviness=1),

    # each tuple in the data is (x[start, end], y, y-error)
    AreaSeries("Raw", zip(ranges, data, errors)),
    
    # show a threshold at y=4.25
    Threshold("Warning", "High Water Usage (Design) [5]", 4678),
    Threshold("Warning", "High Water Usage (MOE) [6]", 7500)

)

page = GridPage(width=8.5*Inch, height=11*Inch, rows=2, columns=1, margin=0.5*Inch, spacing=0.5*Inch)
page[0, 0] = complex_graph
page[0, 1] = page[0, 0]
book.append(page)

'''
# data is defined in (x,y) tuples
import datetime
import random()
water_level = [(datetime.date(2010, 6, i+1), 3 + random() * 4) for i in range(30)]
daylight_hours = [(datetime.date(2010, 6, i+1), 13.0 - 0.02 * i - (random() ** 10) * 5.5) for i in range(30)]

complex_graph = Graph(x=DateAxis('Date', '%yyyy-%mm-%dd'), \
                      y=NumberAxis('Water Level (m)/Sunlight (h)', grid_interval=1.0) \
                      theme=CrispTheme)
complex_graph.add_series(SmoothedLineSeries("Water Level", water_level, line_size=1.5, dot_size=2.0, dot_inner_size=1.0))
complex_graph.add_series(BarSeries("Daylight Hours", daylight_hours, spacing=0)) # can pass x,y lambda functions here to xform data tuples for drawing
complex_graph.y.add_threshold(6.5, "Possible flooding of Dock B")
complex_graph.x.add_threshold(datetime.date(2010, 6, 21), "Summer Solstice")
complex_graph.x.grid_interval = None

vlayout = VerticalLayout(0.1, 0.6) # splits a space vertically into 3.
vlayout[0] = TextSpace("This layout", halign=LEFT)
vlayout[1] = TextSpace("is split up into 3")
vlayout[2] = TextSpace("non-uniformly!", valign=BOTTOM)

page = GridPage(2, 2, width=11, height=8.5)
page[0, 0] = TextSpace("This happens to be a graph.")
page[0, 1] = complex_graph
page[1, 0] = complex_graph
page[1, 1] = vlayout
book.append(page)
'''

book.compile("abc.pdf")
