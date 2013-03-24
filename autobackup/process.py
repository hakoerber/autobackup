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
Module to execute a command on a certain host. When you want to execute it on
the localhost, it behaves like a wrapper around then subprocess.Popen()
constructor to spawn a new process. If you want to execute a command on a remote
machine, the module will built up a commection to that host through the
connection class specified in _CONNECTION_CLASS and delegates the execution to
that class.

It also contains some functions to execute frequently needed processes, like
creating/deleting a directory or testing whether a file exists.
"""

import getpass
import os
import pwd
import subprocess

import networkconnection


_CONNECTION_CLASS = networkconnection.SSHNetworkConnection
_CONNECTION_PORT = 22
_CONNECTION_TIMEOUT = 10 * 1000
_CONNECTION_REMOTE_SHELL = "/bin/bash"
_COMMAND_TIMEOUT = 10 * 1000
_connections = []


def execute(host, args, user, remote_user=None):
    """
    Executes a command on a specific as a user. Will connect to the host and
    maintain the connection if the host is remote until you explicitly
    disconnect to host with disconnect(). If the host is the localhost, the
    command will be executed locally.
    :param host: The host on which the command is to be executed.
    :type host: Host instance
    :param args: A list of arguments of the command.
    :type args: list
    :param user: The user as whom to run the command on the local machine or
    the local connection command if executing to a remote host.
    :type user: string
    :param remote_user: The username to use when connecting to a remote host.
    If none is given, the same user as the local one will be used. If the
    command is executed on the localhost, the parameter will be ignored.
    :type remote_user: string
    :returns: A tuple which contains the exit code of the command, the whole
    output to stdout and the whole output to stderr as strings.
    :rtype: tuple
    :raises: TimeoutError if connecting to or executing a command on a remote
    host and a timeout occurs.
    :raises: ConnectionRefusedError connecting to a remote host fails.
    """
    if not host.is_localhost():
        # Connect to a remote host
        if remote_user is None:
            remote_user = user
        # see if connection already exists
        connection = None
        for conn in _connections:
            if (conn.host == host and conn.local_user == user and
                    conn.remote_user == remote_user):
                connection = conn
                break
        if not connection:
            connection = _CONNECTION_CLASS(host=host,
                                           local_user=user,
                                           remote_user=remote_user,
                                           port=_CONNECTION_PORT)

        if not connection.is_connected():
            try:
                connection.connect(timeout=_CONNECTION_TIMEOUT,
                                   remote_shell=_CONNECTION_REMOTE_SHELL)
            except (TimeoutError, ConnectionRefusedError):
                raise

            try:
                (exit_code, stdoutdata, stderrdata) = connection.execute(
                    command=args, timeout=_COMMAND_TIMEOUT)
            except TimeoutError:
                raise

            return (exit_code, stdoutdata, stderrdata)
    else:
        # Just execute the command locally.

        # used to change the user in the Popen constructor below
        if user != getpass.getuser():
            # getpwnam returns a tuple: (name, passwd, uid, gid ...)
            def preexec():
                uid = pwd.getpwnam(user)[2]
                os.setuid(uid)
        else:
            preexec = None

        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   bufsize=-1,
                                   preexec_fn=preexec)
        (stdoutdata, stderrdata) = process.communicate()
        return (process.returncode, stdoutdata, stderrdata)


def disconnect(host, user=None, remote_user=None):
    """
    Terminates all connections to a host as a specific user/remote_user. If no
    user or remote_user is given, all connection to the host regardless of the
    respective user/remote_user will terminated.
    :param host: The host to terminate connections to.
    :type host: Host instance
    :param user: The user who own the connection process.
    :type user: string
    :param remote_user: The user who was given when connecting to the remote.
    :type remote_user: string
    :returns: True if any connections were disconnected, False otherwise.
    :rtype: bool
    host.
    """
    any_disconnects = False
    for conn in _connections:
        if conn.host == host:
            if ((user is None or user == conn.local_user) and
                    (remote_user is None or remote_user == conn.remote_user)):
                conn.disconnect()
                _connections.remove(conn)
                any_disconnects = True
    return any_disconnects


def disconnect_all():
    """
    Disconnects all connections to all hosts.
    """
    for conn in _connections:
        conn.disconnect()


def execute_success(host, args, user, remote_user=None):
    """
    Executes a command and returns its output to stdout. If the command returns
    a failure status (!= 0), raises a ProcessError.
    :param host: The host on which the command is to be executed.
    :type host: Host instance
    :param args: A list of arguments of the command.
    :type args: list
    :param user: The user as whom to run the command on the local machine or
    the local connection command if executing to a remote host.
    :type user: string
    :param remote_user: The username to use when connecting to a remote host.
    If none is given, the same user as the local one will be used. If the
    command is executed on the localhost, the parameter will be ignored.
    :type remote_user: string
    :returns: A tuple which contains the exit code of the command, the whole
    output to stdout and the whole output to stderr as strings.
    :rtype: tuple
    :raises: TimeoutError if connecting to or executing a command on a remote
    host and a timeout occurs.
    :raises: ConnectionRefusedError connecting to a remote host fails.
    :raises: ProcessError if the command exits with a failure status.
    """
    (exit_code, stdoutdata, stderrdata) = execute(host, args, user, remote_user)
    if exit_code != 0:
        raise ProcessError(exit_code, stdoutdata, stderrdata)
    return stdoutdata


def is_connected(host, user=None, remote_user=None):
    """
    Determines whether there is an active connection to a host as a specific
    user/remote_user. If no user/remote_user is given, determines whether there
    is any connection to that host, regardless of the respective
    user/remote_user.
    :param host: The host to poll.
    :type host: Host instance
    :param user: The user who owns the connection process.
    :type user: string
    :param remote_user: The user that was specified when connecting to the host.
    :type remote_user: string
    :returns: True if there is an active connection to the host as the specified
    user, False otherwise.
    :rtype: bool
    """
    for conn in _connections:
        if conn.host == host:
            if ((user is None or user == conn.local_user) and
                    (remote_user is None or remote_user == conn.remote_user)):
                return True
    return False


class FileTypes(object):
    """
    An enumeration containing all file types usable for func_file_exists().
    """
    ANY = "e"
    BLOCK_SPECIAL = "b"
    DIRECTORY = "d"
    REGULAR = "f"


def func_file_exists(host, user, path, filetype, remote_user=None):
    """
    Function that tests whether a file exists and is or the given type.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: The user as whom to run the command on the local machine or
    the local connection command if executing to a remote host.
    :type user: string
    :param path: The path of the file.
    :type path: string
    :param filetype: The type of the file.
    :type filetype: FileTypes enum member
    :param remote_user: The username to use when connecting to a remote host.
    If none is given, the same user as the local one will be used. If the
    command is executed on the localhost, the parameter will be ignored.
    :type remote_user: string
    :returns: True if the file file exists, false otherwise.
    :rtype: bool
    :raises: TimeoutError if connecting to or executing a command on a remote
    host and a timeout occurs.
    :raises: ConnectionRefusedError connecting to a remote host fails.
    """
    args = ["test", "-{}".format(filetype), path]
    (exit_code, _, _) = execute(host, args, user, remote_user)
    return exit_code == 0


def func_directory_empty(host, user, path, remote_user=None):
    """
    Function that tests whether a given directory is empty.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: The user as whom to run the command on the local machine or
    the local connection command if executing to a remote host.
    :type user: string
    :param path: The path of the direost,
    :type path: string
    :param remote_user: The username to use when connecting to a remote host.
    If none is given, the same user as the local one will be used. If the
    command is executed on the localhost, the parameter will be ignored.
    :type remote_user: string
    :returns: True if the directory is empty, false otherwise.
    :rtype: bool
    :raises: TimeoutError if connecting to or executing a command on a remote
    host and a timeout occurs.
    :raises: ConnectionRefusedError connecting to a remote host fails.
    :raises: ProcessError if reading the directory failed.
    """
    return len(func_directory_get_files(host, user, path, remote_user)) == 0


def func_directory_get_files(host, user, path, remote_user=None):
    """
    Function that returns all elements of a directory.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: The user as whom to run the command on the local machine or
    the local connection command if executing to a remote host.
    :type user: string
    :param path: The path of the directory.
    :type path: string
    :param remote_user: The username to use when connecting to a remote host.
    If none is given, the same user as the local one will be used. If the
    command is executed on the localhost, the parameter will be ignored.
    :type remote_user: string
    :returns: A tuple with the names of all files and subdirectory in the
    directory. Directories can be identified by a succeeding slash.
    :rtype: tuple
    :raises: TimeoutError if connecting to or executing a command on a remote
    host and a timeout occurs.
    :raises: ConnectionRefusedError connecting to a remote host fails.
    :raises: ProcessError if reading the directory failed.
    """
    args = ["ls", "-A", "-1", "-p", path]
    (exit_code, stdoutdata, stderrdata) = execute(host, args, user, remote_user)
    if exit_code != 0:
        raise ProcessError(exit_code, stdoutdata, stderrdata)
    # TODO: pylint thinks that stdoutdata may be a list instead of a string,
    # examine that lazy.
    stdoutdata = str(stdoutdata)
    dirs = stdoutdata.split('\n')
    if dirs[0] == "":
        dirs = []
    return dirs


def func_create_directory(host, user, path, create_parents, remote_user=None):
    """
    Function to create a directory.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: The user as whom to run the command on the local machine or
    the local connection command if executing to a remote host.
    :type user: string
    :param path: The path of the new directory.
    :type path: string
    :param remote_user: The username to use when connecting to a remote host.
    If none is given, the same user as the local one will be used. If the
    command is executed on the localhost, the parameter will be ignored.
    :type remote_user: string
    :returns: A tuple with the exit code, the stdout data and stderr data
    :rtype: tuple
    :raises: TimeoutError if connecting to or executing a command on a remote
    host and a timeout occurs.
    :raises: ConnectionRefusedError connecting to a remote host fails.
    :raises: ProcessError if creating the directory failed.
    """
    args = ["mkdir"]
    if create_parents:
        args.append("-p")
    args.append(path)
    execute_success(host, args, user, remote_user)


def func_remove_directory(host, user, path, recursive, remote_user=None):
    """
    Function to remove a directory.
    :param host: Host on which to execute the command.
    :type host: Host instance
    :param user: The user as whom to run the command on the local machine or
    the local connection command if executing to a remote host.
    :type user: string
    :param path: The path of the directory that shall be deleted.
    :type path: string
    :param recursive: Determines whether to delete the directory and all its
    content recursively.
    :type recursive: bool
    :param remote_user: The username to use when connecting to a remote host.
    If none is given, the same user as the local one will be used. If the
    command is executed on the localhost, the parameter will be ignored.
    :type remote_user: string
    :returns: A tuple with the exit code, the stdout data and stderr data.
    :rtype: tuple
    """
    if recursive:
        args = ["rm", "--recursive"]
    else:
        args = ["rmdir", path]
    return execute_success(host, args, user, remote_user)


class ProcessError(Exception):
    """Exception raised when a process of this module fails."""
    def __init__(self, exit_code, stdoutdata, stderrdata):
        Exception.__init__(self)
        self.exit_code = exit_code
        self.stdoutdata = stdoutdata
        self.stderrdata = stderrdata
