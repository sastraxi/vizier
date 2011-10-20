from __future__ import with_statement
import contextlib
import cairo
import math

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
