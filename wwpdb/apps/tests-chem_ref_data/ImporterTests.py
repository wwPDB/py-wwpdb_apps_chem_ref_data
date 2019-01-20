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

import platform
import os
import unittest


# We cannot import everything due to openeye requirement... Selected from ChemRefDataWebApp
try:
    import openeye.oechem
    fullimport = True
except ImportError:
    fullimport = False

if fullimport:
    import wwpdb.apps.chem_ref_data.webapp.ChemRefDataWebApp
else:
    from wwpdb.utils.session.WebRequest import InputRequest, ResponseContent
    from wwpdb.apps.chem_ref_data.report.ChemRefReportDepictBootstrap import ChemRefReportDepictBootstrap
    from wwpdb.apps.chem_ref_data.search.ChemRefSearchDepictBootstrap import ChemRefSearchDepictBootstrap
    from wwpdb.apps.chem_ref_data.utils.ChemRefDataCvsUtils import ChemRefDataCvsUtils
    from wwpdb.apps.chem_ref_data.utils.ChemRefDataDbUtils import ChemRefDataDbUtils
    from wwpdb.apps.chem_ref_data.utils.ChemRefPathInfo import ChemRefPathInfo
    from wwpdb.apps.chem_ref_data.utils.DownloadUtils import DownloadUtils
    from wwpdb.apps.chem_ref_data.utils.ChemRefDataMiscUtils import ChemRefDataMiscUtils
    from mmcif_utils.style.PrdCategoryStyle import PrdCategoryStyle
    from mmcif_utils.style.ChemCompCategoryStyle import ChemCompCategoryStyle
    from wwpdb.utils.config.ConfigInfo import ConfigInfo
    from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility

class ImportTests(unittest.TestCase):
    def setUp(self):
        pass

    def testInstantiate(self):
        """Tests simple instantiation"""
        pass
