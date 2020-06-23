METS-harness
============

METS-harness is a prototype development environment for rapidly iterating
changes to the standard Archivematica METS file, large or small.

METS-harness provides access to the database component of Django and therefore
Archivematica without the rest of Django behind it.

The main benefits to METS-harness are as follows:

* Re-create a METS file from an Archivematica transfer without having to re-run
the transfer.

* Develop core Archivematica functionality without requiring a full
Archivematica setup.

* Easily output METS using different versions of the METS generation script and
compare the two outputs side-by-side.

* Support modeling and creation of testing of new METS structures.

Python 3 support
----------------

This work is largely compatible with Python 3 but Django had to be downgraded
to 1.11 to support Archivematica.

Quick Setup
-----------

1. Create a virtual environment: `python -m virtualenv venv`
2. Activate the virtual environment: `source venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Run it! `python -m src.mets_runner`

License
-------

GNU AFFERO GENERAL PUBLIC LICENSE Version 3: [Details](LICENSE)

Original License
----------------

_The original entry-point for this work was taken from the [Django-ORM][dj-1]
project by Dan Caron, Abu Ashraf Masnun, wsqy._

_It has largely been reshaped now with the models, scripts, and other Django
settings imported from the [Archivematica project][am-1]. The original license
is recorded below in keeping with its spirit._

_Please check-out the original project and support it given the opportunity and
need as it does provide a nice template to work from._

[dj-1]: https://github.com/dancaron/Django-ORM
[am-1]: https://github.com/artefactual/archivematica

The MIT License (MIT) Copyright (c) 2016 Dan Caron

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
