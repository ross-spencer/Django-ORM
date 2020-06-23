NOTES ON CREATE METS V2
=======================

* If no DC in the database, it is loaded from the transfer file (it doesn't
  appear in the transfer METS).

* METS summary:

	* mets Header (optional)
	* descriptive metadata (optional)
	* administrative metadata section (optional)
	* file section (optional but typical)
	* structural map section (required)
	* structural link section (optional)
	* behavior section (optional)

* Tests

	* Running `tox` from the root directory should work.

* AM test suite expected failures, e.g. `...x..`:

    @unittest.expectedFailure
    def test_create_dc_dmdsec_no_dc_transfer_dc_xml(self):
        # FIXME What is the expected behaviour of this? What should the fixture have?
        # transfers_sip = os.path.join(THIS_DIR, 'fixtures', 'transfer_dc')
        raise NotImplementedError()

	commit 6e1625710ac1674f13663be474f32fd8e026c4ae
	Author: Holly Becker <hbecker@artefactual.com>
	Date:   Thu May 28 16:27:12 2015 -0700

	    createMETS2: Fix no transfer DC bug

	    Add tests for DC dmdSec.

# Observations

Model has foreign keys with the FPR APP (I'm 90% sure this isn't needed and
also impacts what we might do in future with PAR like functions)

* main.FPCommandOutput.rule: (fields.E300) Field defines a relation with model
'fpr.FPRule', which is either not installed, or is abstract.

* main.FPCommandOutput.rule: (fields.E307) The field main.FPCommandOutput.rule
was declared with a lazy reference to 'fpr.fprule', but app 'fpr' isn't
installed.

* main.FileFormatVersion.format_version: (fields.E300) Field defines a relation
with model 'fpr.FormatVersion', which is either not installed, or is abstract.

* main.FileFormatVersion.format_version: (fields.E307) The field
main.FileFormatVersion.format_version was declared with a lazy reference to
'fpr.formatversion', but app 'fpr' isn't installed.

* metadata folder seems to only need to exist for the filesec? Is that correct?
It seems like that might be an error if that's the case.

* # Delete empty directories, see #8427 -- is a strange artefact of the script
and has the potential to modify the file-system structure. Try and understand
why it exists.
