#!/usr/bin/env python

BASE_THICKNESS = 1.0 / 640.0
class Theme(object):

	# TODO swing-style, can change *everything* about how graphs are drawn from Theme.
	def setup_bar(self, context, series_index):
		""" Setup the cairo context to draw a bar for a given series. """
		raise NotImplementedError

	def draw_background(self, context):
		""" Draw the background. """
		raise NotImplementedError

	def setup_line(self, context, series_index):
		""" Setup the cairo context to draw a line and its dot for a given series. """
		raise NotImplementedError

	def setup_scatter(self, context, series_index):
		raise NotImplementedError


class CyclicTheme(Theme):

	def __init__(self, colours, etc.):
		pass


from __future__ import with_statement
import contextlib

@contextlib.contextmanager
def subcontext(ctx, x, y, width, height):
	ctx.save()
	ctx.new_path()
	ctx.rectangle(x, y, width, height)
	ctx.clip()
	ctx.translate(x, y)
	yield
	ctx.restore()


from vizier.book import PDFBook, SimplePage, GridPage, Inch, TextSpace, LEFT, BOTTOM
from vizier.plot import BarGraph, Graph, BarPlot, LinePlot
from vizier.plot.series import SmoothedLineSeries, BarSeries
from vizier.plot.axis import DateAxis, NumberAxis
from vizier.themes import CrispTheme
book = PDFBook(units=Inch)

bar_graph = BarGraph([1, 2, 3, 4, 5, 6, 7])
page = SimplePage(width=11, height=8.5, margin=0.5, spacing=0.5)
page[0] = bar_graph
book.append(page)

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

fp = open("abc.pdf", 'wb')
book.compile(fp)
fp.close()

Inches = 72.0 # points/inch

class Drawable(object):

	def draw(self, ctx, width, height):	
		raise NotImplementedError


class Book(list):

	# TODO watermarks, page numbers

	def render(self, fobj):
		raise NotImplementedError

	def __init__(self, unit=Inches):
		list.__init__(self)
		self.unit = unit


class PDFBook(Book):

	def render(self, fobj):		
		surface = cairo.PDFSurface(fobj, 1.0, 1.0)
		for page in self:
			assert(isinstance(page, Page))
			surface.set_size(page.width * self.unit, page.height * self.unit)
			page.render(cairo.Context(surface))
			surface.show_page()
		surface.finish()


class Page(object):

	# TODO watermarks

	def __init__(self, width, height, layout, margin):
		self.margin = margin
		self.width = width
		self.height = height
		self.layout = layout

	def __getitem__(self, index):
		return self.layout[*index]

	def __setitem__(self, index, value):
		self.layout[*index] = value

	@property
	def inner_bounding_box(self):
		return (self.margin, self.margin, self.width - 2.0 * self.margin, self.height - 2.0 * self.margin)

	def render(self, ctx):
		x, y, width, height = self.inner_bounding_box
		with subcontext(ctx, x, y, width, height):
			self.layout.draw(ctx, width, height)


class GridPage(object):

	def __init__(self, rows, columns, spacing, margin=0.5, units=Inch):
		Page.__init__(self, layout=GridLayout(rows, columns, spacing), margin=margin, units=units)


class SimplePage(object):

	def __init__(self, margin=0.5, units=Inch):
		Page.__init__(self, layout=GridLayout(1, 1, 0), margin=margin, units=units)


class Layout(Drawable):

	def __init__(self, spaces):
		self._spaces = spaces

	def __getitem__(self, i):
		return self._spaces[i]

	def __setitem__(self, i, value):
		self._spaces[i] = value

	def bounding_boxes(self, width, height):
		raise NotImplementedError

	def draw(self, ctx, width, height):
		for i, bb in enumerate(self.bounding_boxes(width, height)):
			x, y, width, height = bb
			space = self._spaces[i]
			if space is not None:
				with subcontext(ctx, x, y, width, height):
					space.draw(ctx, width, height)


class GridLayout(Layout):

	def __getitem__(self, index):
		r, c = index
		return self._spaces[r * self.rows + c]

	def __setitem__(self, index, value):
		r, c = index
		self._spaces[r * self.rows + c] = value

	def __init__(self, rows, columns, spacing=0):
		Layout.__init__(self, [None] * (rows * columns))
		self.rows = rows
		self.columns = columns
		self.spacing = 0

	def bounding_boxes(self, width, height):
		w = (width - self.spacing * float(self.columns - 1)) / float(self.columns)
		h = (height - self.spacing * float(self.rows - 1)) / float(self.rows)
		for i in range(self.rows):
			for j in range(self.columns):
				yield (w * j + self.spacing * j, h * i + self.spacing * i, w, h)


class VerticalLayout(Layout):

	def __init__(self, cuts, spacing=0):
		Layout.__init__(self, [None] * (len(cuts) + 1))
		self.cuts = [0] + cuts + [1]
		self.spacing = spacing

	def bounding_boxes(self, width, height):
		usable_height = height - self.spacing * (len(self.cuts) - 2)
		current_y = 0
		for i in range(len(self.cuts) - 1):
			this_height = usable_height * (self.cuts[i+1] - self.cuts[i])
			yield (0, current_y, width, this_height)
			current_y += this_height + self.spacing


class HorizontalLayout(Layout):

	def __init__(self, cuts, spacing=0):
		Layout.__init__(self, [None] * (len(cuts) + 1))
		self.cuts = [0] + cuts + [1]
		self.spacing = spacing

	def bounding_boxes(self, width, height):
		usable_width = width - self.spacing * (len(self.cuts) - 2)
		current_x = 0
		for i in range(len(self.cuts) - 1):
			this_width = usable_width * (self.cuts[i+1] - self.cuts[i])
			yield (current_x, 0, this_width, height)
			current_x += this_width + self.spacing

