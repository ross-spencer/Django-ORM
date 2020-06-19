import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


"""
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.mysql',
        "NAME": "MCP",
        "USER": "root",
        "PASSWORD": "12345",
        "HOST": "127.0.0.1",
        "PORT": "62001",
    }
}
"""


DATABASES = {
    "default": {
        # Database driver
        "ENGINE": "django.db.backends.sqlite3",
        # Replace below with Database Name if using other database engines
        "NAME": os.path.join(BASE_DIR, "..", "db", "db.sqlite3"),
    }
}



"""
INSTALLED_APPS = (
    "main",
    #"django.contrib.contenttypes",
    #"django.contrib.auth",
    "fpr",
)
"""

INSTALLED_APPS = (
    "main",
    "fpr",
    "django.contrib.contenttypes",
    "django.contrib.auth",
)

# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = "6few3nci_q_o@l1dlbk81%wcxe!*6r29yu629&d97!hiqat9fa"

# Required for Pytest to work.
USE_TZ = True
