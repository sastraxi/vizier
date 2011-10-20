#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import contextlib

from helpers import *
from cairohelpers import *
import cairo
import math

from themes import GoogleVisTheme
from series import *

#BASE_THICKNESS = 1.0 / 400.0

class Drawable(object):

    def draw(self, ctx, width, height): 
        raise NotImplementedError

class Plot(Drawable):

    def __init__(self, title, subtitle):
        self.theme = GoogleVisTheme()
        self.title = title
        self.subtitle = subtitle
        self.context = None

    def draw(self, context, width, height):
        self.context = context
        self.width = width 
        self.height = height 
        self.context.set_line_join(cairo.LINE_JOIN_ROUND)
        self.render()

    def render(self):
        """ render() is called by draw(). Do not override draw, as you'd have to remember
            to call the base class. Instead, put your drawing code in render(). """
        raise NotImplementedError


class ContinuousPlot(Plot):
    """ Plots for which the X/Y axes form a continuous plane.
        Takes AreaSeries, LineSeries, and Threshold series objects. """

    def __init__(self, title=None, subtitle=None, legend=False, x_grid=False, y_grid=False,
                                                                x_labels=True, y_labels=True,
                                                                x_title=None, y_title=None,
                                                                bounds=None):
        Plot.__init__(self, title, subtitle)
        self.legend = legend
        self.grid = [x_grid, y_grid]
        self.labels = [x_labels, y_labels]
        self.axis_titles = [x_title, y_title]
        self.bounds = bounds
        self._autobounds = bounds is None
        self._series = []
        self._thresholds = []

    def add(self, *series):
        for s in series:
            if isinstance(s, Threshold):
                self._thresholds.append(s)
            else:
                self._series.append(s)
        self._calculate_bounds()

    def _calculate_bounds(self):
        self.minimum_point = None
        self.maximum_point = None
        for el in self._series + self._thresholds:           
            minpt, maxpt = el.get_minimum_point(), el.get_maximum_point()
            
            if not self.minimum_point:
                self.minimum_point = minpt
            else:
                # allow minpt[X/Y] to be None: allows infinite lines in series (e.g. Thresholds)
                if minpt[X] is not None: self.minimum_point = (min(self.minimum_point[X], minpt[X]), self.minimum_point[Y])
                if minpt[Y] is not None: self.minimum_point = (self.minimum_point[X], min(self.minimum_point[Y], minpt[Y]))

            if not self.maximum_point:
                self.maximum_point = maxpt
            else:
                # allow maxpt[X/Y] to be None: allows infinite lines in series (e.g. Thresholds)
                if maxpt[X] is not None: self.maximum_point = (max(self.maximum_point[X], maxpt[X]), self.maximum_point[Y])
                if maxpt[Y] is not None: self.maximum_point = (self.maximum_point[X], max(self.maximum_point[Y], maxpt[Y]))

        if self._autobounds:
            self.bounds = (self.minimum_point[X], self.minimum_point[Y],
                           self.maximum_point[X], self.maximum_point[Y])
    
    @contextlib.contextmanager
    def dataspace(self, start, end):

        self.context.save()

        self.context.new_path()
        self.context.rectangle(start[X], start[Y], end[X] - start[X], end[Y] - start[Y])
        self.context.clip()

        width = self.bounds[X2] - self.bounds[X1]
        height = self.bounds[Y2] - self.bounds[Y1]

        # graph position and series scale.
        self.context.translate(start[X], end[Y])
        self.context.scale(1.0, -1.0)
        self.context.scale((end[X] - start[X]) / width,
                           (end[Y] - start[Y]) / height)
        self.context.translate(-self.bounds[X1], -self.bounds[Y1])

        #self.context.move_to(self.bounds[X1], self.bounds[Y1])
        #self.context.line_to(self.bounds[X1] + width, self.bounds[Y1] + height)
        #stroke(self.context, 2)

        yield 

        self.context.restore()

    def render(self):
        self.theme.context = self.context
        ctx = self.context        

        # TODO push measuring responsibilities over to Theme
        # TODO text lists (e.g. legend, labels) need to be able to calculate their extents
        # TODO investigate whether we could use Spaces as a layout mechanism here.

        # bounding box of the graph.
        # this will get modified as we go through the function.
        PADDING = 10.0
        start = [PADDING, PADDING]
        end = [self.width - PADDING, self.height - PADDING]

        # draw the title and subtitle.
        if self.title or self.subtitle: start[Y] += 4
        
        if self.title:
            ctx.move_to(start[X], start[Y])
            self.theme.prepare_title()
            ctx.show_text(self.title)
            start[Y] += 12

        if self.subtitle:
            ctx.move_to(start[X], start[Y])
            self.theme.prepare_subtitle()
            ctx.show_text(self.subtitle)
            start[Y] += 12            

        # draw the series legend.
        if self.legend:
            for i, series in enumerate(self._series):
                with subcontext(ctx, end[X] - 80, start[Y] + i * 20 + 2, 12, 12):
                    self.theme.prepare_series(i, series)
                    series.draw_legend_icon(ctx)
                with subcontext(ctx, end[X] - 80, start[Y] + i * 20, end[X], 16):
                    series.draw_legend_label(ctx)
            end[X] -= 80

        # draw the threshold legend.
        for threshold in self._thresholds:
            with subcontext(ctx, start[X], end[Y] - 14, 12, 12):
                self.theme.prepare_threshold(i, threshold)
                threshold.draw_legend_icon(ctx)
            ctx.move_to(start[X] + 16, end[Y] - 4)
            threshold.draw_legend_label(ctx)
            end[Y] -= 20

        # draw the Y axis title and labels.
        # TODO`

        # draw the X axis title and labels.
        # TODO

        # draw graph elements.
        with self.dataspace(start, end):
            
            self.theme.prepare_grid()
            if self.grid[Y]:
                y_start, y_step = self.grid[Y]
                assert(y_step > 0)
                for y in frange(y_start, self.bounds[Y2], y_step):
                    # don't draw right on/below the axis.
                    if (y + EPSILON) > self.bounds[Y1]:
                        ctx.move_to(self.bounds[X1], y)
                        ctx.line_to(self.bounds[X2], y)
                        stroke(ctx, 0.5)
                        # TODO also draw label
                        
            # TODO X grid

            for i, threshold in enumerate(self._thresholds):
                self.theme.prepare_threshold(i, threshold)
                threshold.draw(ctx, self.bounds)

            for i, series in enumerate(self._series):
                self.theme.prepare_series(i, series)
                series.draw_data(ctx, self.bounds)
                self.theme.prepare_error(i, series)
                series.draw_errors(ctx, self.bounds)
            
        # draw the X axis line.
        self.theme.prepare_axis_line()
        ctx.move_to(start[X], end[Y])
        ctx.line_to(end[X], end[Y])
        ctx.stroke()
