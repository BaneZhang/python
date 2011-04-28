#!/usr/bin/env python3
# Copyright (c) 20011 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import itertools
import Block

__all__ = ["save_blocks_as_svg"]


SVG_START = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"
    "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
     width="{pxwidth}px" height="{pxheight}px" \
viewBox="0 0 {width} {height}">"""
SVG_END = "</svg>\n"

SVG_RECT = """<rect x="{x}" y="{y}" width="{width}" \
height="{height}" fill="{fill}" stroke="{stroke}"/>"""

SVG_TEXT = """<text x="{x}" y="{y}" text-anchor="middle" \
font-size="{fontsize}">{text}</text>"""


class Cell:

    def __init__(self, row=0, column=0, rows=0, columns=0, text=None,
                 color=None):
        self.row = row
        self.column = column
        self.rows = rows
        self.columns = columns
        self.text = text
        self.color = color


    def __repr__(self):
        return ("Cell({0.row!r}, {0.column!r}, {0.rows!r}, "
                "{0.columns!r}, {0.text!r}, {0.color!r})"
                .format(self))

        
    def __lt__(self, other):
        if self.row != other.row:
            return self.row < other.row
        if self.column != other.column:
            return self.column < other.column
        if self.rows != other.rows:
            return self.rows < other.rows
        if self.columns != other.columns:
            return self.columns < other.columns
        return self.text < other.text


def populate_cells(block, row, column, cells):
    cell = Cell(row, column, 1, 1, block.name, block.color)
    if block.children:
        row += 1
    for child in block.children:
        if Block.is_new_row(child):
            row += 1
            column = 0
        else:
            child_cell = populate_cells(child, row, column, cells)
            column += 1
            cell.rows += child_cell.rows
            cell.columns += child_cell.columns
    cells.append(cell)
    return cell


def cells_for_blocks(blocks):
    cells = []
    populate_cells(blocks, 0, 0, cells)
    return sorted(cells)


def compute_widths_and_rows(cells, SCALE_BY):
    columns = 0
    widths = [0] * cells[0].columns
    for row, group in itertools.groupby(cells[1:], lambda x: x.row):
        offset = 0
        for x, cell in enumerate(group):
            columns = max(columns, x)
            width = len(cell.text) // cell.columns
            for column in range(cell.columns):
                widths[column + offset] = max(width,
                                              widths[column + offset])
            offset += cell.columns
    widths = [width * SCALE_BY for width in widths[:columns + 1]]
    return widths, row + 1


def compute_x_offsets_for_columns(widths):
    x_for_column = [0]
    x = 0
    for width in widths:
        x += width
        x_for_column.append(x)
    return x_for_column


def populate_svg(svg, cells, widths, x_for_column, ROW_HEIGHT):
    for cell in cells:
        if cell.text is None or cell.text == "":
            continue

        x = x_for_column[cell.column]
        y = cell.row * ROW_HEIGHT
        width = sum(widths[cell.column:cell.column + cell.columns])
        height = cell.rows * ROW_HEIGHT
        fill = cell.color
        stroke = "black"
        svg.append(SVG_RECT.format(**locals()))

        x += (width // 2)
        y += 2 + ROW_HEIGHT // 2
        fontsize = ROW_HEIGHT // 2
        text = cell.text
        svg.append(SVG_TEXT.format(**locals()))


def save_blocks_as_svg(blocks, filename):
    if not blocks.has_children():
        return False

    SCALE_BY = 4
    ROW_HEIGHT = 10

    cells = cells_for_blocks(blocks)
    widths, rows = compute_widths_and_rows(cells, SCALE_BY)
    x_for_column = compute_x_offsets_for_columns(widths)

    width = x_for_column.pop()
    height = rows * ROW_HEIGHT
    pxwidth = width * SCALE_BY
    pxheight = height * SCALE_BY

    svg = [SVG_START.format(**locals())]
    populate_svg(svg, cells, widths, x_for_column, ROW_HEIGHT)
    svg.append(SVG_END)

    try:
        with open(filename, "wt", encoding="utf8") as fh:
            fh.write("\n".join(svg))
    except EnvironmentError as err:
        print("error: {0}".format(err), file=sys.stderr)
        return False
    return True
