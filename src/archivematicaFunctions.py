# -*- coding: utf-8 -*-
# This file is part of Archivematica.
#
# Copyright 2010-2013 Artefactual Systems Inc. <http://artefactual.com>
#
# Archivematica is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Archivematica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Archivematica.  If not, see <http://www.gnu.org/licenses/>.

# @package Archivematica
# @subpackage archivematicaCommon
# @author Joseph Perry <joseph@artefactual.com>

"""archivematicaFunctions provides various helper functions across the
different Archivematica modules.
"""
from __future__ import absolute_import, print_function

import collections
import os
import re

import six


def escape(string):
    """Replace non-unicode characters with a replacement character. Use this
    primarily for arbitrary strings (e.g. filenames, paths) that might not
    be valid unicode to begin with.
    """
    if isinstance(string, six.binary_type):
        string = string.decode("utf-8", errors="replace")
    return string


def normalizeNonDcElementName(string):
    """Normalize non-DC CONTENTdm metadata element names to match those used
    in transfer's metadata.csv files.
    """
    # Convert non-alphanumerics to _, remove extra _ from ends of string.
    normalized_string = re.sub(r"\W+", "_", string)
    normalized_string = normalized_string.strip("_")
    # Lower case string.
    normalized_string = normalized_string.lower()
    return normalized_string


def strToUnicode(string, obstinate=False):
    """Convert string to Unicode format."""
    if isinstance(string, six.binary_type):
        try:
            string = string.decode("utf8")
        except UnicodeDecodeError:
            if obstinate:
                # Obstinately get a Unicode instance by replacing
                # indecipherable bytes.
                string = string.decode("utf8", "replace")
            else:
                raise
    return string


def unicodeToStr(string):
    """Convert Unicode to string format."""
    if isinstance(string, six.text_type):
        return six.ensure_str(string, "utf-8")
    return string


def find_metadata_files(sip_path, filename, only_transfers=False):
    """
    Check the SIP and transfer metadata directories for filename.

    Helper function to collect all of a particular metadata file (e.g.
    metadata.csv) in a SIP.

    SIP-level files will be at the end of the list, if they exist.

    :param sip_path: Path of the SIP to check
    :param filename: Name of the metadata file to search for
    :param only_transfers: True if it should only look at Transfer metadata,
                           False if it should look at SIP metadata too.
    :return: List of full paths to instances of filename
    """
    paths = []
    # Check transfer metadata.
    transfers_md_path = os.path.join(sip_path, "objects", "metadata", "transfers")
    try:
        transfers = os.listdir(transfers_md_path)
    except OSError:
        transfers = []
    for transfer in transfers:
        path = os.path.join(transfers_md_path, transfer, filename)
        if os.path.isfile(path):
            paths.append(path)
    # Check the SIP metadata dir.
    if not only_transfers:
        path = os.path.join(sip_path, "objects", "metadata", filename)
        if os.path.isfile(path):
            paths.append(path)
    return paths


class OrderedListsDict(collections.OrderedDict):
    """
    OrderedDict where all keys are lists, and elements are appended
    automatically.
    """

    def __setitem__(self, key, value):
        # When inserting, insert into a list of items with the same key
        try:
            self[key]
        except KeyError:
            super(OrderedListsDict, self).__setitem__(key, [])
        self[key].append(value)
