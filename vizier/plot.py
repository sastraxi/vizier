#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import contextlib

from themes import SlickTheme
from helpers import *
from cairohelpers import *
import cairo
import math

from axes import *

from series import *

#BASE_THICKNESS = 1.0 / 400.0

class Drawable(object):

    def draw(self, ctx, width, height): 
        raise NotImplementedError

class Plot(Drawable):

    def __init__(self, title, subtitle, date, theme):
        self.theme = theme
        self.title = title
        self.subtitle = subtitle
        self.date = date
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

    def __init__(self, title=None, subtitle=None, date=None, identifier=None, legend=False, x_axis=None, y_axis=None, bounds=None, y_min=None, theme=SlickTheme()):
        Plot.__init__(self, title, subtitle, date, theme)
        self.identifier = identifier # XXX ward-specific needs to go
        self.legend = legend
        self.axis = [x_axis, y_axis]
        self.bounds = bounds
        self.y_min = y_min
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
            self.bounds = [self.axis[X].as_number(self.minimum_point[X]),
                           self.axis[Y].as_number(self.minimum_point[Y]),
                           self.axis[X].as_number(self.maximum_point[X]),
                           self.axis[Y].as_number(self.maximum_point[Y])]
            
            # if there is no spread on the Y-axis, put the points in the middle of the graph.
            # also captures the case where there are no points at all.
            if abs(self.bounds[Y2] - self.bounds[Y1]) < EPSILON:
                self.bounds[Y1] = self.bounds[Y1] - 0.5
                self.bounds[Y2] = self.bounds[Y2] + 0.5
            
            # if graph would almost hit y=0 (relative to its y-scale), make it hit y=0.
            if self.bounds[Y1] > 0 and self.bounds[Y1] / self.bounds[Y2] < 0.3:
                self.bounds[Y1] = 0
                
            # allow manual override of Y1:
            if self.y_min is not None:
                self.bounds[Y1] = self.y_min

            # XXX here be stupid, hacky dragons.
            # sane margins, github issue #3
            y_padding = (self.bounds[Y2] - self.bounds[Y1]) * 0.07
            self.bounds[Y2] += y_padding
            if abs(self.bounds[Y1]) >= EPSILON:
                self.bounds[Y1] -= y_padding
            # XXX why is zero special?

            # give extra X padding to line-only graphs, github issue #3
            all_lines = all(isinstance(s, LineSeries) for s in self._series)
            if all_lines:
                avg_spacing = sum(s.average_x_frequency(self) for s in self._series) / float(len(self._series))
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

        # draw the "identifier" XXX ward-specific needs to go
        if self.identifier:
            ctx.move_to(end[X], end[Y])
            self.theme.prepare_label()
            self.context.set_font_size(6.0)
            drawtext(ctx, self.identifier, halign=RIGHT, valign=BOTTOM)

        # draw the title and subtitle.
        if self.title:
            ctx.move_to(start[X], start[Y] + 12)
            self.theme.prepare_title()
            ctx.show_text(self.title)
            start[Y] += 12

        if self.subtitle:
            ctx.move_to(start[X], start[Y] + 14)
            self.theme.prepare_subtitle()
            ctx.show_text(self.subtitle)
        
        if self.date:
            ctx.move_to(end[X], start[Y] + 14)
            self.theme.prepare_subtitle()
            drawtext(ctx, self.date, halign=RIGHT, valign=BOTTOM)

        if self.date or self.subtitle:
            start[Y] += 12

        if self.title or self.subtitle or self.date: start[Y] += 10

        # draw the series legend.
        if self.legend:
            for i, series in enumerate(self._series):
                with subcontext(ctx, end[X] - 80, start[Y] + i * 20 + 3, 11, 11):
                    self.theme.prepare_series(i, series)
                    series.draw_legend_icon(ctx)
                ctx.move_to(end[X] - 64, start[Y] + i * 20 + 12)
                self.theme.prepare_label()
                series.draw_legend_label(ctx)
            end[X] -= 90

        # draw the threshold legend.
        for i, threshold in enumerate(self._thresholds):
            with subcontext(ctx, start[X], end[Y] - 14, 12, 12):
                self.theme.prepare_threshold(i, threshold)
                threshold.draw_legend_icon(ctx)
            
            ctx.move_to(start[X] + 16, end[Y] - 5)
            self.theme.prepare_label()
            threshold.draw_legend_label(ctx)
            end[Y] -= 16
        else:
            if self.identifier and not (self.theme.axis_titles[X] and self.axis[X].title):
                end[Y] -= 8
        if self._thresholds: end[Y] -= 4

        # prepare for our grids and labels.
        if self.theme.axis_titles[X] and self.axis[X].title: end[Y] -= 20
        if self.theme.major_axis_labels[X] or \
           self.theme.minor_axis_labels[X]: end[Y] -= 10
        
        if self.theme.axis_titles[Y] and self.axis[Y].title: start[X] += 30
        if self.theme.major_axis_labels[Y] or \
           self.theme.minor_axis_labels[Y]: start[X] += 10 # XXX need to calc. with of these labels. 4 + max(measure(label)[X] for y, label in self.axis[X].markers())
           
        # TODO in the future, we'll add a rotated x-axis label scheme

        # draw labels.
        if self.theme.axis_titles[X] and self.axis[X].title:
            self.theme.prepare_subtitle()
            ctx.move_to(0.5 * (start[X] + end[X]), end[Y] + 12.0)
            drawtext(ctx, self.axis[X].title, CENTER, TOP)

        if self.theme.axis_titles[Y] and self.axis[Y].title:
            # FIXME: this has something you don't... a GREAT BIG BUSHY HACK
            self.theme.prepare_subtitle()
            ctx.move_to(start[X]-36, 0.5 * (start[Y] + end[Y]) - 30)
            drawtext(ctx, self.axis[Y].title, RIGHT, MIDDLE, rotation=-0.5 * math.pi)

        # draw graph elements.
        with self.dataspace(start, end):

            def line(x1, y1, x2, y2):
                ctx.move_to(x1, y1)
                ctx.line_to(x2, y2)
                stroke(ctx)

            xt, _zero = scaledsize(ctx, 4.0, 0)
            _zero, yt = scaledsize(ctx, 0, 4.0)

            with unclipped(ctx):

                # FIXME this is all kinda... erm, not good, but don't worry for now

                # X axis grid lines + labels.
                seen = []
                for marker in self.axis[X].markers(self.bounds[X1], self.bounds[X2]):
                    x, label = marker

                    # don't draw grid lines at the very edges.
                    if abs(x - self.bounds[X1]) > EPSILON and abs(x - self.bounds[X2]) > EPSILON:
                        self.theme.draw_marker_line(X, marker, x, self.bounds[Y1], x, self.bounds[Y2])
                
                    if not any(abs(x - v) < EPSILON for v in seen):
                        self.theme.draw_marker_label(X, marker, x, self.bounds[Y1])    
                    seen.append(x)                    
                       
                # Y axis grid lines + labels.
                seen = []
                for marker in self.axis[Y].markers(self.bounds[Y1], self.bounds[Y2]):
                    y, label = marker

                    # don't draw grid lines at the very edges.
                    if abs(y - self.bounds[Y1]) > EPSILON and abs(y - self.bounds[Y2]) > EPSILON:
                        self.theme.draw_marker_line(Y, marker, self.bounds[X1], y, self.bounds[X2], y)
                    
                    # don't draw the first Y axis label if the X axis has major labels.
                    #if abs(y - self.bounds[Y1]) > EPSILON or not self.theme.major_axis_labels[X]:
                    if not any(abs(y - v) < EPSILON for v in seen):
                        self.theme.draw_marker_label(Y, marker, self.bounds[X1], y)
                    seen.append(y)                    
            
            for i, threshold in enumerate(self._thresholds):
                self.theme.prepare_threshold(i, threshold)
                threshold.draw(self)

            for i, series in enumerate(self._series):
                self.theme.prepare_series(i, series)
                series.draw_data(self)
                self.theme.prepare_error(i, series)
                series.draw_errors(self)
            
        # draw the X axis line.
        self.theme.prepare_axis_line()
        ctx.move_to(start[X], end[Y])
        ctx.line_to(end[X], end[Y])
        ctx.stroke()

        # draw a QR code.
        '''
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