# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import argparse
from contextlib import contextmanager
import os
import sys
import traceback

import django
from six.moves import input

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(THIS_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

django.setup()

from main.models import SIP

sys.dont_write_bytecode = True


class Jobs(object):
    """Jobs mocks the Archivematica Jobs class. TODO: Might need some more work
    to grab extra data from the METS script. Plus we need an idiomatic way to
    output script generated log lines so we need to work on that here too.
    """

    def __init__(self, name, uuid, args, caller_wants_output=False):
        self.args = [name] + args
        self.int_code = 0
        self.status_code = ""
        self.output = ""
        self.error = ""

    def set_status(self, int_code, status_code=""):
        if int_code:
            self.int_code = int(int_code)
        self.status_code = status_code

    def write_output(self, s):
        self.output += s

    def write_error(self, s):
        self.error += s

    def print_error(self, *args):
        self.write_error(" ".join([self._to_str(x) for x in args]) + "\n")

    def pyprint(self, *objects, **kwargs):
        file = kwargs.get("file", sys.stdout)
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        msg = sep.join([self._to_str(x) for x in objects]) + end
        if file == sys.stdout:
            self.write_output(msg)
        elif file == sys.stderr:
            self.write_error(msg)
        else:
            raise Exception("Unrecognized print file: " + str(file))

    @staticmethod
    def _to_str(thing):
        try:
            return str(thing)
        except UnicodeEncodeError:
            return thing.encode("utf8")

    @contextmanager
    def JobContext(self, logger=None):
        try:
            yield
        except Exception as e:
            self.write_error(str(e))
            self.write_error(traceback.format_exc())
            self.set_status(1)


class AIP:
    """AIP just provides a structured way to handle some of the data below
    without relying on the model.
    """

    def __init__(self):
        self.uuid = ""
        self.name = ""

    def __str__(self):
        return "{}, {}".format(self.name, self.uuid)


def mets_runner(create_aip_mets):
    """mets_runner is our runner and will generate METS files based on the
    input provided here.
    """
    aips = []
    for sip in SIP.objects.all():
        aip = AIP()
        aip.uuid = sip.uuid
        aip.name = sip.aip_filename.strip(".7z")
        aips.append(aip)
    print("# Select an AIP to create METS for:")
    for idx, aip in enumerate(aips, 1):
        print("{}:".format(idx), aip.name)
    try:
        choice = input()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, exiting...")
        sys.exit(0)
    try:
        print("Selected:", aips[int(choice) - 1].name)
    except IndexError:
        print("Invalid choice:", choice)
    choice_uuid = aips[int(choice) - 1].uuid
    folder = os.path.join("aips", aips[int(choice) - 1].name)
    output_mets_file = "mets/METS.{}.xml".format(choice_uuid)
    args_example = [
        "--amdSec",
        "--baseDirectoryPath",
        folder,
        "--baseDirectoryPathString",
        "SIPDirectory",
        "--fileGroupIdentifier",
        choice_uuid,
        "--fileGroupType",
        "sip_id",
        "--xmlFile",
        output_mets_file,
        "--sipType",
        "SIP",
    ]

    job = Jobs(name="create_mets", uuid="12345", args=args_example)
    jobs = [job]

    print("Creating AIP METS from harness")
    create_aip_mets.call(jobs)
    print("# Pyprint output:")
    print(job.output.strip())
    print("Status code ({}): {}".format(job.int_code, job.status_code))
    if job.status_code != 0:
        print("Error", job.error, file=sys.stderr)
    print("If success then METS should be partially or completely at:", output_mets_file)
    # We could have a toggle in here if we really wanted....
    tool_mets_file = "mets/tool_output-{}.xml".format(choice_uuid)
    print("                                 (Optionally) Tool output:", tool_mets_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", action="store_true")
    parser.add_argument("--reduced", action="store_true")
    parser.add_argument("--reduced_extra", action="store_true")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        args.original = True
    if len(sys.argv) > 2:
        sys.exit("One argument only please...")
    if len(sys.argv) > 1:
        pass
    if args.original:
        print("Running against the original METS creation script...")
        import create_aip_mets
    if args.reduced:
        print("Running against the reduced METS creation script...")
        import v1_create_aip_mets as create_aip_mets
    if args.reduced_extra:
        print("Running against the reduced METS creation script...")
        import v2_create_aip_mets as create_aip_mets
    mets_runner(create_aip_mets)


if __name__ == "__main__":
    main()
