import cairo
from series import *

class Theme(object):

    def __init__(self):
        self.context = None

    def prepare_title(self):
        pass
    def prepare_subtitle(self):
        pass
    def prepare_series(self, index, series):        
        raise NotImplementedError



class GoogleVisTheme(Theme):

    THRESHOLD_COLOURS = [(1.0, 0.75, 0.2, 1.0), (1.0, 0.4, 0.15, 1.0), (1.0, 0.0, 0.0, 1.0)]
    SERIES_COLOURS = [(0.5, 0.5, 1.0, 1.0), (0.5, 0.75, 1.0, 1.0), (0.5, 1.0, 0.5, 1.0)]
    FONT_FAMILY = "Century Gothic"

    def __init__(self):     
        Theme.__init__(self)

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
        self.context.set_dash([3.0, 5.0])
        self.context.set_line_width(0.8)
        # TODO dash stuff here      
    
    def prepare_error(self, index, series):
        if not self.context: raise Exception("No context attached")
        self.context.set_source_rgba(1.0, 0.0, 0.0, 0.8)
        self.context.set_line_width(1.0)     

    def prepare_grid(self):
        if not self.context: raise Exception("No context attached")
        self.context.set_line_width(1.0)
        self.context.set_source_rgba(0.0, 0.0, 0.0, 0.2)        

    def prepare_axis_line(self):
        if not self.context: raise Exception("No context attached")
        self.context.set_line_width(1.0)
        self.context.set_source_rgba(0.0, 0.0, 0.0, 1.0)

    def prepare_label(self):
        if not self.context: raise Exception("No context attached")
        self.context.select_font_face(self.FONT_FAMILY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(8.0)     
        self.context.set_source_rgba(0, 0, 0, 0.5)
