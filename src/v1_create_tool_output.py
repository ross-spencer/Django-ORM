# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import lxml.etree as etree

from main.models import (
    # MCP table, e.g. select * from main_fpcommandoutput.
    FPCommandOutput,
)

import namespaces as ns


def create_premis_object_characteristics_extensions(fileUUID):
    elements = []
    objectCharacteristicsExtension = etree.Element(
        ns.premisBNS + "objectCharacteristicsExtension"
    )
    parser = etree.XMLParser(remove_blank_text=True)
    documents = FPCommandOutput.objects.filter(
        file_id=fileUUID,
        rule__purpose__in=["characterization", "default_characterization"],
    ).values_list("content")
    for (document,) in documents:
        # This needs to be converted into a byte string because lxml doesn't
        # accept XML documents in Unicode strings if the document contains an
        # encoding declaration.
        output = etree.XML(document.encode("utf-8"), parser)
        objectCharacteristicsExtension.append(output)

    if len(objectCharacteristicsExtension):
        elements.append(objectCharacteristicsExtension)
    return elements
