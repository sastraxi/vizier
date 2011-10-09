
import cairo
import cairoplot
from .handler import Handler as _Handler

class FixedSizeHandler(_Handler):
    """Base class for handlers with a fixed size."""

    def __init__(self, width, height):
        """Create with fixed width and height."""
        self.dimensions = {}
        self.dimensions[cairoplot.HORZ] = width
        self.dimensions[cairoplot.VERT] = height

        # sub-classes must create a surface
        self.surface = None

    def prepare(self, plot):
        """Prepare plot to render by setting its dimensions."""
        _Handler.prepare(self, plot)
        plot.dimensions = self.dimensions
        plot.context = cairo.Context(self.surface)

    def commit(self, plot):
        """Commit the plot (to a file)."""
        _Handler.commit(self, plot)

        # since pngs are different from other fixed size handlers,
        # sub-classes are in charge of actual file writing

