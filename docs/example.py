import cairoplot, cairoplot.handlers    

pdf = cairoplot.handlers.PDFHandler("example.pdf", 850, 1100)

plot1 = cairoplot.VerticalBarPlot(pdf, [5, 0, 4, 1, 3, 2, 2.5, 6])
plot1.render()
plot1.commit()

plot2 = cairoplot.DotLinePlot(pdf, [1, 2, 3, 4, 5, 6, 7, 8, 2.5, 5], grid=True)
plot2.render()

plot2.commit()

