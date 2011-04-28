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

import locale
locale.setlocale(locale.LC_ALL, "")

import datetime
import gzip
import optparse
import os
import pickle
import re
import struct
import sys
import textwrap
import xml.dom.minidom
import xml.etree.ElementTree
import xml.parsers.expat
import xml.sax
import xml.sax.saxutils

USE_RESTRICTIVE_P_FORMAT = False
USE_LONG_WINDED_IMPORT_FUNCTION = False

MAGIC = b"AIB\x00"
FORMAT_VERSION = b"\x00\x01"
GZIP_MAGIC = b"\x1F\x8B"

NumbersStruct = struct.Struct("<Idi?")


class IncidentError(Exception): pass


class IncidentSaxHandler(xml.sax.handler.ContentHandler):

    def __init__(self, incidents):
        super().__init__()
        self.__data = {}
        self.__text = ""
        self.__incidents = incidents
        self.__incidents.clear()


    def startElement(self, name, attributes):
        if name == "incident":
            self.__data = {}
            for key, value in attributes.items():
                if key == "date":
                    self.__data[key] = datetime.datetime.strptime(
                                            value, "%Y-%m-%d").date()
                elif key == "pilot_percent_hours_on_type":
                    self.__data[key] = float(value)
                elif key == "pilot_total_hours":
                    self.__data[key] = int(value)
                elif key == "midair":
                    self.__data[key] = bool(int(value))
                else:
                    self.__data[key] = value
        self.__text = ""


    def endElement(self, name):
        if name == "incident":
            if len(self.__data) != 9:
                raise IncidentError("missing data")
            incident = Incident(**self.__data)
            self.__incidents[incident.report_id] = incident
        elif name in frozenset({"airport", "narrative"}):
            self.__data[name] = self.__text.strip()
        self.__text = ""


    def characters(self, text):
        self.__text += text


class Incident:

    def __init__(self, report_id, date, airport, aircraft_id,
                 aircraft_type, pilot_percent_hours_on_type,
                 pilot_total_hours, midair, narrative=""):
        """
        >>> kwargs = dict(report_id="2007061289X")
        >>> kwargs["date"] = datetime.date(2007, 6, 12)
        >>> kwargs["airport"] = "Los Angeles"
        >>> kwargs["aircraft_id"] = "8184XK"
        >>> kwargs["aircraft_type"] = "CVS91"
        >>> kwargs["pilot_percent_hours_on_type"] = 17.5
        >>> kwargs["pilot_total_hours"] = 1258
        >>> kwargs["midair"] = False
        >>> incident = Incident(**kwargs)
        >>> incident.report_id, incident.date, incident.airport
        ('2007061289X', datetime.date(2007, 6, 12), 'Los Angeles')
        >>> incident.aircraft_id, incident.aircraft_type, incident.midair
        ('8184XK', 'CVS91', False)
        >>> incident.pilot_percent_hours_on_type, incident.pilot_total_hours
        (17.5, 1258)
        >>> incident.approximate_hours_on_type
        220
        >>> incident.narrative = "Two different\\nlines of text"
        >>> str(incident)
        "Incident('2007061289X', datetime.date(2007, 6, 12), 'Los Angeles', '8184XK', 'CVS91', 17.5, 1258, False, '''Two different\\nlines of text''')"
        >>> kwargs["report_id"] = "fail"
        >>> incident = Incident(**kwargs)
        Traceback (most recent call last):
        ...
        AssertionError: invalid report ID
        """
        assert len(report_id) >= 8 and len(report_id.split()) == 1, \
               "invalid report ID"
        self.__report_id = report_id
        self.date = date
        self.airport = airport
        self.aircraft_id = aircraft_id
        self.aircraft_type = aircraft_type
        self.pilot_percent_hours_on_type = pilot_percent_hours_on_type
        self.pilot_total_hours = pilot_total_hours
        self.midair = midair
        self.narrative = narrative


    @property
    def report_id(self):
        return self.__report_id


    @property
    def date(self):
        "The incident date"
        return self.__date

    @date.setter
    def date(self, date):
        assert isinstance(date, datetime.date), "invalid date"
        self.__date = date


    @property
    def pilot_percent_hours_on_type(self):
        "The percentage of total hours flown on this aircraft type"
        return self.__pilot_percent_hours_on_type

    @pilot_percent_hours_on_type.setter
    def pilot_percent_hours_on_type(self, percent):
        assert 0.0 <= percent <= 100.0, "out of range percentage"
        self.__pilot_percent_hours_on_type = percent


    @property
    def pilot_total_hours(self):
        "The total hours this pilot has flown"
        return self.__pilot_total_hours

    @pilot_total_hours.setter
    def pilot_total_hours(self, hours):
        assert hours > 0, "invalid number of hours"
        self.__pilot_total_hours = hours


    @property
    def approximate_hours_on_type(self):
        return int(self.__pilot_total_hours *
                   (self.__pilot_percent_hours_on_type / 100))


    @property
    def midair(self):
        "Whether the incident involved another aircraft"
        return self.__midair

    @midair.setter
    def midair(self, value):
        assert isinstance(value, bool), "invalid midair value"
        self.__midair = value


    @property
    def airport(self):
        "The incident's airport"
        return self.__airport

    @airport.setter
    def airport(self, airport):
        assert airport and "\n" not in airport, "invalid airport"
        self.__airport = airport


    @property
    def aircraft_id(self):
        "The aircraft ID"
        return self.__aircraft_id

    @aircraft_id.setter
    def aircraft_id(self, aircraft_id):
        assert aircraft_id and "\n" not in aircraft_id, \
               "invalid aircraft ID"
        self.__aircraft_id = aircraft_id


    @property
    def aircraft_type(self):
        "The aircraft type"
        return self.__aircraft_type

    @aircraft_type.setter
    def aircraft_type(self, aircraft_type):
        assert aircraft_type and "\n" not in aircraft_type, \
               "invalid aircraft type"
        self.__aircraft_type = aircraft_type


    @property
    def narrative(self):
        "The incident's narrative"
        return self.__narrative

    @narrative.setter
    def narrative(self, narrative):
        self.__narrative = narrative


    def __repr__(self):
        return ("Incident({report_id!r}, {date!r}, "
                "{airport!r}, {aircraft_id!r}, "
                "{aircraft_type!r}, "
                "{pilot_percent_hours_on_type!r}, "
                "{pilot_total_hours!r}, {midair!r}, "
                "'''{narrative}''')".format(**self))


class IncidentCollection(dict):

    """
    >>> kwargs = dict(report_id="2007061289X")
    >>> kwargs["date"] = datetime.date(2007, 6, 12)
    >>> kwargs["airport"] = "Los Angeles"
    >>> kwargs["aircraft_id"] = "8184XK"
    >>> kwargs["aircraft_type"] = "CVS91"
    >>> kwargs["pilot_percent_hours_on_type"] = 17.5
    >>> kwargs["pilot_total_hours"] = 1258
    >>> kwargs["midair"] = False
    >>> incidents = IncidentCollection()
    >>> incident = Incident(**kwargs)
    >>> incidents[incident.report_id] = incident
    >>> kwargs["report_id"] = "2007061989K"
    >>> kwargs["date"] = datetime.date(2007, 6, 19)
    >>> kwargs["pilot_percent_hours_on_type"] = 20
    >>> kwargs["pilot_total_hours"] = 17521
    >>> incident = Incident(**kwargs)
    >>> incidents[incident.report_id] = incident
    >>> kwargs["report_id"] = "2007052989V"
    >>> kwargs["date"] = datetime.date(2007, 5, 29)
    >>> kwargs["pilot_total_hours"] = 1875
    >>> incident = Incident(**kwargs)
    >>> incidents[incident.report_id] = incident
    >>> for incident in incidents.values():
    ...     print(incident.report_id, incident.date.isoformat())
    2007052989V 2007-05-29
    2007061289X 2007-06-12
    2007061989K 2007-06-19
    >>> for report_id in reversed(incidents):
    ...     print(report_id, incidents[report_id].date.isoformat())
    2007061989K 2007-06-19
    2007061289X 2007-06-12
    2007052989V 2007-05-29
    """

    def values(self):
        for report_id in self.keys():
            yield self[report_id]


    def items(self):
        for report_id in self.keys():
            yield (report_id, self[report_id])


    def __iter__(self):
        for report_id in sorted(super().keys()):
            yield report_id

    keys = __iter__


    def __reversed__(self):
        for report_id in sorted(super().keys(), reverse=True):
            yield report_id


    def export(self, filename, writer=None, compress=False):
        extension = os.path.splitext(filename)[1].lower()
        if extension == ".aix":
            if writer == "dom":
                return self.export_xml_dom(filename)
            elif writer == "etree":
                return self.export_xml_etree(filename)
            elif writer == "manual":
                return self.export_xml_manual(filename)
        elif extension == ".ait":
            return self.export_text(filename)
        elif extension == ".aib":
            return self.export_binary(filename, compress)
        elif extension == ".aip":
            return self.export_pickle(filename, compress)
        elif extension in (".htm", ".html"):
            return self.export_html(filename)


    def import_(self, filename, reader=None):
        extension = os.path.splitext(filename)[1].lower()
        call = {(".aix", "dom"): self.import_xml_dom,
                (".aix", "etree"): self.import_xml_etree,
                (".aix", "sax"): self.import_xml_sax,
                (".ait", "manual"): self.import_text_manual,
                (".ait", "regex"): self.import_text_regex,
                (".aib", None): self.import_binary,
                (".aip", None): self.import_pickle}
        result = call[extension, reader](filename)
        if result == False:
            self.clear()
        return result

    if USE_LONG_WINDED_IMPORT_FUNCTION:
        def import_(self, filename, reader=None):
            extension = os.path.splitext(filename)[1].lower()
            result = False
            if extension == ".aix":
                if reader == "dom":
                    result = self.import_xml_dom(filename)
                elif reader == "etree":
                    result = self.import_xml_etree(filename)
                elif reader == "sax":
                    result = self.import_xml_sax(filename)
            elif extension == ".ait":
                if reader == "manual":
                    result = self.import_text_manual(filename)
                elif reader == "regex":
                    result = self.import_text_regex(filename)
            elif extension == ".aib":
                result = self.import_binary(filename)
            elif extension == ".aip":
                result = self.import_pickle(filename)
            if result == False:
                self.clear()
            return result


    def export_xml_dom(self, filename):
        dom = xml.dom.minidom.getDOMImplementation()
        tree = dom.createDocument(None, "incidents", None)
        root = tree.documentElement
        for incident in self.values():
            element = tree.createElement("incident")
            for attribute, value in (
                    ("report_id", incident.report_id),
                    ("date", incident.date.isoformat()),
                    ("aircraft_id", incident.aircraft_id),
                    ("aircraft_type", incident.aircraft_type),
                    ("pilot_percent_hours_on_type",
                     str(incident.pilot_percent_hours_on_type)),
                    ("pilot_total_hours",
                     str(incident.pilot_total_hours)),
                    ("midair", str(int(incident.midair)))):
                element.setAttribute(attribute, value)
            for name, text in (("airport", incident.airport),
                               ("narrative", incident.narrative)):
                text_element = tree.createTextNode(text)
                name_element = tree.createElement(name)
                name_element.appendChild(text_element)
                element.appendChild(name_element)
            root.appendChild(element)

        fh = None
        try:
            fh = open(filename, "w", encoding="utf8")
            tree.writexml(fh, encoding="UTF-8")
            return True
        except EnvironmentError as err:
            print("{0}: export error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def import_xml_dom(self, filename):

        def get_text(node_list):
            text = []
            for node in node_list:
                if node.nodeType == node.TEXT_NODE:
                    text.append(node.data)
            return "".join(text).strip()

        try:
            dom = xml.dom.minidom.parse(filename)
        except (EnvironmentError,
                xml.parsers.expat.ExpatError) as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False

        self.clear()
        for element in dom.getElementsByTagName("incident"):
            try:
                data = {}
                for attribute in ("report_id", "date", "aircraft_id",
                        "aircraft_type",
                        "pilot_percent_hours_on_type",
                        "pilot_total_hours", "midair"):
                    data[attribute] = element.getAttribute(attribute)
                data["date"] = datetime.datetime.strptime(
                                    data["date"], "%Y-%m-%d").date()
                data["pilot_percent_hours_on_type"] = (
                        float(data["pilot_percent_hours_on_type"]))
                data["pilot_total_hours"] = int(
                        data["pilot_total_hours"])
                data["midair"] = bool(int(data["midair"]))
                airport = element.getElementsByTagName("airport")[0]
                data["airport"] = get_text(airport.childNodes)
                narrative = element.getElementsByTagName(
                                                    "narrative")[0]
                data["narrative"] = get_text(narrative.childNodes)
                incident = Incident(**data)
                self[incident.report_id] = incident
            except (ValueError, LookupError, IncidentError) as err:
                print("{0}: import error: {1}".format(
                      os.path.basename(sys.argv[0]), err))
                return False
        return True


    def export_xml_etree(self, filename):
        root = xml.etree.ElementTree.Element("incidents")
        for incident in self.values():
            element = xml.etree.ElementTree.Element("incident",
                    report_id=incident.report_id,
                    date=incident.date.isoformat(),
                    aircraft_id=incident.aircraft_id,
                    aircraft_type=incident.aircraft_type,
                    pilot_percent_hours_on_type=str(
                            incident.pilot_percent_hours_on_type),
                    pilot_total_hours=str(incident.pilot_total_hours),
                    midair=str(int(incident.midair)))
            airport = xml.etree.ElementTree.SubElement(element,
                                                       "airport")
            airport.text = incident.airport.strip()
            narrative = xml.etree.ElementTree.SubElement(element,
                                                         "narrative")
            narrative.text = incident.narrative.strip()
            root.append(element)
        tree = xml.etree.ElementTree.ElementTree(root)
        try:
            tree.write(filename, "UTF-8")
        except EnvironmentError as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        return True


    def import_xml_etree(self, filename):
        try:
            tree = xml.etree.ElementTree.parse(filename)
        except (EnvironmentError,
                xml.parsers.expat.ExpatError) as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False

        self.clear()
        for element in tree.findall("incident"):
            try:
                data = {}
                for attribute in ("report_id", "date", "aircraft_id",
                        "aircraft_type",
                        "pilot_percent_hours_on_type",
                        "pilot_total_hours", "midair"):
                    data[attribute] = element.get(attribute)
                data["date"] = datetime.datetime.strptime(
                                    data["date"], "%Y-%m-%d").date()
                data["pilot_percent_hours_on_type"] = (
                        float(data["pilot_percent_hours_on_type"]))
                data["pilot_total_hours"] = int(
                        data["pilot_total_hours"])
                data["midair"] = bool(int(data["midair"]))
                data["airport"] = element.find("airport").text.strip()
                narrative = element.find("narrative").text
                data["narrative"] = (narrative.strip()
                                     if narrative is not None else "")
                incident = Incident(**data)
                self[incident.report_id] = incident
            except (ValueError, LookupError, IncidentError) as err:
                print("{0}: import error: {1}".format(
                    os.path.basename(sys.argv[0]), err))
                return False
        return True


    def export_xml_manual(self, filename):
        fh = None
        try:
            fh = open(filename, "w", encoding="utf8")
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fh.write("<incidents>\n")
            for incident in self.values():
                fh.write('<incident report_id={report_id} '
                         'date="{0.date!s}" '
                         'aircraft_id={aircraft_id} '
                         'aircraft_type={aircraft_type} '
                         'pilot_percent_hours_on_type='
                         '"{0.pilot_percent_hours_on_type}" '
                         'pilot_total_hours="{0.pilot_total_hours}" '
                         'midair="{0.midair:d}">\n'
                         '<airport>{airport}</airport>\n'
                         '<narrative>\n{narrative}\n</narrative>\n'
                         '</incident>\n'.format(incident,
                    report_id=xml.sax.saxutils.quoteattr(
                                        incident.report_id),
                    aircraft_id=xml.sax.saxutils.quoteattr(
                                        incident.aircraft_id),
                    aircraft_type=xml.sax.saxutils.quoteattr(
                                        incident.aircraft_type),
                    airport=xml.sax.saxutils.escape(incident.airport),
                    narrative="\n".join(textwrap.wrap(
                            xml.sax.saxutils.escape(
                                incident.narrative.strip()), 70))))
            fh.write("</incidents>\n")
            return True
        except EnvironmentError as err:
            print("{0}: export error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def export_text(self, filename):
        wrapper = textwrap.TextWrapper(initial_indent="    ",
                                       subsequent_indent="    ")
        fh = None
        try:
            fh = open(filename, "w", encoding="utf8")
            for incident in self.values():
                narrative = "\n".join(wrapper.wrap(
                                   incident.narrative.strip()))
                fh.write("[{0.report_id}]\n"
                         "date={0.date!s}\n"
                         "aircraft_id={0.aircraft_id}\n"
                         "aircraft_type={0.aircraft_type}\n"
                         "airport={airport}\n"
                         "pilot_percent_hours_on_type="
                         "{0.pilot_percent_hours_on_type}\n"
                         "pilot_total_hours={0.pilot_total_hours}\n"
                         "midair={0.midair:d}\n"
                         ".NARRATIVE_START.\n{narrative}\n"
                         ".NARRATIVE_END.\n\n".format(incident,
                    airport=incident.airport.strip(),
                    narrative=narrative))
            return True
        except EnvironmentError as err:
            print("{0}: export error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def import_text_manual(self, filename):
        fh = None
        try:
            fh = open(filename, encoding="utf8")
            self.clear()
            data = {}
            narrative = None
            for lino, line in enumerate(fh, start=1):
                line = line.rstrip()
                if not line and narrative is None:
                    continue
                if narrative is not None:
                    if line == ".NARRATIVE_END.":
                        data["narrative"] = textwrap.dedent(
                                                    narrative).strip()
                        if len(data) != 9:
                            raise IncidentError("missing data on "
                                            "line {0}".format(lino))
                        incident = Incident(**data)
                        self[incident.report_id] = incident
                        data = {}
                        narrative = None
                    else:
                        narrative += line + "\n"
                elif (not data and line[0] == "["
                               and line[-1] == "]"):
                    data["report_id"] = line[1:-1]
                elif "=" in line:
                    key, value = line.split("=", 1)
                    if key == "date":
                        data[key] = datetime.datetime.strptime(value,
                                                    "%Y-%m-%d").date()
                    elif key == "pilot_percent_hours_on_type":
                        data[key] = float(value)
                    elif key == "pilot_total_hours":
                        data[key] = int(value)
                    elif key == "midair":
                        data[key] = bool(int(value))
                    else:
                        data[key] = value
                elif line == ".NARRATIVE_START.":
                    narrative = ""
                else:
                    raise KeyError("parsing error on line {0}".format(
                                   lino))
            return True
        except (EnvironmentError, ValueError, KeyError,
                IncidentError) as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def import_text_regex(self, filename):
        incident_re = re.compile(
                        r"\[(?P<id>[^]]+)\](?P<keyvalues>.+?)"
                        r"^\.NARRATIVE_START\.$(?P<narrative>.*?)"
                        r"^\.NARRATIVE_END\.$",
                        re.DOTALL|re.MULTILINE)
        key_value_re = re.compile(r"^\s*(?P<key>[^=]+?)\s*=\s*"
                                  r"(?P<value>.+?)\s*$", re.MULTILINE)
        fh = None
        try:
            fh = open(filename, encoding="utf8")
            self.clear()
            for incident_match in incident_re.finditer(fh.read()):
                data = {}
                data["report_id"] = incident_match.group("id")
                data["narrative"] = textwrap.dedent(
                            incident_match.group("narrative")).strip()
                keyvalues = incident_match.group("keyvalues")
                for match in key_value_re.finditer(keyvalues):
                    data[match.group("key")] = match.group("value")
                data["date"] = datetime.datetime.strptime(
                                    data["date"], "%Y-%m-%d").date()
                data["pilot_percent_hours_on_type"] = (
                        float(data["pilot_percent_hours_on_type"]))
                data["pilot_total_hours"] = int(
                        data["pilot_total_hours"])
                data["midair"] = bool(int(data["midair"]))
                if len(data) != 9:
                    raise IncidentError("missing data")
                incident = Incident(**data)
                self[incident.report_id] = incident
            return True
        except (EnvironmentError, LookupError, ValueError,
                IncidentError) as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def export_binary(self, filename, compress=False):

        def pack_string(string):
            data = string.encode("utf8")
            format = "<H{0}s".format(len(data))
            return struct.pack(format, len(data), data)

        if USE_RESTRICTIVE_P_FORMAT:
            def pack_string(string):
                data = string.encode("utf8")
                format = "<{0}p".format(len(data))
                return struct.pack(format, data)

        fh = None
        try:
            if compress:
                fh = gzip.open(filename, "wb")
            else:
                fh = open(filename, "wb")
            fh.write(MAGIC)
            fh.write(FORMAT_VERSION)
            for incident in self.values():
                data = bytearray()
                data.extend(pack_string(incident.report_id))
                data.extend(pack_string(incident.airport))
                data.extend(pack_string(incident.aircraft_id))
                data.extend(pack_string(incident.aircraft_type))
                data.extend(pack_string(incident.narrative.strip()))
                data.extend(NumbersStruct.pack(
                                incident.date.toordinal(),
                                incident.pilot_percent_hours_on_type,
                                incident.pilot_total_hours,
                                incident.midair))
                fh.write(data)
            return True
        except EnvironmentError as err:
            print("{0}: export error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def import_binary(self, filename):

        def unpack_string(fh, eof_is_error=True):
            uint16 = struct.Struct("<H")
            length_data = fh.read(uint16.size)
            if not length_data:
                if eof_is_error:
                    raise ValueError("missing or corrupt string size")
                return None
            length = uint16.unpack(length_data)[0]
            if length == 0:
                return ""
            data = fh.read(length)
            if not data or len(data) != length:
                raise ValueError("missing or corrupt string")
            format = "<{0}s".format(length)
            return struct.unpack(format, data)[0].decode("utf8")
        
        if USE_RESTRICTIVE_P_FORMAT:
            def unpack_string(fh, eof_is_error=True):
                length_data = fh.read(1)
                if not length_data:
                    if eof_is_error:
                        raise ValueError("missing or corrupt string size")
                    return None
                length = int(struct.unpack("<B", length_data)[0])
                if length == 0:
                    return ""
                data = fh.read(length)
                if not data or len(data) != length:
                    raise ValueError("missing or corrupt string")
                format = "<{0}p".format(length)
                return struct.unpack(format, data)[0].decode("utf8")

        fh = None
        try:
            fh = open(filename, "rb")
            magic = fh.read(len(GZIP_MAGIC))
            if magic == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(filename, "rb")
            else:
                fh.seek(0)
            magic = fh.read(len(MAGIC))
            if magic != MAGIC:
                raise ValueError("invalid .aib file format")
            version = fh.read(len(FORMAT_VERSION))
            if version > FORMAT_VERSION:
                raise ValueError("unrecognized .aib file version")
            self.clear()
            while True:
                report_id = unpack_string(fh, False)
                if report_id is None:
                    break
                data = {}
                data["report_id"] = report_id
                for name in ("airport", "aircraft_id",
                             "aircraft_type", "narrative"):
                    data[name] = unpack_string(fh)
                other_data = fh.read(NumbersStruct.size)
                numbers = NumbersStruct.unpack(other_data)
                data["date"] = datetime.date.fromordinal(numbers[0])
                data["pilot_percent_hours_on_type"] = numbers[1]
                data["pilot_total_hours"] = numbers[2]
                data["midair"] = numbers[3]
                incident = Incident(**data)
                self[incident.report_id] = incident
            return True
        except (EnvironmentError, ValueError, IndexError,
                IncidentError) as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def export_pickle(self, filename, compress=False):
        fh = None
        try:
            if compress:
                fh = gzip.open(filename, "wb")
            else:
                fh = open(filename, "wb")
            pickle.dump(self, fh, pickle.HIGHEST_PROTOCOL)
            return True
        except (EnvironmentError, pickle.PicklingError) as err:
            print("{0}: export error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def import_pickle(self, filename):
        fh = None
        try:
            fh = open(filename, "rb")
            magic = fh.read(len(GZIP_MAGIC))
            if magic == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(filename, "rb")
            else:
                fh.seek(0)
            self.clear()
            self.update(pickle.load(fh))
            return True
        except (EnvironmentError, pickle.UnpicklingError) as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


    def import_xml_sax(self, filename):
        fh = None
        try:
            handler = IncidentSaxHandler(self)
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            parser.parse(filename)
            return True
        except (EnvironmentError, ValueError, IncidentError,
                xml.sax.SAXParseException) as err:
            print("{0}: import error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False


    def export_html(self, filename):
        fh = None
        try:
            fh = open(filename, "w", encoding="utf8")
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
                     '1.0 Strict//EN" '
                     '"http://www.w3.org/TR/xhtml1/DTD/'
                     'xhtml1-strict.dtd">\n'
                     '<html xmlns="http://www.w3.org/1999/xhtml" '
                     'lang="en" xml:lang="en">\n'
                     '<head><title>{0}</title>\n'
                     '<meta equiv="content-type" '
                     'content="text/html; charset=utf-8" />\n'
                     '</head><body>\n<h3>{0}</h3>\n'
                     '<table border="1">\n'
                     '<tr><th>Count</th><th>Report ID</th>'
                     '<th>Date</th><th>Aircraft</th>'
                     '<th>Type</th><th>Airport</th>'
                     '<th>Pilot Hours/Type</th><th>Pilot Hours</th>'
                     '<th>Midair</th><th>Narrative (Words)</th>'
                     '</tr>\n'.format("Aircraft Incidents Summary"))
            for i, incident in enumerate(self.values()):
                airport = xml.sax.saxutils.escape(
                                            incident.airport.strip())
                hours = "{0:n}".format(incident.pilot_total_hours)
                midair= "Yes" if incident.midair else "No"
                words = len(incident.narrative.split())
                fh.write('<tr><td align="right">{count}</td>\n'
                         '<td>{0.report_id}</td><td>{0.date!s}</td>'
                         '<td>{0.aircraft_id}</td>'
                         '<td>{0.aircraft_type}</td>'
                         '<td>{airport}</td>'
                         '<td align="right">'
                         '{0.pilot_percent_hours_on_type:.1f} %</td>'
                         '<td align="right">{hours} hours</td>'
                         '<td align="center">{midair}</td>'
                         '<td align="right">{words} words</td>'
                         '</tr>\n'.format(incident, count=i + 1,
                                          **locals()))
            fh.write("</table>\n</body>\n</html>\n")
            return True
        except EnvironmentError as err:
            print("{0}: export error: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()


def parse_options():
    reader_list = "dom d etree e sax s regex r manual m".split()
    writer_list = "dom d etree e manual m".split()
    parser = optparse.OptionParser(usage="""\
usage: %prog [options] infile outfile

Reads aircraft incident data from infile and writes the data to
outfile. The data formats used depend on the file extensions:
.aix is XML, .ait is text (UTF-8 encoding), .aib is binary,
.aip is pickle, and .html is HTML (only allowed for the outfile).
All formats are platform-independent.""")
    parser.add_option("-f", "--force", dest="force",
            action="store_true", default=False,
            help=("write the outfile even if it exists "
                  "[default: off]"))
    parser.add_option("-v", "--verbose", dest="verbose",
            action="store_true", default=False,
            help=("report results [default: off]"))
    parser.add_option("-r", "--reader", dest="reader",
            choices=reader_list,
            help=("reader (XML): 'dom', 'd', 'etree', 'e', "
                  "'sax', 's' reader (text): 'manual', 'm', "
                  "'regex', 'r' [default: etree for XML, "
                  "manual for text]"))
    parser.add_option("-w", "--writer", dest="writer",
            choices=writer_list,
            help=("writer (XML): 'dom', 'd', 'etree', 'e', "
                  "'manual', 'm' [default: manual]"))
    parser.add_option("-z", "--compress", dest="compress",
            action="store_true", default=False,
            help=("compress .aib/.aip outfile [default: off]"))
    parser.add_option("-t", "--test", dest="test",
            action="store_true",
            help=("execute doctests and exit (use with -v for "
                  "verbose)"))
    opts, args = parser.parse_args()

    if opts.test:
        test(opts.verbose)
    if len(args) == 0:
        parser.error("no files have been specified")
    if len(args) != 2:
        parser.error("exactly two files must been specified")
    if args[0] == args[1]:
        parser.error("the two specified files must be different")
    source, target = args

    if not opts.force and os.path.exists(target):
        parser.error("cannot overwrite unless --force is used")
    if opts.compress and target[-1] not in "pb":
        parser.error("can only compress .aib and .aip files")

    valid_extensions = {".aix", ".ait", ".aib", ".aip"}
    extension = os.path.splitext(source)[1].lower()
    if extension not in valid_extensions:
        parser.error("unrecognized infile extension: '{0}'".format(
                     extension))
    if extension == ".aix" and not opts.reader:
        opts.reader = "etree"
    elif extension == ".ait" and not opts.reader:
        opts.reader = "manual"
    text_readers = frozenset({"manual", "m", "regex", "r"})
    if ((extension == ".aix" and opts.reader in text_readers) or
        (extension == ".ait" and opts.reader not in text_readers) or
        (extension not in {".aix", ".ait"} and opts.reader)):
        parser.error("invalid reader for infile")

    valid_extensions |= {".htm", ".html"}
    extension = os.path.splitext(target)[1].lower()
    if extension not in valid_extensions:
        parser.error("unrecognized outfile extension: '{0}'".format(
                     extension))
    if extension == ".aix" and not opts.writer:
        opts.writer = "manual"
    readers = dict(d="dom", e="etree", s="sax", m="manual", r="regex")
    if opts.reader in readers:
        opts.reader = readers[opts.reader]
    writers = dict(d="dom", e="etree", m="manual")
    if opts.writer in writers:
        opts.writer = writers[opts.writer]
    if ((extension == ".aix" and opts.writer not in
         set(writers.keys()) | set(writers.values())) or
        (extension != ".aix" and opts.writer)):
        parser.error("invalid writer for outfile")

    return opts, source, target


def test(verbose):
    import doctest
    doctest.testmod(verbose=verbose)
    sys.exit()


def main():
    opts, source, target = parse_options()
    aircraft_incidents = IncidentCollection()
    if aircraft_incidents.import_(source, opts.reader):
        if opts.verbose:
            print("imported {0} record{s} from '{1}'".format(
                  len(aircraft_incidents), source,
                  s = "s" if len(aircraft_incidents) != 1 else ""))
        if aircraft_incidents.export(target, opts.writer,
                                     opts.compress):
            if opts.verbose:
                print("exported {0} record{s} to   '{1}'".format(
                    len(aircraft_incidents), target,
                    s = "s" if len(aircraft_incidents) != 1 else ""))


main()

