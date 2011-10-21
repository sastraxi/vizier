#!/usr/bin/env python

from vizier.book import PDFBook, SimplePage, GridPage, Inch, LEFT, BOTTOM
from vizier.plot import ContinuousPlot, X, Y
from vizier.series import LineSeries, AreaSeries, Threshold
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
                               legend=True,
                               x_grid=(0, 3), x_labels=True, x_title="Hour of Day",
                               y_grid=(0, 1500), y_labels=True, y_title="Rate (L/min)",
                               x_formatter=lambda h: "%d:00" % (h%24,))
complex_graph.add(

    # each tuple in the data is (x, y, y-error)
    LineSeries("Pval + 500", zip(midpoints, [d + 400 + random.random() * 1800 for d in data]), curviness=1),

    # each tuple in the data is (x[start, end], y, y-error)
    AreaSeries("Raw", zip(ranges, data, errors)),
    
    # show a threshold at y=4.25
    Threshold("Warning", "High Water Usage (Design) [5]", 4678),
    Threshold("Warning", "High Water Usage (MOE) [6]", 7500)

)

complex_graph2 = ContinuousPlot(title="Only Lines Here", subtitle="This is a test of x spacing, among other things.", legend=False)
complex_graph2.grid[Y] = (0, 10)
complex_graph2.add(

    LineSeries("Random(5, 55)", [(0.5 + (x / 2.0), 5 + 50 * random.random()) for x in range(20)], curviness=0),
    LineSeries("Random(20, 40)", [(0.5 + (x / 3.0), 20 + 20 * random.random(), random.random() * 2) for x in range(30)])

)

page = GridPage(width=8.5*Inch, height=11*Inch, rows=2, columns=1, margin=0.5*Inch, spacing=0.5*Inch)
page[0, 0] = complex_graph
page[0, 1] = complex_graph2
book.append(page)
book.compile("abc.pdf")
