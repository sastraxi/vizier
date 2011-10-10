import cairo, math, sys

import vizier
from vizier.series import Series

# non-random data for needs of visual comparison of changes
if '--non-random' in sys.argv:
    random = lambda : 1.0
    print 'Plotting nonrandom data'
else:
    import random
    random = random.random

# Line plotting
test_scatter_plot = 1
test_dot_line_plot = 1
test_function_plot = 1
# Bar plotting
test_vertical_bar_plot = 1
test_horizontal_bar_plot = 1
# Pie plotting
test_pie_plot = 1
test_donut_plot = 1
# Others
test_gantt_chart = 1
test_themes = 1


if test_scatter_plot:
    #Default data
    data = Series([ (-2,10), (0,0), (0,15), (1,5), (2,0), (3,-10), (3,5) ])
    vizier.scatter_plot ( 'scatter_1_default_series.png', data = data, width = 500, height = 500, border = 20, axis = True, grid = True )
    
    #lists of coordinates x,y
    data = Series([[[1,2,3,4,5],[1,1,1,1,1]]])
    vizier.scatter_plot ( 'scatter_2_lists_series.png', data = data, width = 500, height = 500, border = 20, axis = True, grid = True )
    
    #lists of coordinates x,y,z
    data = Series([[[0.5,1,2,3,4,5],[0.5,1,1,1,1,1],[10,6,10,20,10,6]]])
    colors = [ (0,0,0,0.25), (1,0,0,0.75) ]
    vizier.scatter_plot ( 'scatter_3_lists_series.png', data = data, width = 500, height = 500, border = 20, axis = True, discrete = True,
                             grid = True, circle_colors = colors )    
    
    data = Series([(-1, -16, 12), (-12, 17, 11), (-4, 6, 5), (4, -20, 12), (13, -3, 21), (7, 14, 20), (-11, -2, 18), (19, 7, 18), (-10, -19, 15),
                  (-17, -2, 6), (-9, 4, 10), (14, 11, 16), (13, -11, 18), (20, 20, 16), (7, -8, 15), (-16, 17, 16), (16, 9, 9), (-3, -13, 25),
                  (-20, -6, 17), (-10, -10, 12), (-7, 17, 25), (10, -10, 13), (10, 13, 20), (17, 6, 15), (18, -11, 14), (18, -12, 11), (-9, 11, 14),
                  (17, -15, 25), (-2, -8, 5), (5, 20, 20), (18, 20, 23), (-20, -16, 17), (-19, -2, 9), (-11, 19, 18), (17, 16, 12), (-5, -20, 15),
                  (-20, -13, 10), (-3, 5, 20), (-1, 13, 17), (-11, -9, 11)])
    colors = [ (0,0,0,0.25), (1,0,0,0.75) ]
    vizier.scatter_plot ( 'scatter_2_variable_radius_series.png', data = data, width = 500, height = 500, border = 20, 
                             axis = True, discrete = True, dots = 2, grid = True, 
                             x_title = "x axis", y_title = "y axis", circle_colors = colors )
    
    #Scatter x DotLine error bars
    t = [x*0.1 for x in range(0,40)]
    f = [math.exp(x) for x in t]
    g = [10*math.cos(x) for x in t]
    h = [10*math.sin(x) for x in t]
    erx = [0.1*random() for x in t]
    ery = [5*random() for x in t]
    data = Series({"exp" : [t,f], "cos" : [t,g], "sin" : [t,h]})
    series_colors = [ (1,0,0), (0,0,0), (0,0,1) ]
    vizier.scatter_plot ( 'cross_r_exponential_series.png', data = data, errorx = [erx,erx], errory = [ery,ery], width = 800, height = 600, border = 20, 
                             axis = True, discrete = False, dots = 5, grid = True, 
                             x_title = "t", y_title = "f(t) g(t)", series_legend=True, series_colors = series_colors )


if test_dot_line_plot:
    #Default plot
    data = [ 0, 1, 3.5, 8.5, 9, 0, 10, 10, 2, 1 ]
    vizier.dot_line_plot( "dot_line_1_default_series.png", data, 400, 300, border = 50, axis = True, grid = True,
                             x_title = "x axis", y_title = "y axis" )

    #Labels
    data = { "john" : [-5, -2, 0, 1, 3], "mary" : [0, 0, 3, 5, 2], "philip" : [-2, -3, -4, 2, 1] }
    x_labels = [ "jan/2008", "feb/2008", "mar/2008", "apr/2008", "may/2008" ]
    y_labels = [ "very low", "low", "medium", "high", "very high" ]
    vizier.dot_line_plot( "dot_line_2_dictionary_labels_series.png", data, 400, 300, x_labels = x_labels, 
                             y_labels = y_labels, axis = True, grid = True,
                             x_title = "x axis", y_title = "y axis", series_legend=True )
    
    #Series legend
    data = { "john" : [10, 10, 10, 10, 30], "mary" : [0, 0, 3, 5, 15], "philip" : [13, 32, 11, 25, 2] }
    x_labels = [ "jan/2008", "feb/2008", "mar/2008", "apr/2008", "may/2008" ]
    vizier.dot_line_plot( 'dot_line_3_series_legend_series.png', data, 400, 300, x_labels = x_labels, 
                             axis = True, grid = True, series_legend = True )

    #Speed test, many x_labels
    data = range(1000)
    x_labels = [str(x) for x in data]
    vizier.dot_line_plot( 'dot_line_4_many_x_labels.png', data, 14000, 300, x_labels = x_labels, 
                             axis = True, grid = True, series_legend = True )

if test_function_plot :
    #Default Plot
    data = lambda x : x**2
    vizier.function_plot( 'function_1_default_series.png', data, 400, 300, grid = True, x_bounds=(-10,10), step = 0.1 )
    
    #Discrete Plot
    data = lambda x : math.sin(0.1*x)*math.cos(x)
    vizier.function_plot( 'function_2_discrete_series.png', data, 800, 300, discrete = True, dots = True, grid = True, x_bounds=(0,80), 
                             x_title = "t (s)", y_title = "sin(0.1*x)*cos(x)")

    #Labels test
    data = lambda x : [1,2,3,4,5][x]
    x_labels = [ "4", "3", "2", "1", "0" ]
    vizier.function_plot( 'function_3_labels_series.png', data, 400, 300, discrete = True, dots = True, grid = True, x_labels = x_labels, x_bounds=(0,4), step = 1 )
    
    #Multiple functions
    data = [ lambda x : 1, lambda y : y**2, lambda z : -z**2 ]
    colors = [ (1.0, 0.0, 0.0 ), ( 0.0, 1.0, 0.0 ), ( 0.0, 0.0, 1.0 ) ]
    vizier.function_plot( 'function_4_multi_functions_series.png', data, 400, 300, grid = True, series_colors = colors, step = 0.1 )

    #Gaussian
    a = 1
    b = 0
    c = 1.5
    gaussian = lambda x : a*math.exp(-(x-b)*(x-b)/(2*c*c))
    vizier.function_plot( 'function_5_gaussian_series.png', data, 400, 300, grid = True, x_bounds = (-10,10), step = 0.1 )
    
    #Dict function plot
    data = Series()
    data.range = (-5,5)
    data.group_list = {'linear':lambda x : x*2, 'quadratic':lambda x:x**2, 'cubic':lambda x:(x**3)/2}
    vizier.function_plot( 'function_6_dict_serie.png', data, 400, 300, grid = True, x_bounds=(-5,5), step = 0.1 )


if test_vertical_bar_plot:
    #Passing a dictionary
    data = Series({ 'teste00' : [27], 'teste01' : [10], 'teste02' : [18], 'teste03' : [5], 'teste04' : [1], 'teste05' : [22] })
    vizier.vertical_bar_plot ( 'vbar_0_dictionary_series.png', data, 400, 300, border = 20, grid = True, rounded_corners = True )

    #Display values
    data = Series({ 'teste00' : [27], 'teste01' : [10], 'teste02' : [18], 'teste03' : [5], 'teste04' : [1], 'teste05' : [22] })
    vizier.vertical_bar_plot ( 'vbar_0_dictionary_series.png', data, 400, 300, border = 20, display_values = True, grid = True, rounded_corners = True )

    #Using default, rounded corners and 3D visualization
    data = Series([ [0, 3, 11], [8, 9, 21], [13, 10, 9], [2, 30, 8] ])
    colors = [ (1,0.2,0), (1,0.7,0), (1,1,0) ]
    series_labels = ["red", "orange", "yellow"]
    vizier.vertical_bar_plot ( 'vbar_1_default_series.png', data, 400, 300, border = 20, grid = True, rounded_corners = False, colors = "yellow_orange_red" )
    vizier.vertical_bar_plot ( 'vbar_2_rounded_series.png', data, 400, 300, border = 20, series_labels = series_labels, display_values = True, grid = True, rounded_corners = True, colors = colors )
    vizier.vertical_bar_plot ( 'vbar_3_3D_series.png', data, 400, 300, border = 20, series_labels = series_labels, grid = True, three_dimension = True, colors = colors )

    #Mixing groups and columns
    data = Series([ [1], [2], [3,4], [4], [5], [6], [7], [8], [9], [10] ])
    vizier.vertical_bar_plot ( 'vbar_4_group_series.png', data, 400, 300, border = 20, grid = True )

    #Using no labels, horizontal and vertical labels
    data = Series([[3,4], [4,8], [5,3], [9,1]])
    y_labels = [ "line1", "line2", "line3", "line4", "line5", "line6" ]
    x_labels = [ "group1", "group2", "group3", "group4" ]
    vizier.vertical_bar_plot ( 'vbar_5_no_labels_series.png', data, 600, 200, border = 20, grid = True )
    vizier.vertical_bar_plot ( 'vbar_6_x_labels_series.png', data, 600, 200, border = 20, grid = True, x_labels = x_labels )
    vizier.vertical_bar_plot ( 'vbar_7_y_labels_series.png', data, 600, 200, border = 20, grid = True, y_labels = y_labels )
    vizier.vertical_bar_plot ( 'vbar_8_hy_labels_series.png', data, 600, 200, border = 20, display_values = True, grid = True, x_labels = x_labels, y_labels = y_labels )
    
    #Large data set
    data = Series([[10*random()] for x in range(50)])
    x_labels = ["large label name oh my god it's big" for x in data]
    vizier.vertical_bar_plot ( 'vbar_9_large_series.png', data, 1000, 800, border = 20, grid = True, rounded_corners = True, x_labels = x_labels )
    
    #Stack vertical
    data = Series([ [6, 4, 10], [8, 9, 3], [1, 10, 9], [2, 7, 11] ])
    colors = [ (1,0.2,0), (1,0.7,0), (1,1,0) ]
    x_labels = ["teste1", "teste2", "testegrande3", "testegrande4"]
    vizier.vertical_bar_plot ( 'vbar_10_stack_series.png', data, 400, 300, border = 20, display_values = True, grid = True, rounded_corners = True, stack = True, 
                                  x_labels = x_labels, colors = colors )


if test_horizontal_bar_plot:
    #Passing a dictionary
    data = Series({ 'teste00' : [27], 'teste01' : [10], 'teste02' : [18], 'teste03' : [5], 'teste04' : [1], 'teste05' : [22] })
    vizier.horizontal_bar_plot ( 'hbar_0_dictionary_series.png', data, 400, 300, border = 20, display_values = True, grid = True, rounded_corners = True )

    #Using default, rounded corners and 3D visualization
    data = Series([ [0, 3, 11], [8, 9, 21], [13, 10, 9], [2, 30, 8] ])
    colors = [ (1,0.2,0), (1,0.7,0), (1,1,0) ]
    series_labels = ["red", "orange", "yellow"]
    vizier.horizontal_bar_plot ( 'hbar_1_default_series.png', data, 400, 300, border = 20, grid = True, rounded_corners = False, colors = "yellow_orange_red" )
    vizier.horizontal_bar_plot ( 'hbar_2_rounded_series.png', data, 400, 300, border = 20, series_labels = series_labels, display_values = True, grid = True, rounded_corners = True, colors = colors )


    #Mixing groups and columns
    data = ([ [1], [2], [3,4], [4], [5], [6], [7], [8], [9], [10] ])
    vizier.horizontal_bar_plot ( 'hbar_4_group_series.png', data, 400, 300, border = 20, grid = True )

    #Using no labels, horizontal and vertical labels
    series_labels = ["data11", "data22"]
    data = Series([[3,4], [4,8], [5,3], [9,1]])
    x_labels = [ "line1", "line2", "line3", "line4", "line5", "line6" ]
    y_labels = [ "group1", "group2", "group3", "group4" ]
    vizier.horizontal_bar_plot ( 'hbar_5_no_labels_series.png', data, 600, 200, border = 20, series_labels = series_labels, grid = True )
    vizier.horizontal_bar_plot ( 'hbar_6_x_labels_series.png', data, 600, 200, border = 20, series_labels = series_labels, grid = True, x_labels = x_labels )
    vizier.horizontal_bar_plot ( 'hbar_7_y_labels_series.png', data, 600, 200, border = 20, series_labels = series_labels, grid = True, y_labels = y_labels )
    vizier.horizontal_bar_plot ( 'hbar_8_hy_labels_series.png', data, 600, 200, border = 20, series_labels = series_labels, display_values = True, grid = True, x_labels = x_labels, y_labels = y_labels )

    #Large data set
    data = Series([[10*random()] for x in range(25)])
    x_labels = ["large label name oh my god it's big" for x in data]
    vizier.horizontal_bar_plot ( 'hbar_9_large_series.png', data, 1000, 800, border = 20, grid = True, rounded_corners = True, x_labels = x_labels )

    #Stack horizontal
    data = Series([ [6, 4, 10], [8, 9, 3], [1, 10, 9], [2, 7, 11] ])
    colors = [ (1,0.2,0), (1,0.7,0), (1,1,0) ]
    y_labels = ["teste1", "teste2", "testegrande3", "testegrande4"]
    vizier.horizontal_bar_plot ( 'hbar_10_stack_series.png', data, 400, 300, border = 20, display_values = True, grid = True, rounded_corners = True, stack = True, 
                                    y_labels = y_labels, colors = colors )

if test_pie_plot :
    #Define a new backgrond
    background = cairo.LinearGradient(300, 0, 300, 400)
    background.add_color_stop_rgb(0.0,0.7,0.0,0.0)
    background.add_color_stop_rgb(1.0,0.3,0.0,0.0)

    #Plot data
    data = {"orcs" : 100, "goblins" : 230, "elves" : 50 , "demons" : 43, "humans" : 332}
    vizier.pie_plot( "pie_1_default_series.png", data, 600, 400 )
    vizier.pie_plot( "pie_2_gradient_shadow_series.png", data, 600, 400, gradient = True, shadow = True )
    vizier.pie_plot( "pie_3_background_series.png", data, 600, 400, background = background, gradient = True, shadow = True ) 

if test_donut_plot :
    #Define a new backgrond
    background = cairo.LinearGradient(300, 0, 300, 400)
    background.add_color_stop_rgb(0,0.4,0.4,0.4)
    background.add_color_stop_rgb(1.0,0.1,0.1,0.1)
    
    data = {"john" : 700, "mary" : 100, "philip" : 100 , "suzy" : 50, "yman" : 50}
    #Default plot, gradient and shadow, different background
    vizier.donut_plot( "donut_1_default_series.png", data, 600, 400, inner_radius = 0.3 )
    vizier.donut_plot( "donut_2_gradient_shadow_series.png", data, 600, 400, gradient = True, shadow = True, inner_radius = 0.3 )
    vizier.donut_plot( "donut_3_background_series.png", data, 600, 400, background = background, gradient = True, shadow = True, inner_radius = 0.3 )

if test_gantt_chart :
    #Default Plot
    pieces = Series([(0.5, 5.5), [(0, 4), (6, 8)], (5.5, 7), (7, 9)])
    x_labels = [ 'teste01', 'teste02', 'teste03', 'teste04']
    y_labels = [ '0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009', '0010' ]
    colors = [ (1.0, 0.0, 0.0), (1.0, 0.7, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0) ]
    vizier.gantt_chart('gantt_1_default_series.png', pieces, 500, 350, x_labels, y_labels, colors)
    
if test_themes :    
    data = Series([[1,2,3,4,5,6,7,8,9,10,11,12,13,14]])
    vizier.vertical_bar_plot ( 'bar_1_color_themes_series.png', data, 400, 300, border = 20, grid = True, colors="rainbow" )
    
    data = Series([[1,2,3,4,5,6,7,8,9,10,11,12,13,14]])
    vizier.vertical_bar_plot ( 'bar_2_color_themes_series.png', data, 400, 300, background = "white light_gray", border = 20, grid = True, colors="rainbow" )
    
    data = Series()
    data.range = (0,10,0.1)
    data.group_list = [ lambda x : 1, lambda y : y**2, lambda z : -z**2 ]
    vizier.function_plot( 'function_color_themes_series.png', data, 400, 300, grid = True, series_colors = ["red", "orange", "yellow"], step = 0.1 )
    
    #Scatter x DotLine
    t = [x*0.1 for x in range(0,40)]
    f = [math.exp(x) for x in t]
    g = [10*math.cos(x) for x in t]
    h = [10*math.sin(x) for x in t]
    erx = [0.1*random() for x in t]
    ery = [5*random() for x in t]
    data = Series({"exp" : [t,f], "cos" : [t,g], "sin" : [t,h]})
    series_colors = [ (1,0,0), (0,0,0) ]
    vizier.scatter_plot ( 'scatter_color_themes_series.png', data = data, errorx = [erx,erx], errory = [ery,ery], width = 800, height = 600, border = 20, 
                             axis = True, discrete = False, dots = 5, grid = True, 
                             x_title = "t", y_title = "f(t) g(t)", series_legend=True, series_colors = ["red", "blue", "orange"])
