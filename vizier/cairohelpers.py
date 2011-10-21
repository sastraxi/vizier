from __future__ import with_statement
import contextlib
import cairo
import math

# XXX these may interfere with similar definitions in vizier.book

TOP = 1.0
MIDDLE = 0.5
BOTTOM = 0.0

LEFT = 0.0
CENTER = -0.5
RIGHT = -1.0

@contextlib.contextmanager
def subcontext(ctx, x, y, width, height):
    ctx.save()
    ctx.new_path()
    ctx.rectangle(x, y, width, height)
    ctx.clip()
    ctx.translate(x, y)
    yield
    ctx.restore()

@contextlib.contextmanager
def unscaled(ctx):
    ctx.save()
    ctx.identity_matrix()   
    yield
    ctx.restore()

@contextlib.contextmanager
def unclipped(ctx):
    ctx.save()
    ctx.reset_clip()
    yield
    ctx.restore()

def scaledsize(ctx, x, y):
    saved_path = ctx.copy_path()
    ctx.save()
    
    ctx.identity_matrix()
    ctx.new_path()
    ctx.move_to(0, 0)
    ctx.line_to(x, y)

    ctx.restore()
    x1, y1, x2, y2 = ctx.path_extents()

    ctx.new_path()
    ctx.append_path(saved_path)
    return x2 - x1, y2 - y1

def stroke(ctx, width):
    with unscaled(ctx):
        ctx.set_line_width(width)
        ctx.stroke()

def dot(ctx, x, y, radius):
    ctx.move_to(x, y)
    with unscaled(ctx):
        sx, sy = ctx.get_current_point()
        ctx.new_path()
        ctx.arc(sx, sy, radius, 0, 2 * math.pi)
        ctx.fill()

def roundedrect(ctx, x, y, width, height, radius):
    ctx.new_path()
    ctx.arc(x + width - radius, y + radius, radius, -0.5 * math.pi, 0)
    ctx.arc(x + width - radius, y + height - radius, radius, 0, 0.5 * math.pi)
    ctx.arc(x + radius, y + height - radius, radius, 0.5 * math.pi, 1.0 * math.pi)
    ctx.arc(x + radius, y + radius, radius, 1.0 * math.pi, 1.5 * math.pi)

# FIXME drawtext doesn't actually work with rotation yet
def drawtext(ctx, text, halign=LEFT, valign=TOP, hadjust=0.0, vadjust=0.0, size=None, rotation=0):
    with unscaled(ctx):
        sx, sy = ctx.get_current_point()
        if size: ctx.set_font_size(size)

        ctx.rotate(rotation)        

        x_bearing, y_bearing, width, height, x_advance, y_advance = ctx.text_extents(text)
        ctx.rel_move_to(halign * x_advance + hadjust, valign * height + vadjust)            

        ctx.show_text(text)
        #ctx.move_to(sx, sy)
