
class Handler(object):
    """Base class for all handlers."""

    def prepare(self, plot):
        pass

    def commit(self, plot):
        """All handlers need to finalize the cairo context."""
        plot.context.show_page()

