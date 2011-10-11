#!/usr/bin/env python

from vizier.book import PDFBook, SimplePage, GridPage, Inch, LEFT, BOTTOM#, TextSpace
from vizier.plot import VerticalBarPlot, ScatterPlot
#from vizier.plot.series import SmoothedLineSeries, BarSeries
#from vizier.plot.axis import DateAxis, NumberAxis
#from vizier.themes import CrispTheme
book = PDFBook()

bar_graph = VerticalBarPlot([1, 2, 3, 4, 5, 6, 7])
page = SimplePage(width=11*Inch, height=8.5*Inch, margin=0.5*Inch)
page[0] = bar_graph
book.append(page)

page = GridPage(width=8.5*Inch, height=11*Inch, rows=2, columns=2, margin=0.5*Inch, spacing=0.5*Inch)
page[0, 0] = ScatterPlot([(0, 0), (0.1, 0.3), (1, 0.1), (2, 2.3), (3, 3)])
page[0, 1] = page[0, 0]
page[1, 0] = page[0, 0]
page[1, 1] = page[0, 0]
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
