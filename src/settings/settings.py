import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.dirname(os.path.dirname(BASE_DIR))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(DB_DIR, "db", "db.sqlite3"),
    },
}

"""TODO this should be in our databases registry but tests are trying to pick
it up incorrectly.

    "am": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "MCP",
        "USER": "root",
        "PASSWORD": "12345",
        "HOST": "127.0.0.1",
        "PORT": "62001",
    },
"""

# TODO: This should silence the system check we don't need for the SQL database
# as we only ever read from it.
SILENCED_SYSTEM_CHECKS = ["django_mysql.W002"]

INSTALLED_APPS = ("main", "fpr", "django.contrib.contenttypes", "django.contrib.auth")

# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = "6few3nci_q_o@l1dlbk81%wcxe!*6r29yu629&d97!hiqat9fa"

# Required for Pytest to work.
USE_TZ = True
