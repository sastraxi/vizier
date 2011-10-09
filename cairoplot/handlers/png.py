
import cairo

from .fixedsize import FixedSizeHandler as _FixedSizeHandler

class PNGHandler(_FixedSizeHandler):
    """Handler to create plots that output to png files."""

    def __init__(self, filename, width, height):
        """Creates a surface to be used by Cairo."""
        _FixedSizeHandler.__init__(self, width, height)
        self.filename = filename
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

    def commit(self, plot):
        """Writes plot to file."""
        _FixedSizeHandler.commit(self, plot)
        self.surface.write_to_png(self.filename)

