##
# File: ImportTests.py
# Date:  06-Oct-2018  E. Peisach
#
# Updates:
##
"""Test import for chem_ref_data"""

__docformat__ = "restructuredtext en"
__author__ = "Ezra Peisach"
__email__ = "peisach@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import unittest
import sys

# We cannot import everything due to openeye requirement... Selected from ChemRefDataWebApp
try:
    import openeye.oechem  # noqa: F401 pylint: disable=unused-import

    fullimport = True
except ImportError:
    fullimport = False

if fullimport:
    import wwpdb.apps.chem_ref_data.webapp.ChemRefDataWebApp  # noqa: F401 pylint: disable=unused-import
else:
    from wwpdb.utils.session.WebRequest import InputRequest, ResponseContent  # noqa: F401 pylint: disable=unused-import
    from wwpdb.apps.chem_ref_data.report.ChemRefReportDepictBootstrap import ChemRefReportDepictBootstrap  # noqa: F401 pylint: disable=unused-import
    from wwpdb.apps.chem_ref_data.search.ChemRefSearchDepictBootstrap import ChemRefSearchDepictBootstrap  # noqa: F401 pylint: disable=unused-import
    from wwpdb.apps.chem_ref_data.utils.ChemRefDataCvsUtils import ChemRefDataCvsUtils  # noqa: F401 pylint: disable=unused-import
    from wwpdb.apps.chem_ref_data.utils.ChemRefDataDbUtils import ChemRefDataDbUtils  # noqa: F401 pylint: disable=unused-import
    from wwpdb.apps.chem_ref_data.utils.DownloadUtils import DownloadUtils  # noqa: F401 pylint: disable=unused-import
    from wwpdb.apps.chem_ref_data.utils.ChemRefDataMiscUtils import ChemRefDataMiscUtils  # noqa: F401 pylint: disable=unused-import


class ImportTests(unittest.TestCase):
    def setUp(self):
        pass

    def testInstantiate(self):
        """Tests simple instantiation"""
        sys.stderr.write("Full import is %s\n" % fullimport)


if __name__ == "__main__":
    unittest.main()
