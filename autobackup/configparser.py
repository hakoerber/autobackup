# -*- encoding: utf-8 -*-
# Copyright (c) 2013 Hannes Körber <hannes.koerber@gmail.com>
#
# This file is part of autobackup.
#
# autobackup is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# autobackup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module helps reading configuration files of a specific format.
This format is similar to XML, but not as flexible or powerful.
"""

import os
import xml.etree.ElementTree as etree


class Parser(object):
    """Abstract base class for all parsers in this module."""
    def __init__(self, path):
        pass

    def read(self):
        raise NotImplementedError()

    def parse(self):
        raise NotImplementedError()

    def get_structure(self):
        raise NotImplementedError()


class XMLParser(Parser):
    """
    Parses an .xml-file. Parsing is quite easy, as we can be sure that the file
    is valid, because it had to be validated against an xsd-file.

    The resulting structure is as follows:
    structure: [hosts, devices, backups]
    hosts: name -> (ip, hostname), one is of course None
    devices: name -> (uuid, filesystem, mountpoint)
    backups: list of backup
    backup: name -> (source[], destination, tag[])
    tag: name -> (cron, max_age, max_count)
    """
    def __init__(self, path):
        """
        :param path: The path to the configuration file.
        :type path: string
        """
        Parser.__init__(self, path)
        self.path = path
        self.structure = {}
        self.text = None

    def read(self):
        """
        Reads the file into memory.
        :raises: IOError if the file was not found.
        """
        if not os.path.isfile(self.path):
            raise IOError("File not found.")
        self.text = open(self.path).read()

    def parse(self):
        """
        Parses the file. Automatically calls read() if necessary.
        """
        if self.text is None:
            self.read()
        root = etree.fromstring(self.text)
        hosts = {}
        devices = {}
        backups = []
        for host in root.find("hosts"):
            name = host.attrib["name"]
            ip = host.findtext("ip")
            hostname = host.findtext("hostname")
            hosts[name] = (ip, hostname)
        for device in root.find("devices"):
            name = device.attrib["name"]
            uuid = device.findtext("uuid")
            filesystem = device.findtext("filesystem")
            mountpoint = device.findtext("mountpoint")
            devices[name] = (uuid, filesystem, mountpoint)
        for backup in root.find("backups"):
            sources = []
            for source in backup.findall("source"):
                sources.append(source.text)
            destination = backup.find("destination").text
            tags = []
            for tag in backup.findall("tag"):
                name = tag.attrib["name"]
                cron = tag.findtext("cron")
                max_age = tag.findtext("max_age")
                max_count = tag.findtext("max_count")
                tags.append({name: (cron, max_age, max_count)})
            backups.append((sources, destination, tags))
        self.structure = [hosts, devices, backups]
        return self.structure


class ParseError(Exception):
    """
    This exception is raised when the parsing of the configuration file fails.
    """
    def __init__(self, line_number, line, message):
        """
        :param line_number: The line number where the error occured.
        :type line_number: int
        :param line: The text of the line where the error occured.
        :type line: string
        :param message: The error message.
        :type message: string
        """
        super(ParseError, self).__init__(message)
        self.line_number = line_number
        self.line = line
        self.message = message


class CfgParser(Parser):

    _COMMENT_CHARS = ('#', ';')
    _SECTION_PAIRS = [('[', ']')]
    _ELEMENT_PAIRS = [('<', '>')]
    _KEY_VALUE_SEPARATORS = ('=', ':')

    def __init__(self, path,
                 comment_chars=_COMMENT_CHARS,
                 section_pairs=_SECTION_PAIRS,
                 element_pairs=_ELEMENT_PAIRS,
                 key_value_separators=_KEY_VALUE_SEPARATORS,
                 multiple_keys=True):
        raise NotImplementedError("This class if deprecated.")
        Parser.__init__(self, path)
        self.path = path
        self.comment_chars = comment_chars
        self.section_pairs = section_pairs
        self.element_pairs = element_pairs
        self.key_value_separators = key_value_separators
        self.multiple_keys = multiple_keys

        self.text = None
        self.structure = dict()

    def read(self):
        if not os.path.isfile(self.path):
            raise IOError("File not found.")
        self.text = open(self.path).read()

    def parse(self):
        if self.text is None:
            self.read()
        current_section = ""
        current_element = ""
        lineno = 0
        for line in self.text.split('\n'):
            lineno += 1
            line = line.strip()
            for char in self.comment_chars:
                line = line.split(char)[0]
            if not line:
                continue
            if any([(line[0], line[-1]) == pair for pair in self.section_pairs]):
                current_section = line
                self.structure[line] = {}
                continue
            elif any([(line[0], line[-1]) == pair for pair in self.element_pairs]):
                if not current_section:
                    raise ParseError(lineno, line,
                                     "Element without associated section.")
                current_element = line
                self.structure[current_section][current_element] = {}
                continue
            elif any(sep in line for sep in self.key_value_separators):
                if any([line.startswith(sep[0]) for sep in self.key_value_separators]):
                    raise ParseError(lineno, line, "Missing key.")
                if sum([line.count(sub) for sub in self.key_value_separators]) > 1:
                    raise ParseError(lineno, line, "Ambiguous line.")
                if not current_section:
                    raise ParseError(lineno, line,
                                     "Key without associated section.")
                if not current_element or not current_element in self.structure[current_section]:
                    raise ParseError(lineno, line,
                                     "Key without associated element.")
                key, value = line.split(filter(lambda sep: sep in line,
                                               self.key_value_separators)[0])
                if not key.strip():
                    raise ParseError(lineno, line, "Empty key.")
                if key.strip() in  self.structure[current_section][current_element]:
                    if self.multiple_keys:
                        values = self.structure[current_section]\
                            [current_element][key.strip()]
                        if type(values) is str:
                            values = [values]
                        values.append(value.strip())
                        self.structure[current_section][current_element]\
                            [key.strip()] = values
                    else:
                        raise ParseError(lineno, line,
                                         "Found key twice in the same element.")
                else:
                    if not current_element in self.structure[current_section]:
                        raise ParseError(lineno, line,
                                         "Element without associated section")
                    self.structure[current_section][current_element]\
                        [key.strip()] = value.strip()
            else:
                raise ParseError(lineno, line, "Invalid line")
        return self.structure

    def get_structure(self):
        return self.structure
