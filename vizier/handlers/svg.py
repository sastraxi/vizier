
import cairo
from .vector import VectorHandler as _VectorHandler

class SVGHandler(_VectorHandler):
    """Handler to create plots that output to svg files."""

    def __init__(self, filename, width, height):
        """Creates a surface to be used by Cairo."""
        _VectorHandler.__init__(self, None, width, height)
        self.surface = cairo.SVGSurface(filename, width, height)

