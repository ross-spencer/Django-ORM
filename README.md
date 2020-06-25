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
4. The database migrations have already been run, so just load the fixtures:
    `python -m src.manage loaddata fixtures/fixtures.json.zip`
5. Run it! `python -m src.mets_runner`

Running with non-default data
-----------------------------

**Warning:** _One of the reasons I don't recommend this at present is that the
runner needs AIP structures that match those of the Archivematica transfers
you've processed. The AIPs folder is both where those are stored, and where
METS files will be processed from. This matches the Archivematica process 1:1
for now. To make life easier I've included a METS greatest hits._

* ✔️ Demo transfer CSV.
* ✔️ Deep transfer.
* ✔️ Zipped bag transfer.
* ✔️ Deep zipped transfer.
* ✔️ METS structmap example.
* ✔️ Delete packages (delete after).
* ✔️ Delete packages (don't delete)._

If you still want to update or refresh the data, e.g. for greater simplicity or
complexity:

1. Delete or backup the existing db somewhere else: `rm db/db.sqlite3`
2. Dump a set of transfers from Archivematica:
	```bash
	python -m src.manage dumpdata --database=am \
		--exclude contenttypes \
		--exclude auth.permission \
		| python -m json.tool > fixtures/fixtures.json
	```
3. Load the fixtures (the harness database is set as the default so it does not
need to be specified here):
	`python -m src.manage loaddata fixtures/fixtures.json`
4. Organize your AIP layout in the aips folder. The structure should be a) a
folder matching the name of the AIP in Archivematica. b) the objects directory.
c) a metadata directory (this can apparently be blank, its use is to be
determined). Example for the demo transfer, nb. its 'bag' structure is the
primary part that has been removed.
```
demo_transfer_csv-15e219c3-0f51-4d32-80f4-577edfeceb05/
├── metadata
└── objects
    ├── artwork
    │   ├── MARBLES.TGA
    │   └── Montreal.png
    ├── beihai.tif
    ├── bird.mp3
    ├── metadata
    │   └── transfers
    │       └── demo_transfer_csv-3d81bc07-1962-4286-a85d-a9942b1a1991
    │           ├── checksum.md5
    │           ├── checksum.sha1
    │           ├── checksum.sha256
    │           ├── checksum.sha512
    │           ├── directory_tree.txt
    │           ├── identifiers.json
    │           ├── metadata.csv
    │           └── rights.csv
    ├── ocr-image.png
    ├── piiTestDataCreditCardNumbers.txt
    ├── submissionDocumentation
    │   └── transfer-demo_transfer_csv-3d81bc07-1962-4286-a85d-a9942b1a1991
    │       ├── Agreement-Gift-MBRS-project.pdf
    │       └── METS.xml
    └── View_from_lookout_over_Queenstown_towards_the_Remarkables_in_spring.jpg
```

Comparing two METS
------------------

There are a series of original-METS included in this repository. You might
elect to recreate a METS with checksum: `15e219c3-0f51-4d32-80f4-577edfeceb05`.

When you run the harness to do this it will be output into the `mets/` folder.

Compare it using `git diff` as follows;
```
git diff --no-index mets/METS.15e219c3-0f51-4d32-80f4-577edfeceb05.xml \
 original-mets/METS.15e219c3-0f51-4d32-80f4-577edfeceb05.xml
```

_**TODO:** More sophisticated mechanisms will be conjured as appropriate. For
example, programatically replacing the date values in the new and original METS
files with something generic so that they do not present as differences when
compared._

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
