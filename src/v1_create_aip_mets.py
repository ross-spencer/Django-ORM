# -*- coding: utf-8 -*-

from v1_create_aip_mets_reduced import create_mets

import traceback

import logging


def call(jobs):

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("--sipType", action="store", dest="sip_type", default="SIP")
    parser.add_option(
        "-s",
        "--baseDirectoryPath",
        action="store",
        dest="baseDirectoryPath",
        default="",
    )
    # transferDirectory/
    parser.add_option(
        "-b",
        "--baseDirectoryPathString",
        action="store",
        dest="baseDirectoryPathString",
        default="SIPDirectory",
    )
    # transferUUID/sipUUID
    parser.add_option(
        "-f",
        "--fileGroupIdentifier",
        action="store",
        dest="fileGroupIdentifier",
        default="",
    )
    parser.add_option(
        "-t", "--fileGroupType", action="store", dest="fileGroupType", default="sipUUID"
    )
    parser.add_option("-x", "--xmlFile", action="store", dest="xmlFile", default="")
    parser.add_option(
        "-a", "--amdSec", action="store_true", dest="amdSec", default=False
    )
    parser.add_option(
        "-n",
        "--createNormativeStructmap",
        action="store_true",
        dest="createNormativeStructmap",
        default=False,
    )

    for job in jobs:
        with job.JobContext(logger=logging):
            try:
                opts, _ = parser.parse_args(job.args[1:])
                create_mets(job, opts)
            except Exception as err:
                job.print_error(repr(err))
                job.print_error(traceback.format_exc())
                job.set_status(1, status_code="failure")
