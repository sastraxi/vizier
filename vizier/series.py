from helpers import *
from cairohelpers import *
import cairo
import math

HALF_ERROR_BAR_WIDTH = 3.0

def draw_error_bar(ctx, x, y, error):
    error_top = y + error
    error_bottom = y - error

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
        # XXX y_error only makes sense if plot.axis[Y] is a NumberAxis
        y = max(t[Y] + (t[YERR] or 0) for t in self.data)
        return (x, y)

    def transformed_data(self, plot):
        for xs, y, y_error in self.data:
            x1, x2 = xs
            # XXX y_error only makes sense if plot.axis[Y] is a NumberAxis
            yield plot.axis[X].as_number(x1), \
                  plot.axis[X].as_number(x2), \
                  plot.axis[Y].as_number(y), \
                  y_error
    
    def draw_data(self, plot):
        ctx = plot.context
        half_spacing, _zero = scaledsize(ctx, self.HALF_SPACING, 0)

        # XXX total hack.
        r, g, b, a = ctx.get_source().get_rgba()

        for i, d in enumerate(self.transformed_data(plot)):
            x1, x2, y2, y_error = d
            y1 = plot.bounds[Y1]

            ctx.set_source_rgba(r, g, b, a * (1.0 if i % 2 else 0.9))
            ctx.rectangle(x1 + half_spacing, y1, x2 - x1 - 2*half_spacing, y2-y1)
            ctx.fill()

    def draw_errors(self, plot):
        for x1, x2, y, y_error in self.transformed_data(plot):
            if y_error:
                draw_error_bar(plot.context, 0.5 * (x1 + x2), y, y_error)


class LineSeries(Series):

    def __init__(self, name, data, dots=True, curviness=0.0, nan_holes=True):
        Series.__init__(self, name)
        self.data = []
        for d in data:
            try:
                x, y, yerr = d
            except ValueError: # need more than 2 values to unpack
                x, y = d
                yerr = None

            # adding NaN values to self.data will create holes, so only add
            # them if that's what we went.
            if nan_holes or not math.isnan(y):
                self.data.append((x, y, yerr))

        self.curviness = curviness
        self.dots = dots

    # XXX kinda hacky
    def average_x_frequency(self, plot):
        spacings = 0
        nspacings = len(self.data) - 1
        for i in range(nspacings):
            spacings += (plot.axis[X].as_number(self.data[i+1][X]) \
                         - plot.axis[X].as_number(self.data[i][X]))
        return float(spacings) / nspacings

    def get_minimum_point(self):
        if not self.data: return None
        x = min(t[X] for t in self.data)
        y = min(t[Y] for t in self.data) # XXX if we take into account error here we'll go below 0 for graphs that probably shouldn't
        return (x, y)            

    def get_maximum_point(self):
        if not self.data: return None
        x = max(t[X] for t in self.data)
        y = max(t[Y] + (t[YERR] or 0) for t in self.data)
        return (x, y)

    def transformed_data(self, plot):
        for x, y, y_error in self.data:
            # XXX y_error only makes sense if plot.axis[Y] is a NumberAxis
            yield plot.axis[X].as_number(x), plot.axis[Y].as_number(y), y_error
    
    def draw_data(self, plot):
        ctx = plot.context
        dot_radius = 3 #theme.get_dot_size(self) # TODO fix this
        # TODO use bounds to clip out data

        position = [(t[X], t[Y]) for t in self.transformed_data(plot)]
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
        
    def draw_errors(self, plot):
        for x, y, y_error in self.transformed_data(plot):
            if y_error:
                draw_error_bar(plot.context, x, y, y_error)


class Threshold(Series):

    def __init__(self, id, type, name, value):
        #Series.__init__(self, str(value) + " - " + type + ": " + name) # wait until colour change and bolding for "Warning" etc.
        Series.__init__(self, '{0} - {1} [{2}]'.format(str(value), name, id))
        self.type = type
        self.value = value
    
    def get_minimum_point(self):
        return (None, self.value)

    def get_maximum_point(self):
        return (None, self.value)

    def draw(self, plot):
        ctx = plot.context
        ctx.new_path()
        y = plot.axis[Y].as_number(self.value)
        ctx.move_to(plot.bounds[X1], y)
        ctx.line_to(plot.bounds[X2], y)
        stroke(ctx)

    def draw_legend_icon(self, ctx):
        x1, y1, x2, y2 = ctx.clip_extents()
        roundedrect(ctx, x1 + 1, y1 + 1, x2 - x1 - 2, y2 - y1 - 2, (x2 - x1) * 0.3)
        stroke(ctx)

    def draw_legend_label(self, ctx):
        Series.draw_legend_label(self, ctx)
        # TODO same colour as icon for e.g. "Warning" and bold!

