
import cairo
from .vector import VectorHandler as _VectorHandler

class PSHandler(_VectorHandler):
    """Handler to create plots that output to PostScript files."""

    def __init__(self, filename, width, height):
        """Creates a surface to be used by Cairo."""
        _VectorHandler.__init__(self, None, width, height)
        self.surface = cairo.PSSurface(filename, width, height)

