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
                                                                x_labels=False, y_labels=True,
                                                                x_title=None, y_title=None,
                                                                x_formatter=None, y_formatter=None,
                                                                bounds=None):
        Plot.__init__(self, title, subtitle)
        self.legend = legend
        self.grid = [x_grid, y_grid] # N.B. each arg is a 2-tuple (start, positive_step)
        self.labels = [x_labels, y_labels]
        self.axis_titles = [x_title, y_title]
        self.formatters = [x_formatter or (lambda v: str(v)),
                           y_formatter or (lambda v: str(v))]
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
            self.bounds = [self.minimum_point[X], self.minimum_point[Y],
                           self.maximum_point[X], self.maximum_point[Y]]
            
            # if graph would almost hit y=0 (relative to its y-scale), make it hit y=0.
            if self.bounds[Y1] > 0 and self.bounds[Y1] / self.bounds[Y2] < 0.3:
                self.bounds[Y1] = 0

            # XXX here be stupid, hacky dragons.
            # sane margins, github issue #3
            self.bounds[Y2] *= 1.07                 

            # give extra X padding to line-only graphs, github issue #3
            all_lines = all(isinstance(s, LineSeries) for s in self._series)
            if all_lines:
                avg_spacing = sum(s.average_x_frequency() for s in self._series) / float(len(self._series))
                self.bounds[X1] -= 0.5 * avg_spacing 
                self.bounds[X2] += 0.5 * avg_spacing
    
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

        yield 

        self.context.restore()

    def generate_x_stops(self, width):

        # if we have any area series:
        # take the most-frequent one that won't crowd the x axis and display labels at the midpoints.
        # if we don't, take 

        if self.grid[X]:
            start, step = self.grid[X]
        else:
            # TODO figure out how much space we have, etc. etc.
            return []

        stops = []
        for x in frange(start, self.bounds[X2] + EPSILON, step):
            stops.append(x)        
        return stops

    def generate_y_stops(self, height):

        if self.grid[Y]:
            start, step = self.grid[Y]
        else:
            # TODO figure out how much space we have, etc. etc.
            return [], 0

        stops = []
        for y in frange(start + step, self.bounds[Y2], step): # start + step because we don't want a grid line or label for the bottom of the graph
            stops.append(y)
        
        # TODO send out the largest y-label size (use the formatter)
        return stops, 0

    def render(self):
        self.theme.context = self.context
        ctx = self.context        

        # TODO push measuring responsibilities over to Theme
        # TODO text lists (e.g. legend, labels) need to be able to calculate their extents
        # TODO investigate whether we could use Spaces as a layout mechanism here.
        # TODO messy magic numbers all about.

        # bounding box of the graph.
        # this will get modified as we go through the function.
        PADDING = 0.0
        start = [PADDING, PADDING]
        end = [self.width - PADDING, self.height - PADDING]

        # draw the title and subtitle.
        if self.title:
            ctx.move_to(start[X], start[Y] + 12)
            self.theme.prepare_title()
            ctx.show_text(self.title)
            start[Y] += 12

        if self.subtitle:
            ctx.move_to(start[X], start[Y] + 12)
            self.theme.prepare_subtitle()
            ctx.show_text(self.subtitle)
            start[Y] += 12

        if self.title or self.subtitle: start[Y] += 10

        # draw the series legend.
        if self.legend:
            for i, series in enumerate(self._series):
                with subcontext(ctx, end[X] - 80, start[Y] + i * 20 + 3, 11, 11):
                    self.theme.prepare_series(i, series)
                    series.draw_legend_icon(ctx)
                ctx.move_to(end[X] - 64, start[Y] + i * 20 + 12)
                series.draw_legend_label(ctx)
            end[X] -= 90

        # draw the threshold legend.
        for i, threshold in enumerate(self._thresholds):
            with subcontext(ctx, start[X], end[Y] - 14, 12, 12):
                self.theme.prepare_threshold(i, threshold)
                threshold.draw_legend_icon(ctx)
            ctx.move_to(start[X] + 16, end[Y] - 5)
            threshold.draw_legend_label(ctx)
            end[Y] -= 16
        if self._thresholds: end[Y] -= 4

        # prepare our grids and labels.
        x_stops, y_stops = [], []

        if self.axis_titles[X]: end[Y] -= 20
        if self.labels[X]: end[Y] -= 10
        
        if self.axis_titles[Y]: start[X] += 16
        if self.labels[Y] or self.grid[Y]:
            y_stops, width = self.generate_y_stops(end[Y] - start[Y])
            start[X] += width + 4

        if self.labels[X]:
            x_stops = self.generate_x_stops(end[X] - start[X])            
            # TODO in the future, we'll add a rotated x-axis label scheme which would influence end[Y]            
        
        # draw labels.
        if self.axis_titles[X]:
            self.theme.prepare_subtitle()
            ctx.move_to(0.5 * (start[X] + end[X]), end[Y] + 12.0)
            drawtext(ctx, self.axis_titles[X], CENTER, TOP)

        if self.axis_titles[Y]:
            # FIXME: this has something you don't... a GREAT BIG BUSHY HACK
            with unclipped(ctx):
                self.theme.prepare_subtitle()
                ctx.move_to(start[X] - 20.0, 0.5 * (start[Y] + end[Y]))
                drawtext(ctx, self.axis_titles[Y], RIGHT, MIDDLE, rotation=-0.5 * math.pi, hadjust=28, vadjust=-14)

        # draw graph elements.
        with self.dataspace(start, end):
            
            for y in y_stops:
                
                # draw grid line.
                self.theme.prepare_grid()                
                if self.grid[Y]:
                    ctx.move_to(self.bounds[X1], y)
                    ctx.line_to(self.bounds[X2], y)
                    stroke(ctx, 0.5)
                    
                # draw the label.
                self.theme.prepare_label()
                if self.labels[Y]:
                    ctx.move_to(self.bounds[X1], y)
                    with unclipped(ctx):
                        drawtext(ctx, self.formatters[Y](y), RIGHT, MIDDLE, hadjust=-4.0)
                        
            for x in x_stops:
            
                # draw grid line.
                self.theme.prepare_grid()     
                if self.grid[X]:
                    # don't draw edge grid lines for the X axis
                    if (x - EPSILON) > self.bounds[X1] and (x + EPSILON) < self.bounds[X2]:
                        ctx.move_to(x, self.bounds[Y1])
                        ctx.line_to(x, self.bounds[Y2])
                        stroke(ctx, 0.5)
                    
                # draw the label.
                self.theme.prepare_label()
                if self.labels[X]:
                    ctx.move_to(x, self.bounds[Y1])
                    with unclipped(ctx):
                        drawtext(ctx, self.formatters[X](x), CENTER, TOP, vadjust=4.0)
            

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

        # draw a QR code.
        '''
        import datetime
        import urllib, urllib2        
        text = "goo.gl/tw1d90y"
        url = "http://chart.apis.google.com/chart?cht=qr&chs=300x300&chl=" + urllib.quote(text) + "&chld=H|0"
        fobj = urllib2.urlopen(url)
        surface = cairo.ImageSurface.create_from_png(fobj)        
        dest_x = self.width - 25
        dest_y = 0
        ctx.rectangle(dest_x, dest_y, 25, 25)
        ctx.save()
        ctx.scale(25 / 300.0, 25 / 300.0)
        ctx.set_source_surface(surface, dest_x * (300 / 25.0), dest_y * (300 / 25.0))
        ctx.fill()
        ctx.restore()            
        '''
