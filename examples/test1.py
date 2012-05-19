#!/usr/bin/env python

from vizier.book import PDFBook, SimplePage, GridPage, Inch, LEFT, BOTTOM
from vizier.plot import ContinuousPlot, X, Y
from vizier.series import LineSeries, AreaSeries, Threshold
from vizier.themes import SlickTheme, MarkerType
from vizier.axes import *
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

complex_graph = ContinuousPlot(title="Continuous Effluent Flow",
                               subtitle="These words sound scientific",
                               identifier="21/12/abc/123/def",
                               legend=True,
                               #x_axis=DatetimeAxis("Hour of Day", major=datetime.timedelta(minutes=180), minor=datetime.timedelta(minutes=60)),
                               x_axis=NumberAxis("Hour of Day", major=3.0, minor=1.0),
                               y_axis=NumberAxis("Rate (L/min)", major=1500, minor=250),
                               theme=SlickTheme())
complex_graph.add(

    # each tuple in the data is (x, y, y-error)
    LineSeries("Pval + 500", zip(midpoints, [d + 400 + random.random() * 1800 for d in data]), curviness=1),

    # each tuple in the data is (x[start, end], y, y-error)
    AreaSeries("Raw", zip(ranges, data, errors)),
    
    # show a threshold at y=4.25
    Threshold(5, "Warning", "High Water Usage (Design)", 4678),
    Threshold(6, "Warning", "High Water Usage (MOE)", 7500)

)

complex_graph2 = ContinuousPlot(title="Only Lines Here",
                                subtitle="This is a test of x spacing and NaN handling.",
                                date="July 1, 2009",
                                identifier="00/12/abc/123/def",
                                legend=False,
                                y_min=0.0,
                                y_max=60.0,
                                theme=SlickTheme())
complex_graph2.axis[X] = NumberAxis(None, major=3.0)
complex_graph2.axis[Y] = NumberAxis(None, major=10, minor=2.5)
complex_graph2.theme.minor_axis_labels[Y] = True
complex_graph2.theme.minor_axis_labels[X] = True
complex_graph2.theme.minor_axis_style[Y] = MarkerType.INNER_TICKS
complex_graph2.theme.minor_axis_style[X] = MarkerType.LINES
complex_graph2.add(

    LineSeries("Random(5, 55)", [(0.5 + (x / 2.0), 5 + 50 * random.random()) for x in range(20)], curviness=0, raw=True),
    LineSeries("Random(20, 40)", [(0.5 + (x / 3.0), (20 + 20 * random.random()) if random.random() < 0.8 else float('nan'), random.random() * 2) for x in range(30)], curviness=1, nan_holes=True),
    LineSeries("Just NaNs", [(0.5 + (x / 3.0), float('nan')) for x in range(30)], nan_holes=True)

)

page = GridPage(width=8.5*Inch, height=11*Inch, rows=2, columns=1, margin=0.5*Inch, spacing=0.5*Inch)
page[0, 0] = complex_graph
page[0, 1] = complex_graph2
book.append(page)
book.compile("test1.pdf")
