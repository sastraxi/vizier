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

    HALF_SPACING = 0.5

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
        for xs, y2, y_error in self.data:
            x1, x2 = xs
            y1 = 0

            half_spacing, _zero = scaledsize(ctx, self.HALF_SPACING, 0)

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
        '''
        min_pt = (min(p[X] for p in position), min(p[Y] for p in position))
        max_pt = (max(p[X] for p in position), max(p[Y] for p in position))
        clamp = lambda a, low, high: low if a < low else (high if a > high else a)                    
        constrain = lambda x, y: (clamp(x, min_pt[0], max_pt[0]), clamp(y, min_pt[1], max_pt[1]))
        '''
        def velocity(i):
            if i == 0 or i == len(position) - 1: return (0, 0)
            x, y = (position[i+1][0] - position[i-1][0], position[i+1][1] - position[i-1][1])
            x, y = 0.5 * x, 0.5 * y
            '''
            if x == 0 and y == 0: return (x, y)
            
            # constrain in both directions
            def line_hit_ratio(dir):
                dx, dy = dir * x, dir * y
                cx, cy = position[i][0] + dx, position[i][1] + dy
                ccx, ccy = constrain(cx, cy)
                rx, ry = 1.0 - ((ccx - cx) / x), 1.0 - ((ccy - cy) / y) # negatives will cancel out here, dx,dy will be positive
                return min(rx, ry)

            ratios = [line_hit_ratio(1), line_hit_ratio(-1)]
            r = min(ratios) ** 0.3 # XXX mixing factor is really silly, but hey, the graphs look good niow!
            x, y = x * r, y * r
            '''
            return (x, y)

        ctx.move_to(*position[0])

        for i in range(1, len(position)):
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
                dot(ctx, p[X], p[Y], dot_radius)
        
    def draw_errors(self, ctx, transform):
        for x, y, y_error in self.data:
            if y_error:
                draw_error_bar(ctx, x, y, y_error)


class Threshold(Series):

    def __init__(self, type, name, value):
        Series.__init__(self, type + ":" + name)
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

