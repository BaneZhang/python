#!/usr/bin/env python3

import Graphics.Png as Png

def load(filename):
    print("eps: load", filename)


def save(filename):
    print(Png.SAMPLE_RATE)
    print("eps: save", filename)


def width():
    print("eps: width")


def height():
    print("eps: height")


def color_at(x, y):
    print("eps: color_at")


def set_color_at(x, y, color):
    print("eps: set_color_at")
