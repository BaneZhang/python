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
import pickle
import shelve
import sys
import Console
import Util


def main():
    functions = dict(a=add_bookmark, e=edit_bookmark, l=list_bookmarks,
                     r=remove_bookmark, q=quit)
    filename = os.path.join(os.path.dirname(__file__), "bookmarks.dbm")
    db = None
    try:
        db = shelve.open(filename, protocol=pickle.HIGHEST_PROTOCOL)
        action = ""
        while True:
            print("\nBookmarks ({0})".format(os.path.basename(filename)))
            list_bookmarks(db)
            print()
            menu = "(A)dd  (E)dit  (L)ist  (R)emove  (Q)uit"
            action = Console.get_menu_choice(menu, "aelrq",
                                        "l" if len(db) else "a", True)
            functions[action](db)
    finally:
        if db is not None:
            db.close()


def add_bookmark(db):
    url = Console.get_string("URL", "URL")
    if not url:
        return
    if "://" not in url:
        url = "http://" + url
    name = Console.get_string("Name", "name")
    if not name:
        return
    db[name] = url
    db.sync()
    

def edit_bookmark(db):
    name = find_bookmark(db, "edit")
    if name is None:
        return
    url = Console.get_string("URL", "URL", db[name])
    if not url:
        return
    if "://" not in url:
        url = "http://" + url
    new_name = Console.get_string("Name", "name", name)
    db[new_name] = url
    if new_name != name:
        del db[name]
    db.sync()
    

def list_bookmarks(db):
    for i, name in enumerate(sorted(db, key=str.lower)):
        print("({0}) {1:.<40} {2}".format(i + 1, name, db[name]))
    

def remove_bookmark(db):
    name = find_bookmark(db, "remove")
    if name is None:
        return
    ans = Console.get_bool("Remove {0}?".format(db[name]), "no")
    if ans:
        del db[name]
        db.sync()
    

def quit(db):
    print("Saved {0} bookmark{1}".format(len(db), Util.s(len(db))))
    db.close()
    sys.exit()


def find_bookmark(db, message):
    message = "Number of bookmark to " + message
    number = Console.get_integer(message, "number", minimum=0,
                                 maximum=len(db))
    if number == 0:
        return None
    number -= 1
    for i, name in enumerate(sorted(db, key=str.lower)):
        if i == number:
            return name

main()
