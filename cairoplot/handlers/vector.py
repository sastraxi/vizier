
import cairo
from .fixedsize import FixedSizeHandler as _FixedSizeHandler

class VectorHandler(_FixedSizeHandler):
    """Handler to create plots that output to vector files."""

    def __init__(self, surface, *args, **kwargs):
        """Create Handler for arbitrary surfaces."""
        _FixedSizeHandler.__init__(self, *args, **kwargs)
        self.surface = surface

    def commit(self, plot):
        """Writes plot to file."""
        _FixedSizeHandler.commit(self, plot)
        self.surface.finish()

