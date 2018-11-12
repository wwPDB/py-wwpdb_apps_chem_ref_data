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


import sys
import unittest
import traceback
import sys
import time
import os
import os.path
import shutil


from pdbx_v2.chemcomp.PdbxChemCompIo import PdbxChemCompIo

from wwpdb.utils.rcsb.WebRequest import InputRequest
from wwpdb.api.facade.ConfigInfo import ConfigInfo, getSiteId
from wwpdb.apps.chem_ref_data.utils.ChemRefDataMiscUtils import ChemRefDataMiscUtils


class ChemRefDataMiscUtilsTests(unittest.TestCase):

    def setUp(self):
        self.__lfh = sys.stderr
        self.__verbose = True
        # Pick up site information from the environment or failover to the development site id.
        self.__siteId = getSiteId(defaultSiteId='WWPDB_DEPLOY_TEST_RU')
        self.__lfh.write("\nTesting with site environment for:  %s\n" % self.__siteId)
        self.__cI = ConfigInfo(self.__siteId)
        self.__topPath = self.__cI.get('SITE_WEB_APPS_TOP_PATH')
        self.__topSessionPath = self.__cI.get('SITE_WEB_APPS_TOP_SESSIONS_PATH')
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
        """Test case -  get chemical component definition file path list (serial)
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        try:
            mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            pathList = mu.getChemCompPathList()
            self.__lfh.write("Length of path list %d\n" % len(pathList))

        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()

    def testGetCompPathListMulti(self):
        """Test case -  get chemical component definition file path list (multiprocess)
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        try:
            mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            pathList = mu.getChemCompPathListMulti(numProc=4)
            self.__lfh.write("Length of path list %d\n" % len(pathList))

        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()

    def testUpdateChemRefDataFiles(self):
        """Test case -  create chemical component definition file idList, pathList, and concatenated dictionary.
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        ok = False
        try:
            mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            ok = mu.updateChemCompSupportFiles()
        except:
            traceback.print_exc(file=self.__lfh)
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


if __name__ == '__main__':
    #
    if (True):
        mySuite = suitePathList()
        unittest.TextTestRunner(verbosity=2).run(mySuite)

        mySuite = suiteUpdateReferenceFiles()
        unittest.TextTestRunner(verbosity=2).run(mySuite)
