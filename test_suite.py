#! usr/bin/env python 
import os

import pyglet
from pyglet import gl

import squirtle

config = pyglet.gl.Config(sample_buffers=1, samples=4)
w = pyglet.window.Window(config=config, resizable=True)

# w = pyglet.window.Window(800, 600)
keys = pyglet.window.key.KeyStateHandler()
w.push_handlers(keys)

gl.glClearColor(1, 1, 1, 1)
gl.glEnable(gl.GL_LINE_SMOOTH)
gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
gl.glLineWidth(2)

squirtle.setup_gl()

filelist = [f for f in os.listdir('svgs')
            if f.endswith('svg') or f.endswith('svgz')]
filename = None
svgObj = None


def nextFile():
    global filename, svgObj
    if not filename:
        next = 0
    else:
        prevFile = os.path.basename(filename)
        next = filelist.index(prevFile) + 1
        next %= len(filelist)
    filename = os.path.join('svgs', filelist[next])
    print(f'Parsing {filename}')
    svgObj = squirtle.SVG(filename)
    svgObj.anchor_x, svgObj.anchor_y = svgObj.width / 2, svgObj.height / 2


nextFile()

zoom = 1
angle = 0
draw_x = 400
draw_y = 300


def tick(dt):
    global zoom, angle, draw_x, draw_y
    if keys[pyglet.window.key.W]:
        draw_y -= 8
    elif keys[pyglet.window.key.S]:
        draw_y += 8
    elif keys[pyglet.window.key.D]:
        draw_x -= 8
    elif keys[pyglet.window.key.A]:
        draw_x += 8
    elif keys[pyglet.window.key.UP]:
        zoom *= 1.1
    elif keys[pyglet.window.key.DOWN]:
        zoom /= 1.1
    elif keys[pyglet.window.key.LEFT]:
        angle -= 8
    elif keys[pyglet.window.key.RIGHT]:
        angle += 8


def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        nextFile()


w.push_handlers(on_key_press)

pyglet.clock.schedule_interval(tick, 1 / 60.0)


@w.event
def on_draw():
    w.clear()
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.gluOrtho2D(0.0, 800.0, 600, 0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    svgObj.draw(draw_x, draw_y, scale=zoom, angle=angle)
    # Necessary flush to ensure each SVG is displayed
    #   https://stackoverflow.com/a/64283380
    pyglet.gl.glFlush()


pyglet.app.run()
