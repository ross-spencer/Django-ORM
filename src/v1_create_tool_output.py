# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import lxml.etree as etree
import os

import metsrw

from fs_entries_tree import FSEntriesTree
from main.models import SIP

import namespaces as ns

# from custom_handlers import get_script_logger
import logging

logger = logging


def remove_logical_structmap(mets):
    """Remove the logical structmap

    Remove logical structmap is output by default from mets-reader-
    writer, but it isn't a default argument in Archivematica.
    """
    mets_root = mets.serialize()
    struct_map = mets_root.find(
        ".//mets:structMap[@TYPE='logical']", namespaces=ns.NSMAP
    )
    mets_root.remove(struct_map)
    return mets_root


def create_tool_mets(job, opts):
    """Create tool mets

    Outputs a structmap, fileSec, and PREMIS objects containing largely
    just the PREMIS object characteristics extension which holds the
    tool output for objects from Archivematica's processing via the FPR.
    """

    # Based entirely on create_transfer_METS from Cole...
    # https://git.io/JJK8a

    METS_DIR = "mets"
    tool_output_filename = "tool_output-{}.xml"

    # WELLCOME TODO: We can convert these variables to camel_case which
    # would be a start towards refactoring this legacy piece.

    base_directory_path = opts.baseDirectoryPath
    base_directory_path_string = "%%%s%%" % (opts.baseDirectoryPathString)
    aip_uuid = opts.fileGroupIdentifier
    file_group_type = opts.fileGroupType
    include_amd_sec = opts.amdSec
    create_normative_structmap = opts.createNormativeStructmap

    # WELLCOME TODO: Delete this stuff... it's just garnish to help
    # refactoring, i.e. what is it all??
    print("____________")
    print("")
    print("1. dir path", base_directory_path)
    print("2. path string", base_directory_path_string)
    print("3. aip uuid", aip_uuid)
    print("4. file grp type", file_group_type)
    print("5. inc amdsec", include_amd_sec)
    print("6. norm structmap", create_normative_structmap)
    print("")
    print("‾‾‾‾‾‾‾‾‾‾‾‾")

    mets_tool_path = os.path.join(METS_DIR, tool_output_filename.format(aip_uuid))

    # Wellcome TODO: this is way too finicky...
    base_directory_path = os.path.join(base_directory_path, "")
    objects_directory_path = os.path.join(base_directory_path, "objects")

    objects_directory_path = base_directory_path

    mets = metsrw.METSDocument()
    mets.objid = str(aip_uuid)

    try:
        aip = SIP.objects.get(uuid=aip_uuid)
    except SIP.DoesNotExist:
        logger.info("No record in database for transfer: %s", aip_uuid)
        raise

    fsentry_tree = FSEntriesTree(
        objects_directory_path, base_directory_path_string, aip, structure_only=False
    )
    fsentry_tree.scan()

    mets.append_file(fsentry_tree.root_node)

    # WELLCOME TODO: This is very much a hack until we can solve:
    # https://github.com/archivematica/Issues/issues/1272
    if create_normative_structmap:
        mets = remove_logical_structmap(mets)

    mets = etree.ElementTree(mets)
    mets.write(
        mets_tool_path, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    )
