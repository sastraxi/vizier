import cairo
from series import *
from helpers import enum
from cairohelpers import *
from axes import MajorMarker, MinorMarker, MarkerType

class Theme(object):

    def __init__(self):
        self.context = None

    def prepare_title(self):
        pass
    def prepare_subtitle(self):
        pass
    def prepare_series(self, index, series):        
        raise NotImplementedError


class SlickTheme(Theme):

    THRESHOLD_COLOURS = [(1.0, 0.75, 0.2, 1.0), (1.0, 0.4, 0.15, 1.0), (1.0, 0.0, 0.0, 1.0)]
    SERIES_COLOURS = [(0.5, 0.5, 1.0, 1.0), (0.5, 0.75, 1.0, 1.0), (0.5, 1.0, 0.5, 1.0)]
    FONT_FAMILY = "Century Gothic"

    TICK_SIZE = 4.0

    def __init__(self):
        Theme.__init__(self)
        self.major_axis_labels=[True, True]
        self.minor_axis_labels=[False, False]
        self.major_axis_style=[None, MarkerType.LINES]
        self.minor_axis_style=[MarkerType.OUTER_TICKS, MarkerType.INNER_TICKS]
        self.axis_titles=[True, True]

    def prepare_title(self):
        if not self.context: raise Exception("No context attached")
        self.context.set_source_rgba(0, 0, 0, 1.0)
        self.context.select_font_face(self.FONT_FAMILY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)        
        self.context.set_font_size(14.0)

    def prepare_subtitle(self):
        if not self.context: raise Exception("No context attached")
        self.context.set_source_rgba(0, 0, 0, 0.8)
        self.context.select_font_face(self.FONT_FAMILY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(10.0)     

    def prepare_series(self, index, series):        
        if not self.context: raise Exception("No context attached")
        colour = self.SERIES_COLOURS[index % len(self.SERIES_COLOURS)]
        self.context.set_source_rgba(*colour)
        self.context.set_line_width(1.6)
        self.context.set_dash([])

    def prepare_threshold(self, index, threshold):
        if not self.context: raise Exception("No context attached")
        colour = self.THRESHOLD_COLOURS[index % len(self.THRESHOLD_COLOURS)]
        self.context.set_source_rgba(*colour)
        self.context.set_line_cap(cairo.LINE_CAP_ROUND)
        self.context.set_dash([1.0, 2.0])
        self.context.set_line_width(0.8)
        # TODO dash stuff here      
    
    def prepare_error(self, index, series):
        if not self.context: raise Exception("No context attached")
        self.context.set_source_rgba(1.0, 0.0, 0.0, 0.8)
        self.context.set_line_width(1.0)     

    def prepare_axis_line(self):
        if not self.context: raise Exception("No context attached")
        self.context.set_line_width(1.0)
        self.context.set_source_rgba(0.0, 0.0, 0.0, 1.0)

    def draw_marker_line(self, axis, marker, x1, y1, x2, y2):
        if not self.context: raise Exception("No context attached")
        self.context.set_line_width(0.4)
        if isinstance(marker, MajorMarker):
            self.context.set_source_rgba(0.0, 0.0, 0.0, 0.2)
            style = self.major_axis_style[axis]
        else:
            self.context.set_source_rgba(0.0, 0.0, 0.0, 0.1)
            style = self.minor_axis_style[axis]

        def line(x1, y1, x2, y2):
            self.context.move_to(x1, y1)
            self.context.line_to(x2, y2)
            stroke(self.context)

        xt, yt = scaledsize(self.context, self.TICK_SIZE, self.TICK_SIZE)

        if style == MarkerType.LINES:
            line(x1, y1, x2, y2)
        elif style == MarkerType.INNER_TICKS:
            self.context.set_source_rgba(0.0, 0.0, 0.0, 0.3)
            if axis == X:
                line(x1, y1, x2, y1 + yt)
            else:
                line(x1, y1, x1 + xt, y2)

        elif style == MarkerType.OUTER_TICKS:
            self.context.set_source_rgba(0.0, 0.0, 0.0, 0.5)
            if axis == X:
                line(x1, y1, x2, y1 - yt)
            else:
                line(x1, y1, x1 - xt, y2)

    def draw_marker_label(self, axis, marker, x, y):
        if not self.context: raise Exception("No context attached")
        self.context.select_font_face(self.FONT_FAMILY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.context.set_source_rgba(0, 0, 0, 0.5)

        if isinstance(marker, MajorMarker):
            self.context.set_font_size(8.0)
            if not self.major_axis_labels[axis]: return
        else:
            self.context.set_font_size(6.0)
            if not self.minor_axis_labels[axis]: return

        self.context.move_to(x, y)
        if axis == X:
            drawtext(self.context, marker.label, CENTER, TOP, vadjust=4.0)     
        else:
            drawtext(self.context, marker.label, RIGHT, MIDDLE, hadjust=-4.0)              


    def prepare_label(self):
        self.context.select_font_face(self.FONT_FAMILY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.context.set_source_rgba(0, 0, 0, 0.5)
        self.context.set_font_size(8.0)
