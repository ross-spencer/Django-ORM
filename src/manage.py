# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(THIS_DIR))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    print("")
