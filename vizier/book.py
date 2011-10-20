from __future__ import with_statement

import cairo
from cairohelpers import *
from .plot import Drawable

LEFT = -1
CENTER = 0
RIGHT = 1

TOP = -1
BOTTOM = 1

Inch = 72.0 # points/inch

class Book(list):

    # TODO watermarks, page numbers

    def compile(self, fobj):
        raise NotImplementedError

    def __init__(self):
        list.__init__(self)

class PDFBook(Book):

    def compile(self, fobj):        
        surface = cairo.PDFSurface(fobj, 1.0, 1.0)
        for page in self:

            assert(isinstance(page, Page))

            surface.set_size(page.width, page.height)
            ctx = cairo.Context(surface)
            page.render(ctx)

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
        return self.layout[index]

    def __setitem__(self, index, value):
        self.layout[index] = value

    @property
    def inner_bounding_box(self):
        return (self.margin, self.margin, self.width - 2.0 * self.margin, self.height - 2.0 * self.margin)

    def render(self, ctx):
        x, y, width, height = self.inner_bounding_box
        with subcontext(ctx, x, y, width, height):
            self.layout.draw(ctx, width, height)

class GridPage(Page):

    def __init__(self, width, height, rows, columns, spacing, margin):
        Page.__init__(self, width, height, layout=GridLayout(rows, columns, spacing), margin=margin)

class SimplePage(Page):

    def __init__(self, width, height, margin):
        Page.__init__(self, width, height, layout=SimpleLayout(), margin=margin)

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

class SimpleLayout(Layout):

    def __init__(self):
        Layout.__init__(self, [None])
    
    def bounding_boxes(self, width, height):
        return [(0, 0, width, height)]

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
        self.spacing = spacing

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
