=========================================
Vizier: a fork of Cairoplot for reporting
=========================================

A fork of cairoplot to add new reporting functionality, including but not
limited to

* the creation and management of multi-page documents ("books"); and
* different types of plots (e.g. bar, line, scatter) on one graph

Vizier is dedicated to the fine work of the contributors and maintainers of
that project, who sadly have not had time to continue their work. See the
original CairoPlot on `Launchpad <https://launchpad.net/cairoplot>`_ for
more information about that project.

Note: requires libcairo >= 1.10.1, to fix a bug with multi-page PDF clipping.
https://bugs.freedesktop.org/show_bug.cgi?id=24691

Quick Example
=============

Vizier is used much like cairoplot; a multi-page PDF could be created as
follows::

    #!/usr/bin/env python

    from vizier.book import PDFBook, SimplePage, GridPage, Inch, TextSpace, LEFT, BOTTOM
    from vizier.plot import BarGraph, Graph, BarPlot, LinePlot
    book = PDFBook(units=Inch)

    bar_graph = BarGraph([1, 2, 3, 4, 5, 6, 7])
    page = SimplePage(width=11, height=8.5, margin=0.5, spacing=0.5)
    page[0] = bar_graph
    book.append(page)
    
    complex_graph = Graph()
    complex_graph.add_plot(LinePlot([10, 9, 10, 9, 8, 10, 7, 6]))
    complex_graph.add_plot(BarPlot([7, 6, 5, 4, 3, 2, 1, 0]))
    complex_graph.add_y_threshold(9.5, "Above here is trouble")
    
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

