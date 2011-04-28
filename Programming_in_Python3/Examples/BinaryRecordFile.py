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

"""
>>> import shutil
>>> import sys

>>> S = struct.Struct("<15s")
>>> fileA = os.path.join(tempfile.gettempdir(), "fileA.dat")
>>> fileB = os.path.join(tempfile.gettempdir(), "fileB.dat")
>>> for name in (fileA, fileB):
...    try:
...        os.remove(name)
...    except EnvironmentError:
...        pass

>>> brf = BinaryRecordFile(fileA, S.size)
>>> for i, text in enumerate(("Alpha", "Bravo", "Charlie", "Delta",
...        "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet",
...        "Kilo", "Lima", "Mike", "November", "Oscar", "Papa",
...        "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor",
...        "Whisky", "X-Ray", "Yankee", "Zulu")):
...    brf[i] = S.pack(text.encode("utf8"))
>>> assert len(brf) == 26
>>> brf[len(brf) + 2] = S.pack(b"Extra at the end")
>>> assert len(brf) == 29
>>> shutil.copy(fileA, fileB)
>>> del brf[12]
>>> assert len(brf) == 29
>>> brf.compact()
>>> assert len(brf) == 26
>>> brf.close()

>>> if ((os.path.getsize(fileA) + 3 + (3 * S.size)) !=
...        os.path.getsize(fileB)):
...    print("FAIL#1: expected file sizes are wrong")
...    sys.exit()

>>> shutil.copy(fileB, fileA)
>>> if os.path.getsize(fileA) != os.path.getsize(fileB):
...    print("FAIL#2: expected file sizes differ")
...    sys.exit()

>>> for name in (fileA, fileB):
...    try:
...        os.remove(name)
...    except EnvironmentError:
...        pass

>>> filename =  os.path.join(tempfile.gettempdir(), "test.dat")
>>> if os.path.exists(filename): os.remove(filename)
>>> S = struct.Struct("<8s")
>>> test = BinaryRecordFile(filename, S.size)
>>> test[0] = S.pack(b"Alpha")
>>> test[1] = S.pack(b"Bravo")
>>> test[2] = S.pack(b"Charlie")
>>> test[3] = S.pack(b"Delta")
>>> test[4] = S.pack(b"Echo")
>>> test.inplace_compact()  # No blank or deleted
>>> test.close()
>>> os.path.getsize(filename)
45
>>> test = BinaryRecordFile(filename, S.size)
>>> len(test)
5
>>> for index in range(len(test)):
...     del test[index]
>>> test.inplace_compact()  # All blank or deleted
>>> test.close()
>>> os.path.getsize(filename)
0
>>> test = BinaryRecordFile(filename, S.size)
>>> test[0] = S.pack(b"Alpha")
>>> test[1] = S.pack(b"Bravo")
>>> test[2] = S.pack(b"Charlie")
>>> test[3] = S.pack(b"Delta")
>>> test[4] = S.pack(b"Echo")
>>> del test[2]
>>> del test[4]
>>> del test[3]
>>> test.inplace_compact()  # Blank or deleted at the end
>>> test.close()
>>> os.path.getsize(filename)
18
>>> test = BinaryRecordFile(filename, S.size)
>>> test[0] = S.pack(b"Alpha")
>>> test[1] = S.pack(b"Bravo")
>>> test[2] = S.pack(b"Charlie")
>>> test[3] = S.pack(b"Delta")
>>> test[4] = S.pack(b"Echo")
>>> del test[0]
>>> del test[2]
>>> del test[3]
>>> test.inplace_compact()  # Blank or deleted interspersed
>>> test.close()
>>> os.path.getsize(filename)
18
>>> os.remove(filename)
"""

import os
import struct
import tempfile


_DELETED = b"\x01"
_OKAY = b"\x02"


class BinaryRecordFile:

    def __init__(self, filename, record_size, auto_flush=True):
        """A random access binary file that behaves rather like a list
        with each item a bytes or bytesarray object of record_size.
        """
        self.__record_size = record_size + 1
        mode = "w+b" if not os.path.exists(filename) else "r+b"
        self.__fh = open(filename, mode)
        self.auto_flush = auto_flush


    @property
    def record_size(self):
        "The size of each item"
        return self.__record_size - 1


    @property
    def name(self):
        "The name of the file"
        return self.__fh.name


    def flush(self):
        """Flush writes to disk
        Done automatically if auto_flush is True
        """
        self.__fh.flush()


    def close(self):
        self.__fh.close()


    def __setitem__(self, index, record):
        """Sets the item at position index to be the given record

        The index position can be beyond the current end of the file.
        """
        assert isinstance(record, (bytes, bytearray)), \
               "binary data required"
        assert len(record) == self.record_size, (
            "record must be exactly {0} bytes".format(
            self.record_size))
        self.__fh.seek(index * self.__record_size)
        self.__fh.write(_OKAY)
        self.__fh.write(record)
        if self.auto_flush:
            self.__fh.flush()


    def __getitem__(self, index):
        """Returns the item at the given index position

        If there is no item at the given position, raises an
        IndexError exception.
        If the item at the given position has been deleted returns
        None.
        """
        self.__seek_to_index(index)
        state = self.__fh.read(1)
        if state != _OKAY:
            return None
        return self.__fh.read(self.record_size)
        

    def __seek_to_index(self, index):
        if self.auto_flush:
            self.__fh.flush()
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        offset = index * self.__record_size
        if offset >= end:
            raise IndexError("no record at index position {0}".format(
                             index))
        self.__fh.seek(offset)


    def __delitem__(self, index):
        """Deletes the item at the given index position.

        See undelete()
        """
        self.__seek_to_index(index)
        state = self.__fh.read(1)
        if state != _OKAY:
            return
        self.__fh.seek(index * self.__record_size)
        self.__fh.write(_DELETED)
        if self.auto_flush:
            self.__fh.flush()


    def undelete(self, index):
        """Undeletes the item at the given index position.

        If an item is deleted it can be undeleted---providing compact()
        (or inplace_compact()) has not been called.
        """
        self.__seek_to_index(index)
        state = self.__fh.read(1)
        if state == _DELETED:
            self.__fh.seek(index * self.__record_size)
            self.__fh.write(_OKAY)
            if self.auto_flush:
                self.__fh.flush()
            return True
        return False


    def __len__(self):
        """The number number of record positions.

        This is the maximum number of records there could be at
        present. The true number may be less because some records
        might be deleted. After calling compact() (or
        inplace_compact()), this returns the true number.
        """
        if self.auto_flush:
            self.__fh.flush()
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        return end // self.__record_size


    def compact(self, keep_backup=False):
        """Eliminates blank and deleted records"""
        compactfile = self.__fh.name + ".$$$"
        backupfile = self.__fh.name + ".bak"
        self.__fh.flush()
        self.__fh.seek(0)
        fh = open(compactfile, "wb")
        while True:
            data = self.__fh.read(self.__record_size)
            if not data:
                break
            if data[:1] == _OKAY:
                fh.write(data)
        fh.close()
        self.__fh.close()

        os.rename(self.__fh.name, backupfile)
        os.rename(compactfile, self.__fh.name)
        if not keep_backup:
            os.remove(backupfile)
        self.__fh = open(self.__fh.name, "r+b")


    def inplace_compact(self):
        """Eliminates blank and deleted records in-place preserving the
        original order
        """
        index = 0
        length = len(self)
        while index < length:
            self.__seek_to_index(index)
            state = self.__fh.read(1)
            if state != _OKAY:
                for next in range(index + 1, length):
                    self.__seek_to_index(next)
                    state = self.__fh.read(1)
                    if state == _OKAY:
                        self[index] = self[next]
                        del self[next]
                        break
                else:
                    break
            index += 1
        self.__seek_to_index(0)
        state = self.__fh.read(1)
        if state != _OKAY:
            self.__fh.truncate(0)
        else:
            limit = None
            for index in range(len(self) - 1, 0, -1):
                self.__seek_to_index(index)
                state = self.__fh.read(1)
                if state != _OKAY:
                    limit = index
                else:
                    break
            if limit is not None:
                self.__fh.truncate(limit * self.__record_size)
        self.__fh.flush()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
