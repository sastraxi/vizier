from helpers import *
from cairohelpers import *
import cairo
import math

HALF_ERROR_BAR_WIDTH = 3.0

def draw_error_bar(ctx, x, y, error):
    error_top = y + 0.5*error
    error_bottom = y - 0.5*error

    half_width, _zero = scaledsize(ctx, HALF_ERROR_BAR_WIDTH, 0)

    ctx.move_to(x - half_width, error_top)
    ctx.line_to(x + half_width, error_top)
    stroke(ctx, 1.0)

    ctx.move_to(x - half_width, error_bottom)
    ctx.line_to(x + half_width, error_bottom)
    stroke(ctx, 1.0)

    ctx.move_to(x, error_top)
    ctx.line_to(x, error_bottom)
    stroke(ctx, 1.0)


class Series(object):

    def __init__(self, name):
        self.name = name

    def average_x_frequency(self):
        pass

    def get_minimum_point(self):
        pass

    def get_maximum_point(self):
        pass

    def draw_legend_icon(self, ctx):
        x1, y1, x2, y2 = ctx.clip_extents()
        ctx.rectangle(x1, y1, x2 - x1, y2 - y1)
        ctx.fill()

    def draw_legend_label(self, ctx):
        ctx.show_text(self.name)


class AreaSeries(Series):
    """ Data given in the form of ((x1, x2), y, y-error) """

    HALF_SPACING = 1.0

    def __init__(self, name, data):
        Series.__init__(self, name)
        self.data = []
        for d in data:
            try:
                xs, y, yerr = d
            except ValueError: # need more than 2 values to unpack
                xs, y = d
                yerr = None
            self.data.append((xs, y, yerr))

    def average_x_frequency(self):
        spacings = 0
        nspacings = len(self.data) - 1
        for i in range(nspacings):
            m1 = 0.5 * (self.data[i][X][0] + self.data[i][X][1])
            m2 = 0.5 * (self.data[i+1][X][0] + self.data[i+1][X][1])
            spacings += (m2 - m1)
        return float(spacings) / nspacings

    def get_minimum_point(self):
        if not self.data: return None
        x = min(t[X][0] for t in self.data)
        y = min(t[Y] for t in self.data) # XXX if we take into account error here we'll go below 0 for graphs that probably should't
        return (x, y)

    def get_maximum_point(self):
        if not self.data: return None
        x = max(t[X][1] for t in self.data)
        y = max(t[Y] + (t[YERR] or 0) for t in self.data)
        return (x, y)

    def draw_data(self, ctx, bounds):
        half_spacing, _zero = scaledsize(ctx, self.HALF_SPACING, 0)

        # XXX total hack.
        r, g, b, a = ctx.get_source().get_rgba()

        for i, d in enumerate(self.data):
            xs, y2, y_error = d
            x1, x2 = xs
            y1 = 0

            ctx.set_source_rgba(r, g, b, a * (1.0 if i % 2 else 0.9))
            ctx.rectangle(x1 + half_spacing, y1, x2 - x1 - 2*half_spacing, y2)
            ctx.fill()

    def draw_errors(self, ctx, bounds):
        for xs, y, y_error in self.data:
            if y_error:
                draw_error_bar(ctx, 0.5 * (xs[0] + xs[1]), y, y_error)


class LineSeries(Series):

    def __init__(self, name, data, dots=True, curviness=1.0):
        Series.__init__(self, name)
        self.data = []
        for d in data:
            try:
                x, y, yerr = d
            except ValueError: # need more than 2 values to unpack
                x, y = d
                yerr = None
            self.data.append((x, y, yerr))

        self.curviness = curviness
        self.dots = dots

    def average_x_frequency(self):
        spacings = 0
        nspacings = len(self.data) - 1
        for i in range(nspacings):
            spacings += (self.data[i+1][X] - self.data[i][X])
        return float(spacings) / nspacings

    def get_minimum_point(self):
        if not self.data: return None
        x = min(t[X] for t in self.data)
        y = min(t[Y] for t in self.data) # XXX if we take into account error here we'll go below 0 for graphs that probably should't
        return (x, y)            

    def get_maximum_point(self):
        if not self.data: return None
        x = max(t[X] for t in self.data)
        y = max(t[Y] + (t[YERR] or 0) for t in self.data)
        return (x, y)

    def draw_data(self, ctx, bounds):
        dot_radius = 3 #theme.get_dot_size(self) # TODO fix this
        # TODO use bounds to clip out data

        position = [(t[X], t[Y]) for t in self.data]
        def velocity(i):
            if i == 0 or i == len(position) - 1: return (0, 0)
            if math.isnan(position[i+1][Y]) or math.isnan(position[i-1][Y]): return (0, 0)
            x, y = (position[i+1][0] - position[i-1][0], position[i+1][1] - position[i-1][1])
            x, y = 0.5 * x, 0.5 * y
            return (x, y)

        needpt = True
        for i in range(0, len(position)):
            if math.isnan(position[i][Y]):
                stroke(ctx, 2.0)
                needpt = True
                continue
            
            if needpt:
                ctx.move_to(*position[i])
                needpt = False
                continue

            px0, py0 = position[i-1]
            px1, py1 = position[i]
            vx0, vy0 = velocity(i-1)                        
            vx1, vy1 = velocity(i)

            # the current point, due to curve_to and the above move_to is right now x0, y0 = (px0, py0)
            # however, we can't assert it due to rounding errors.
            # assert(ctx.get_current_point() == (px0, py0))

            x1, y1 = (px0 + 0.5 * self.curviness * vx0, py0 + 0.5 * self.curviness * vy0)
            x2, y2 = (px1 - 0.5 * self.curviness * vx1, py1 - 0.5 * self.curviness * vy1)
            x3, y3 = (px1, py1)
            ctx.curve_to(x1, y1, x2, y2, x3, y3)

        stroke(ctx, 2.0)

        if self.dots:
            for p in position:
                if not math.isnan(p[Y]):
                    dot(ctx, p[X], p[Y], dot_radius)
        
    def draw_errors(self, ctx, transform):
        for x, y, y_error in self.data:
            if y_error:
                draw_error_bar(ctx, x, y, y_error)


class Threshold(Series):

    def __init__(self, type, name, value):
        Series.__init__(self, str(value) + " - " + type + ": " + name)
        self.type = type
        self.value = value
    
    def get_minimum_point(self):
        return (None, self.value)

    def get_maximum_point(self):
        return (None, self.value)

    def draw(self, ctx, bounds):
        ctx.new_path()
        ctx.move_to(bounds[X1], self.value)
        ctx.line_to(bounds[X2], self.value)
        stroke(ctx, 1.0)

    def draw_legend_icon(self, ctx):
        x1, y1, x2, y2 = ctx.clip_extents()
        roundedrect(ctx, x1 + 1, y1 + 1, x2 - x1 - 2, y2 - y1 - 2, (x2 - x1) * 0.3)
        stroke(ctx, 1.0)

    def draw_legend_label(self, ctx):
        Series.draw_legend_label(self, ctx)
        # TODO same colour as icon for e.g. "Warning" and bold!

