# -*- encoding: utf-8 -*-
# Copyright (c) 2013 Hannes Körber
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

""" Module to identify with hosts in a network."""

import socket


def get_localhost():
    """Returns a host representing the localhost."""
    return Host(ip="127.0.0.1")


class Host(object):
    """A host in a network, identified by his hostname or an ip address"""

    def __init__(self, ip=None, hostname=None):
        if ip is None and hostname is None:
            raise ValueError("Either ip or hostname must be specified.")
        try:
            if ip is not None:
                self._ip = ip
            else:
                self._ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            raise ValueError("Unknown hostname.")

    def is_localhost(self):
        """
        Determines whether the host is the localhost.
        :returns: True if this host is the localhost, False otherwise.
        :rtype: bool
        """
        return self.ip.startswith("127.")

    def get_real_ip(self):
        """
        Returns the ip useable by all hosts in the network, not the localhost
        ip for the local host.
        :returns: The ip of this host as seen by other hosts in the network.
        :rtype: bool
        """
        if not self.is_localhost():
            return self.ip
        else:
            raise NotImplementedError()

    def _get_ip(self):
        return self._ip
    ip = property(_get_ip)

    # Needs to be overloaded, as a simple comparison of the ips is not
    # sufficient. All ips in 127.*.*.* refer to the localhost, so for instance
    # 127.0.0.1 and 27.42.13.37 are the same machine.
    def __eq__(self, other):
        if self.is_localhost() and other.is_localhost():
            return True
        return self.ip == other.ip

    def __ne__(self, other):
        return not self.__eq__(other)
