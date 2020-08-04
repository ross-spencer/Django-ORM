# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import lxml.etree as etree

from main.models import (
    Directory,
    File,
    # MCP table, e.g. select * from main_fpcommandoutput.
    FPCommandOutput,

    SIP,
)

import namespaces as ns


def Xcreate_premis_object_characteristics_extensions(fileUUID):
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


# =============================================================================
# Bad METS....
# =============================================================================

import os
import sys

from django.utils import timezone

from archivematicaFunctions import strToUnicode


class ErrorAccumulator(object):
    def __init__(self):
        self.error_count = 0


class MetsState(object):
    def __init__(
        self, globalAmdSecCounter=0, globalTechMDCounter=0, globalDigiprovMDCounter=0
    ):
        self.globalFileGrps = {}
        self.globalFileGrpsUses = [
            "original",
            "submissionDocumentation",
            "preservation",
            "service",
            "access",
            "license",
            "text/ocr",
            "metadata",
            "derivative",
        ]
        for use in self.globalFileGrpsUses:
            grp = etree.Element(ns.metsBNS + "fileGrp")
            grp.set("USE", use)
            self.globalFileGrps[use] = grp

        # counters
        self.amdSecs = []
        self.dmdSecs = []
        self.globalDmdSecCounter = 0
        self.globalAmdSecCounter = globalAmdSecCounter
        self.globalTechMDCounter = globalTechMDCounter
        self.globalDigiprovMDCounter = globalDigiprovMDCounter
        self.globalRightsMDCounter = 0
        self.fileNameToFileID = {}  # Used for mapping structMaps included with transfer
        self.globalStructMapCounter = 0

        self.trimStructMap = None
        self.trimStructMapObjects = None

        # GROUPID="G1" -> GROUPID="Group-%object's UUID%"
        # group of the object and it's related access, license

        self.CSV_METADATA = {}
        self.error_accumulator = ErrorAccumulator()


def newChild(parent, tag, text=None, tailText=None, sets=None):
    # TODO convert sets to a dict, and use **dict
    sets = sets or []
    child = etree.SubElement(parent, tag)
    child.text = strToUnicode(text)
    if tailText:
        child.tail = strToUnicode(tailText)
    for set_ in sets:
        key, value = set_
        child.set(key, value)
    return child


def createFileSec(
    job,
    directoryPath,
    parentDiv,
    baseDirectoryPath,
    baseDirectoryName,
    fileGroupIdentifier,
    fileGroupType,
    directories,
    state,
    includeAmdSec=True,
):

    """Creates fileSec and structMap entries for files on disk recursively.

    :param directoryPath: Path to recursively traverse and create METS entries for
    :param parentDiv: structMap div to attach created children to
    :param baseDirectoryPath: SIP path
    :param baseDirectoryName: Name of the %var% for the SIP path
    :param fileGroupIdentifier: SIP UUID
    :param fileGroupType: Name of the foreign key field linking to SIP UUID in files.
    :param includeAmdSec: If True, creates amdSecs for the files
    """
    filesInThisDirectory = []
    dspaceMetsDMDID = None
    try:
        directoryContents = sorted(os.listdir(directoryPath))
    except os.error:
        # Directory doesn't exist
        job.pyprint(directoryPath, "doesn't exist", file=sys.stderr)
        return

    # Create the <mets:div> element for the directory that this file is in.
    # If this directory has been assigned a UUID during transfer, retrieve that
    # UUID based on the directory's relative path and document it in its own
    # <mets:dmdSec> element.
    directoryName = os.path.basename(directoryPath)
    relativeDirectoryPath = "%SIPDirectory%" + os.path.join(
        directoryPath.replace(baseDirectoryPath, "", 1), ""
    )
    dir_mdl = directories.get(
        relativeDirectoryPath, directories.get(relativeDirectoryPath.rstrip("/"))
    )
    if dir_mdl:
        pass
    structMapDiv = etree.SubElement(
        parentDiv, ns.metsBNS + "div", TYPE="Directory", LABEL=directoryName
    )

    for item in directoryContents:
        itemdirectoryPath = os.path.join(directoryPath, item)
        if os.path.isdir(itemdirectoryPath):
            createFileSec(
                job,
                itemdirectoryPath,
                structMapDiv,
                baseDirectoryPath,
                baseDirectoryName,
                fileGroupIdentifier,
                fileGroupType,
                directories,
                state,
                includeAmdSec=includeAmdSec,
            )

        elif os.path.isfile(itemdirectoryPath):
            # Setup variables for creating file metadata
            directoryPathSTR = itemdirectoryPath.replace(
                baseDirectoryPath, baseDirectoryName, 1
            )

            kwargs = {
                "removedtime__isnull": True,
                fileGroupType: fileGroupIdentifier,
                "currentlocation": directoryPathSTR,
            }
            try:
                f = File.objects.get(**kwargs)
            except File.DoesNotExist:
                err = 'No uuid for file: "{}"'.format(directoryPathSTR)
                job.pyprint(err, file=sys.stderr)
                state.error_accumulator.error_count += 1
                continue

            use = f.filegrpuse
            label = f.label
            typeOfTransfer = f.transfer.type if f.transfer else None

            directoryPathSTR = itemdirectoryPath.replace(baseDirectoryPath, "", 1)

            # Special TRIM processing
            if typeOfTransfer == "TRIM" and state.trimStructMap is None:
                pass

            # Create <div TYPE="Item"> and child <fptr>
            # <fptr FILEID="file-<UUID>" LABEL="filename.ext">
            fileId = "file-{}".format(f.uuid)
            label = item if not label else label
            fileDiv = etree.SubElement(
                structMapDiv, ns.metsBNS + "div", LABEL=label, TYPE="Item"
            )
            etree.SubElement(fileDiv, ns.metsBNS + "fptr", FILEID=fileId)
            # Pair items listed in custom structmaps. Strip leading path
            # separator if it exists.
            state.fileNameToFileID[directoryPathSTR] = fileId

            # Determine fileGrp @GROUPID based on the file's fileGrpUse and transfer type
            GROUPID = ""
            if f.filegrpuuid:
                # GROUPID was determined elsewhere
                GROUPID = "Group-%s" % (f.filegrpuuid)
                if use == "TRIM file metadata":
                    use = "metadata"

            elif use in (
                "original",
                "submissionDocumentation",
                "metadata",
                "maildirFile",
            ):
                # These files are in a group defined by themselves
                GROUPID = "Group-%s" % (f.uuid)
                if use == "maildirFile":
                    use = "original"
                # Check for CSV-based Dublincore dmdSec
                if use == "original":
                    pass

            if GROUPID == "":
                state.error_accumulator.error_count += 1
                job.pyprint(
                    'No groupID for file: "', directoryPathSTR, '"', file=sys.stderr
                )

            if use not in state.globalFileGrps:
                job.pyprint('Invalid use: "%s"' % (use), file=sys.stderr)
                state.error_accumulator.error_count += 1
            else:
                file_elem = etree.SubElement(
                    state.globalFileGrps[use],
                    ns.metsBNS + "file",
                    ID=fileId,
                    GROUPID=GROUPID,
                )
                if use == "original":
                    filesInThisDirectory.append(file_elem)

                # E.g. <Flocat xlink:href="objects/file1-UUID" locType="other" otherLocType="system"/>
                #
                # LOCTYPE = Other, because not URI, URN, HANDLE etc.
                # OTHERLOCTYPE = System because it is a 'system' path.
                newChild(
                    file_elem,
                    ns.metsBNS + "FLocat",
                    sets=[
                        (ns.xlinkBNS + "href", directoryPathSTR),
                        ("LOCTYPE", "OTHER"),
                        ("OTHERLOCTYPE", "SYSTEM"),
                    ],
                )

                if includeAmdSec:
                    pass

    if dspaceMetsDMDID is not None:
        for file_elem in filesInThisDirectory:
            file_elem.set("DMDID", dspaceMetsDMDID)

    return structMapDiv


def create_original_style_structmap(job, opts):
    """Create original style structmap

    Below is the really basic original METS code to get us part of the way
    to our tool only output... but it is in dire need of a refactor....

    Let's try not to use this if at all possible.
    """

    state = MetsState()

    baseDirectoryPath = opts.baseDirectoryPath
    baseDirectoryPathString = "%%%s%%" % (opts.baseDirectoryPathString)
    fileGroupIdentifier = opts.fileGroupIdentifier
    fileGroupType = opts.fileGroupType
    includeAmdSec = opts.amdSec

    # Wellcome TODO: this is way to finicky...
    baseDirectoryPath = os.path.join(baseDirectoryPath, "")
    objectsDirectoryPath = os.path.join(baseDirectoryPath, "objects")

    structMap = etree.Element(
        ns.metsBNS + "structMap",
        TYPE="physical",
        ID="structMap_{}".format(state.globalStructMapCounter),
        LABEL="Archivematica default",
    )
    sip_dir_name = os.path.basename(baseDirectoryPath.rstrip("/"))
    structMapDiv = etree.SubElement(
        structMap, ns.metsBNS + "div", TYPE="Directory", LABEL=sip_dir_name
    )

    # Fetch any ``Directory`` objects in the database that are contained within
    # this SIP and return them as a dict from relative paths to UUIDs. (See
    # createSIPfromTransferObjects.py for the association of ``Directory``
    # objects to a ``SIP``.
    directories = {
        d.currentlocation.rstrip("/"): d
        for d in Directory.objects.filter(sip_id=fileGroupIdentifier.encode()).all()
    }

    createFileSec(
        job,
        objectsDirectoryPath,
        structMapDiv,
        baseDirectoryPath,
        baseDirectoryPathString,
        fileGroupIdentifier,
        fileGroupType,
        directories,
        state,
        includeAmdSec=includeAmdSec,
    )

    fileSec = etree.Element(ns.metsBNS + "fileSec")
    for group in state.globalFileGrpsUses:  # state.globalFileGrps.itervalues():
        grp = state.globalFileGrps[group]
        if len(grp) > 0:
            fileSec.append(grp)

    rootNSMap = {"mets": ns.metsNS, "xsi": ns.xsiNS, "xlink": ns.xlinkNS}
    root = etree.Element(
        ns.metsBNS + "mets",
        nsmap=rootNSMap,
        attrib={
            "{"
            + ns.xsiNS
            + "}schemaLocation": "http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/version1121/mets.xsd"
        },
    )
    etree.SubElement(root, ns.metsBNS + "metsHdr").set(
        "CREATEDATE", timezone.now().strftime("%Y-%m-%dT%H:%M:%S")
    )

    root.append(fileSec)
    root.append(structMap)

    print(etree.tostring(root, pretty_print=True))


# =============================================================================
# End of BAD METS...
# =============================================================================

import uuid

import metsrw

from fs_entries_tree import FSEntriesTree

def create_tool_mets(job, opts):
    """hello"""

    # Based entirely on create_transfer_METS from Cole...
    # https://git.io/JJK8a

    baseDirectoryPath = opts.baseDirectoryPath
    baseDirectoryPathString = "%%%s%%" % (opts.baseDirectoryPathString)
    aip_uuid = opts.fileGroupIdentifier
    fileGroupType = opts.fileGroupType
    includeAmdSec = opts.amdSec
    mets_tool_path = "mets/tool_output-{}.xml".format(aip_uuid)

    # Wellcome TODO: this is way too finicky...
    baseDirectoryPath = os.path.join(baseDirectoryPath, "")
    objectsDirectoryPath = os.path.join(baseDirectoryPath, "objects")

    objectsDirectoryPath = baseDirectoryPath

    mets = metsrw.METSDocument()
    mets.objid = str(aip_uuid)

    try:
        transfer = SIP.objects.get(uuid=aip_uuid)
    except Transfer.DoesNotExist:
        logger.info("No record in database for transfer: %s", aip_uuid)
        raise

    fsentry_tree = FSEntriesTree(objectsDirectoryPath, "%SIPDirectory%", transfer)
    fsentry_tree.scan()

    mets.append_file(fsentry_tree.root_node)
    mets.write(mets_tool_path, pretty_print=True)



    '''
    transfer_dir_path = os.path.expanduser(transfer_dir_path)
    transfer_dir_path = os.path.normpath(transfer_dir_path)
    db_base_path = r"%{}%".format(base_path_placeholder)
    mets = metsrw.METSDocument()
    mets.objid = str(transfer_uuid)
    dashboard_uuid = get_dashboard_uuid()
    if dashboard_uuid:
        agent = metsrw.Agent(
            "CREATOR",
            type="SOFTWARE",
            name=str(dashboard_uuid),
            notes=["Archivematica dashboard UUID"],
        )
        mets.agents.append(agent)
    try:
        transfer = Transfer.objects.get(uuid=transfer_uuid)
    except Transfer.DoesNotExist:
        logger.info("No record in database for transfer: %s", transfer_uuid)
        raise
    if transfer.accessionid:
        alt_record_id = metsrw.AltRecordID(transfer.accessionid, type="Accession ID")
        mets.alternate_ids.append(alt_record_id)
    fsentry_tree = FSEntriesTree(transfer_dir_path, db_base_path, transfer)
    fsentry_tree.scan()
    mets.append_file(fsentry_tree.root_node)
    mets.write(mets_path, pretty_print=True)
    '''





def _create_tool_mets(job, opts):
    """Do something..."""

    ORIGINALS = "original"
    PATH_PLACEHOLDER = "%SIPDirectory%"

    fileGroupIdentifier = opts.fileGroupIdentifier

    print("SIP UUID", fileGroupIdentifier)

    # FieldError: Cannot resolve keyword 'grp' into field. Choices are:
    # checksum, checksumtype, currentlocation, derived_file_set,
    # enteredsystem, event, fileformatversion, filegrpuse, filegrpuuid,
    # fileid, fpcommandoutput, identifiers, label, modificationtime,
    # original_file_set, originallocation, removedtime, sip, sip_id,
    # size, transfer, transfer_id, uuid

    # file_ids = FileID.objects.filter(file_id=fileUUID)
    files = File.objects.filter(sip=fileGroupIdentifier, filegrpuse=ORIGINALS)

    for file in files:
        # This data is used for the file sec... but the structmap is a
        # little more yucky...
        print(file.currentlocation.replace(PATH_PLACEHOLDER, ""))

    # 1. Create structmap components first...
    # 2. Create structmap...
    # 3. Create file sec...
    # 4. Output tool data into PREMIS...

    for file in files:
        print(file.uuid)
        documents = FPCommandOutput.objects.filter(
            file_id=file.uuid,
            rule__purpose__in=["characterization", "default_characterization"],
        ).values_list("content")
        for (document,) in documents:
            print(document.encode("utf-8")[39:50])

    # currentlocation, enteredsystem, identifiers, originallocation,
    # sip, sip_id, transfer, transfer_id, uuid
    directories = Directory.objects.filter(sip=fileGroupIdentifier)

    for directory in directories:
        print("NB.", directory.currentlocation.replace(PATH_PLACEHOLDER, ""))

    # For reference...
    # create_original_style_structmap(job, opts)
