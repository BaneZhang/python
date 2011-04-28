#!/usr/bin/env python3
# Copyright (c) 2008-11 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import os
import re
import sys
import tkinter


class MainWindow:

    def __init__(self, parent):
        self.parent = parent

        self.regex = tkinter.StringVar()
        self.regex.set(r"(?P<key>\w+)\s*=\s*(?P<value>[\d.]+)\s*(.*)")
        self.text = tkinter.StringVar()
        self.text.set("quantity = 11.95, etc")
        self.ignore_case = tkinter.IntVar()
        self.dotall = tkinter.IntVar()
        self.captures = []
        for i in range(10):
            self.captures.append(tkinter.StringVar())
        self.message = tkinter.StringVar()

        frame = tkinter.Frame(self.parent)
        regexLabel = tkinter.Label(frame, text="Regex:", underline=0)
        regexLabel.grid(row=0, column=0, padx=2, pady=2, sticky=tkinter.W)
        regexEntry = tkinter.Entry(frame, width=50,
                                   textvariable=self.regex)
        regexEntry.grid(row=0, column=1, columnspan=2, padx=2, pady=2,
                        sticky=tkinter.EW)
        textLabel = tkinter.Label(frame, text="Text:", underline=0)
        textLabel.grid(row=1, column=0, padx=2, pady=2, sticky=tkinter.W)
        textEntry = tkinter.Entry(frame, textvariable=self.text)
        textEntry.grid(row=1, column=1, columnspan=2, padx=2, pady=2,
                       sticky=tkinter.EW)
        self.ignoreCaseCheckbutton = tkinter.Checkbutton(frame,
                text="Ignore case", underline=0, variable=self.ignore_case)
        self.ignoreCaseCheckbutton.grid(row=2, column=0, columnspan=2,
                                        padx=2, pady=2, sticky=tkinter.E)
        self.dotallCheckbutton = tkinter.Checkbutton(frame, text="Dotall",
                underline=0, variable=self.dotall)
        self.dotallCheckbutton.grid(row=2, column=2, padx=2, pady=2,
                                    sticky=tkinter.E)
        self.groupLabels = []
        self.captureLabels = []
        row = 3
        for i in range(10):
            label = tkinter.Label(frame, text="Group {0}".format(i))
            label.grid(row=row + i, column=0, padx=2, pady=2,
                       sticky=tkinter.W)
            self.groupLabels.append(label)
            capture = tkinter.Label(frame, relief=tkinter.RIDGE,
                                    anchor=tkinter.W, bg="aliceblue",
                                    textvariable=self.captures[i])
            capture.grid(row=row + i, column=1, columnspan=2, padx=2,
                         pady=2, sticky=tkinter.EW)
            self.captureLabels.append(capture)
        self.messageLabel = tkinter.Label(frame, relief=tkinter.GROOVE,
                                          anchor=tkinter.W, bg="white",
                                          textvariable=self.message)
        self.messageLabel.grid(row=14, column=0, columnspan=3, padx=2,
                               pady=2, sticky=tkinter.EW)

        frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=999)
        frame.columnconfigure(2, weight=999)

        window = self.parent.winfo_toplevel()
        window.columnconfigure(0, weight=1)

        regexEntry.focus_set()
        parent.bind("<Alt-r>", lambda arg: regexEntry.focus_set())
        parent.bind("<Alt-t>", lambda arg: textEntry.focus_set())
        parent.bind("<Alt-i>", self.ignoreCaseChanged)
        parent.bind("<Alt-d>", self.dotallChanged)
        parent.bind("<Control-q>", self.quit)
        parent.bind("<Escape>", self.quit)
        regexEntry.bind("<Any-KeyRelease>", self.calculate)
        textEntry.bind("<Any-KeyRelease>", self.calculate)
        parent.title("Regex")
        self.calculate()


    def ignoreCaseChanged(self, *ignore):
        self.ignoreCaseCheckbutton.invoke()
        self.calculate()


    def dotallChanged(self, *ignore):
        self.dotallCheckbutton.invoke()
        self.calculate()


    def calculate(self, *ignore):
        for i in range(10):
            self.captures[i].set("")
            self.captureLabels[i]["bg"] = "aliceblue"
            self.groupLabels[i]["text"] = "Group {0}".format(i)
        if not self.regex.get():
            return
        try:
            flags = 0
            if self.ignore_case.get():
                flags |= re.IGNORECASE 
            if self.dotall.get():
                flags |= re.DOTALL
            regex = re.compile(self.regex.get(), flags)
            match = regex.search(self.text.get())
        except re.error:
            self.message.set("Invalid regex")
            self.messageLabel["bg"] = "mistyrose"
        else:
            self.message.set("Matched" if match is not None
                             else "Unmatched")
            self.messageLabel["bg"] = "white"
            if match:
                groups = {v: k for k, v in match.groupdict().items()}
                limit = min(10, 1 + len(match.groups()))
                for i in range(limit):
                    group = match.group(i)
                    if group is not None:
                        self.captures[i].set(group)
                        if group in groups:
                            self.groupLabels[i]["text"] = (
                                "Group {0} '{1}'".format(
                                i, groups[group]))
                        self.captureLabels[i]["bg"] = "cornsilk"


    def quit(self, event=None):
        self.parent.destroy()


application = tkinter.Tk()
path = os.path.join(os.path.dirname(__file__), "images/")
if sys.platform.startswith("win"):
    icon = path + "regex.ico"
else:
    icon = "@" + path + "regex.xbm"
application.iconbitmap(icon)
window = MainWindow(application)
application.protocol("WM_DELETE_WINDOW", window.quit)
application.mainloop()

