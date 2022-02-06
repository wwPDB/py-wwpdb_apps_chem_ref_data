##
#
# File:    ChemRefDataMiscUtilsTests.py
# Author:  jdw
# Date:    16-Mar-2016
# Version: 0.001
#
# Updates:
##
"""
A collection of tests for the ChemRefDataMiscUtils and related classes.   Requires access to
checked out CVS repository of chemical components.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


import unittest
import sys
import logging
import os

if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from commonsetup import HERE  # noqa:  F401 pylint: disable=import-error,unused-import
else:
    from .commonsetup import HERE  # noqa: F401 pylint: disable=relative-beyond-top-level

from wwpdb.utils.session.WebRequest import InputRequest
from wwpdb.utils.config.ConfigInfo import ConfigInfo, getSiteId
from wwpdb.apps.chem_ref_data.utils.ChemRefDataMiscUtils import ChemRefDataMiscUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# @unittest.skipUnless(Features().haveCCD(), "Need full CCD for tests")
class ChemRefDataMiscUtilsTests(unittest.TestCase):
    def setUp(self):
        self.__lfh = sys.stderr
        self.__verbose = True
        # Pick up site information from the environment or failover to the development site id.
        self.__siteId = getSiteId(defaultSiteId="WWPDB_DEPLOY_TEST_RU")
        logger.info("Testing with site environment for:  %s", self.__siteId)
        self.__cI = ConfigInfo(self.__siteId)
        self.__topPath = self.__cI.get("SITE_WEB_APPS_TOP_PATH")
        self.__topSessionPath = self.__cI.get("SITE_WEB_APPS_TOP_SESSIONS_PATH")
        #
        # Create a request object and session directories for test cases
        #
        self.__reqObj = InputRequest(paramDict={}, verbose=self.__verbose, log=self.__lfh)
        self.__reqObj.setValue("WWPDB_SITE_ID", self.__siteId)
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("TopPath", self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        #

    def tearDown(self):
        pass

    def testGetCompPathList(self):
        """Test case -  get chemical component definition file path list (serial)"""
        logger.info("Starting")
        try:
            mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            pathList = mu.getChemCompPathList()
            logger.info("Length of path list %d", len(pathList))

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In test")
            self.fail()

    def testGetCompPathListMulti(self):
        """Test case -  get chemical component definition file path list (multiprocess)"""
        logger.info("Starting")
        try:
            mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            pathList = mu.getChemCompPathListMulti(numProc=4)
            logger.info("Length of path list %d", len(pathList))

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In testGetCompPathListMulti")
            self.fail()

    def testUpdateChemRefDataFiles(self):
        """Test case -  create chemical component definition file idList, pathList, and concatenated dictionary."""
        logger.info("Starting")
        ok = False
        try:
            mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            ok = mu.updateChemCompSupportFiles(skipIndex=True)  # Do not generate sdb or index file
            self.assertTrue(ok)
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In testUpdateChemRefDataFiles")
            self.fail()


def suitePathList():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ChemRefDataMiscUtilsTests("testGetCompPathList"))
    suiteSelect.addTest(ChemRefDataMiscUtilsTests("testGetCompPathListMulti"))
    return suiteSelect


def suiteUpdateReferenceFiles():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ChemRefDataMiscUtilsTests("testUpdateChemRefDataFiles"))
    return suiteSelect


if __name__ == "__main__":
    #
    if True:  # pylint: disable=using-constant-test
        mySuite = suitePathList()
        unittest.TextTestRunner(verbosity=2).run(mySuite)

        mySuite = suiteUpdateReferenceFiles()
        unittest.TextTestRunner(verbosity=2).run(mySuite)
