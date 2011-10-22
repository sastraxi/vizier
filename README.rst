==================================
Vizier: a python reporting library
==================================

Originally intended to be a fork of cairoplot to add new reporting functionality,
vizier has been completely re-written and re-imagined to provide a dead-easy
reporting and graphing alternative for python using cairo.

Notable features include::

    - bezier line interpolation,

    - handling NaN values,

    - threshold indicators,

    - the creation and management of multi-page documents ("books"), and

    - different types of plots (e.g. rectangle, line, scatter) on one graph

Vizier was inspired by the fine work of the contributors and maintainers of
the CairoPlot project, who sadly have not had time to continue their work. See
`CairoPlot's project page on Launchpad <https://launchpad.net/cairoplot>`_.

Note: libcairo >= 1.10.1 recommended, to fix a bug with multi-page PDF clipping.
https://bugs.freedesktop.org/show_bug.cgi?id=24691

Installing on Windows
=====================

Grab a recent version of GTK+, which includes Cairo. You can download an installer here:
http://sourceforge.net/projects/gtk-win/files/GTK%2B%20Runtime%20Environment/GTK%2B%202.22/

Now, get vizier. In the root vizier directory, run::

    python setup.py install

You should now be able to run one of the examples. Try::

    python examples/test1.py

If abc.pdf is created and looks relatively sane, you're ready to go.

Quick Example
=============

See examples/test1.py for code that creates a multi-page PDF.
