==================================
Vizier: a python reporting library
==================================

Originally intended to be a fork of cairoplot to add new reporting functionality,
vizier has been completely re-written and re-imagined to provide a dead-easy
reporting and graphing alternative for python using cairo.

Notable features include::

* the creation and management of multi-page documents ("books"); and
* different types of plots (e.g. bar, line, scatter) on one graph

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

A multi-page PDF could be created as follows::

    #!/usr/bin/env python

    from vizier.book import PDFBook, SimplePage, GridPage, Inch, TextSpace, LEFT, BOTTOM
    from vizier.plot import BarGraph, Graph, BarPlot, LinePlot
    book = PDFBook(units=Inch)

    bar_graph = BarGraph([1, 2, 3, 4, 5, 6, 7])
    page = SimplePage(width=11, height=8.5, margin=0.5, spacing=0.5)
    page[0] = bar_graph
    book.append(page)
    
    complex_graph = ContinuousPlot(legend=True, x_grid=(0, 0.2), y_grid=(0, 0.5))
    complex_graph.add_series(

        # each tuple in the data is (x, y, y-error)
        LineSeries("Raw Observations", [(0, 0.03, 0.016), (1, 0.18, 0.034), (2, 0.176, 0.016)]),

        # each tuple in the data is (x[start, end], y, y-error)
        AreaSeries("Other Things", [((-0.5, 0.5), 1.03, 0.016), ((0.5, 1.5), 1.21, 0.034), ((1.5, 2.5), 1.386, 0.034)]),
        
        # show a threshold at y=4.25
        Threshold("Warning", "Imminent Catastrophic Destruction", 4.25)
    )
    
    vlayout = VerticalLayout(0.1, 0.6) # splits a space vertically into 3.
    vlayout[0] = TextSpace("This layout", halign=LEFT)
    vlayout[1] = TextSpace("is split up into 3")
    vlayout[2] = TextSpace("non-uniformly!", valign=BOTTOM)
    
    page = GridPage(2, 2, width=11, height=8.5)
    page[0, 0] = TextSpace("This happens to be a graph.") 
    page[0, 1] = complex_graph
    page[1, 0] = complex_graph
    page[1, 1] = vlayout
    book.append(page)
    
    fp = open("abc.pdf", 'wb')
    book.compile(fp)    
    fp.close()        

